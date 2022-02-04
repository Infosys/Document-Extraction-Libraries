# ===============================================================================================================#
#
# Copyright 2021 Infosys Ltd.
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at
# http://www.apache.org/licenses/
#
# ===============================================================================================================#

import concurrent.futures
import copy
import json
import logging
import os
import time
import ast
import traceback
import urllib3
from urllib.parse import urlencode
from infy_ocr_generator.interface.data_service_provider_interface import (
    SUB_RE_API_STRUCTURE, GENERATE_API_RES_STRUCTURE, DataServiceProviderInterface, DOC_DATA)

CONFIG_PARAMS_DICT = {
    'azure': {
        'computer_vision': {
            'subscription_key': '',
            'api_read': {
                'url': '',
                'query_params': {
                    'language': '',
                    'readingOrder': 'basic',
                    'model-version': 'latest'
                }
            }
        }
    }
}


class AzureReadOcrDataServiceProvider(DataServiceProviderInterface):
    """Implementation of DataServiceProvider for AZURE-Read API"""

    def __init__(self, config_params_dict: CONFIG_PARAMS_DICT,
                 output_dir: str = None,
                 output_to_supporting_folder: bool = False,
                 overwrite: bool = False,
                 logger: logging.Logger = None,
                 log_level: int = None):
        """Creates an instance of Azure Read Ocr Data Service Provider

        Args:
            config_params_dict (CONFIG_PARAMS_DICT): Provider CONFIG values
            output_dir (str, optional): Directory to generate OCR file,
                if not given will generate into same file location. Defaults to None.
            output_to_supporting_folder (bool, optional): If True, OCR file will be generated to
                same file location but into supporting folder named `* _files`. Defaults to False.
            overwrite (bool, optional): If True, existing OCR file will be overwritten. Defaults to False.
            logger (logging.Logger, optional): logger object. Defaults to None.
            log_level (int, optional): log level. Defaults to None.

        Raises:
            FileNotFoundError: Raises an error if file not found.
        """
        super(AzureReadOcrDataServiceProvider,
              self).__init__(logger, log_level)
        self.config_params_dict = self.get_updated_config_dict(
            config_params_dict['azure'], CONFIG_PARAMS_DICT['azure'])
        self.config_params_dict = copy.deepcopy(
            self.config_params_dict['computer_vision'])
        if output_dir and not os.path.exists(output_dir):
            raise FileNotFoundError(f"{output_dir} not found")
        self.output_dir = output_dir

        self.output_to_supporting_folder = output_to_supporting_folder
        self.overwrite = overwrite

    def submit_request(self, doc_data_list: [DOC_DATA]):
        """API to submit Azure read ocr data serivce request for asynchorouns call

        Args:
            doc_data_list ([DOC_DATA]): List of input documents. e.g, ['c:/1.jpg','c:/1.pdf']
        """
        def _call_azure_read_post_api(in_doc_obj) -> dict:
            response_dict = copy.deepcopy(SUB_RE_API_STRUCTURE)
            input_doc_data = None
            api_query_param = self.config_params_dict['api_read']['query_params']
            api_query_param['pages'] = in_doc_obj['pages']
            api_query_param = {k: v for k, v in api_query_param.items() if v}
            in_doc = in_doc_obj['doc_path']
            response_dict['input_doc'] = in_doc
            response_dict['submit_api']['query_params'] = api_query_param
            api_url = self.config_params_dict['api_read']['url']
            sub_key = self.config_params_dict['subscription_key']

            output_doc = self.get_output_file(
                in_doc, self.output_dir, self.output_to_supporting_folder,
                pages=api_query_param.get('pages'), suffix='_azure_read.json')

            if not self.overwrite and os.path.exists(output_doc):
                # file already exists
                response_dict['submit_api']['response']['status_code'] = 409
                return response_dict
            try:
                with open(in_doc, "rb") as reader:
                    input_doc_data = reader.read()
                headers = {'Ocp-Apim-Subscription-Key': sub_key,
                           'Content-Type': 'application/octet-stream'}
                self.set_api_log(api_url)
                http = urllib3.PoolManager()
                api_url = f'{api_url}?{urlencode(api_query_param)}'
                response = http.request(
                    "post", api_url,
                    body=input_doc_data,
                    headers=headers)
                response_dict['submit_api']['response'] = {
                    'status_code': response.status,
                    'error': response.reason,
                    'operation_location': response.headers.get('Operation-Location', None),
                    'apim_request_id': response.headers.get('apim-request-id', None)}
            except Exception as e:
                response_dict["error"] = e.args[0]
                full_trace_error = traceback.format_exc()
                self.logger.error(full_trace_error)
            return response_dict

        if len(doc_data_list) == 0:
            raise Exception("Valid doc_data_list arg is required.")
        start_time = time.time()
        response_list = []
        with concurrent.futures.ThreadPoolExecutor(
                max_workers=min(5, len(doc_data_list)),
                thread_name_prefix="th_azure_read_submit") as executor:
            thread_pool_dict = {
                executor.submit(
                    _call_azure_read_post_api,
                    in_doc_obj
                ): in_doc_obj for in_doc_obj in doc_data_list
            }
            for future in concurrent.futures.as_completed(thread_pool_dict):
                response_list.append(future.result())
        self.logger.info(
            f"Total time taken for #{len(doc_data_list)} docs is {round((time.time() - start_time)/60,2)} mins")
        return response_list

    def receive_response(self, submit_req_response_list, rerun_unsucceeded_mode=False):
        """API to Azure_read_ocr_data_service Received response of asynchorouns call submit request.

        Args:
            submit_req_response_list ([SUB_RE_API_STRUCTURE]): Response structure of `submit_request` api
            rerun_unsucceeded_mode (bool, optional): Enabling this mode and passing same request
             -will rerun for unsuccessful call. Defaults to False.
        """
        def _call_azure_read_get_api(sub_req_res) -> dict:
            try:
                response_dict = sub_req_res
                if int(response_dict['submit_api']['response'].get('status_code', -1)) != 202:
                    return response_dict
                # when rerun_unsucceeded_mode true, run for only unsuccessful call
                if rerun_unsucceeded_mode and response_dict["receive_api"]["response"].get("status", "") == "succeeded":
                    return response_dict

                pages = response_dict['submit_api'].get(
                    'query_params', {}).get('pages', '1')
                output_doc = self.get_output_file(
                    response_dict['input_doc'], self.output_dir, self.output_to_supporting_folder,
                    pages=pages, suffix='_azure_read.json')
                if not self.overwrite and os.path.exists(output_doc):
                    # file already exists
                    response_dict['submit_api']['response']['status_code'] = 409
                    return response_dict
                headers = {
                    'Ocp-Apim-Subscription-Key': self.config_params_dict['subscription_key']}
                api_url = sub_req_res['submit_api']['response']['operation_location']

                self.set_api_log(api_url)
                http = urllib3.PoolManager()
                response = http.request(
                    "get",
                    api_url,
                    headers=headers
                )
                response_dict["receive_api"]["response"] = ast.literal_eval(
                    response.data.decode('utf-8'))
            except Exception as e:
                response_dict['error'] = e.args[0]
                full_trace_error = traceback.format_exc()
                self.logger.error(full_trace_error)
            return response_dict

        if len(submit_req_response_list) == 0:
            raise Exception("Valid submit_req_response_list arg is required.")
        start_time = time.time()
        response_list = []
        with concurrent.futures.ThreadPoolExecutor(
                max_workers=min(5, len(submit_req_response_list)),
                thread_name_prefix="th_azure_read_receive") as executor:
            thread_pool_dict = {
                executor.submit(
                    _call_azure_read_get_api,
                    sub_req_res
                ): sub_req_res for sub_req_res in submit_req_response_list
            }
            for future in concurrent.futures.as_completed(thread_pool_dict):
                response_list.append(future.result())
        self.logger.info(f"Total time taken for #{len(submit_req_response_list)}"
                         f" pages is {round((time.time() - start_time)/60,2)} mins")
        return response_list

    def generate(self, doc_data_list: [DOC_DATA] = None, api_response_list: list = None) -> list:
        """API to generate OCR based on OCR provider given

        Args:
            doc_data_list ([DOC_DATA], optional): Use these input files to
                -implement technique and generate output files. Defaults to None.
            api_response_list (list, optional): API response will be generated into output file. Defaults to None.

        Raises:
            Exception: Valid api_response_list param is required

        Returns:
            list: List of generated ocr file path.
        """
        ocr_list = []
        if not api_response_list:
            raise Exception("Valid api_response_list param is required")
        for api_res in api_response_list:
            gen_res_dict = copy.deepcopy(GENERATE_API_RES_STRUCTURE)
            gen_res_dict['input_doc'] = api_res['input_doc']
            try:
                # code 409 updated in code while making submit request
                # for the already existing file
                sub_api_res = int(api_res.get('submit_api', {}).get(
                    'response', {}).get('status_code', -1))
                file_already_exist = (sub_api_res == 409)

                ocr_json_data = api_res.get(
                    'receive_api', {}).get('response', {})
                # Skip the final json generation for the Receive response failured files
                if not file_already_exist and ocr_json_data.get("status", "") != "succeeded":
                    gen_res_dict[
                        'error'] = (f"Submit API status code is `{sub_api_res}`;"
                                    f" Receive API status is `{ocr_json_data.get('status')}`;")
                    continue

                pages = api_res['submit_api'].get(
                    'query_params', {}).get('pages', '1')
                output_doc = self.get_output_file(
                    api_res['input_doc'], self.output_dir, self.output_to_supporting_folder,
                    pages=pages, suffix='_azure_read.json')

                gen_res_dict['output_doc'] = output_doc
                # Overwrite check
                if not self.overwrite and os.path.exists(output_doc):
                    ocr_list.append(gen_res_dict)
                    continue
                if not gen_res_dict['input_doc'].lower().endswith('.pdf'):
                    # only to the image
                    infy_ocr_generator_metadata = self.get_image_details(
                        gen_res_dict['input_doc'])
                    infy_ocr_generator_metadata['doc_page_num'] = pages
                    ocr_json_data['analyzeResult']['infy_ocr_generator_metadata'] = infy_ocr_generator_metadata
                with open(output_doc, 'w', encoding='utf-8') as f:
                    json.dump(ocr_json_data['analyzeResult'],
                              f, ensure_ascii=False, indent=4)
                ocr_list.append(gen_res_dict)
            except Exception as e:
                gen_res_dict['error'] += e.args[0]
                full_trace_error = traceback.format_exc()
                self.logger.error(full_trace_error)
        return ocr_list

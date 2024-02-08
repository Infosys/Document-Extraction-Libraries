# ===============================================================================================================#
#
# Copyright 2021 Infosys Ltd.
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at
# http://www.apache.org/licenses/
#
# ===============================================================================================================#

import concurrent.futures
import json
import os
import time
import traceback
import copy
import logging
import ast
from urllib.parse import urlencode
import urllib3
from infy_ocr_generator.interface.data_service_provider_interface import (
    GENERATE_API_RES_STRUCTURE, DataServiceProviderInterface, DOC_DATA)

CONFIG_PARAMS_DICT = {
    'azure': {
        'computer_vision': {
            'subscription_key': '',
            'api_ocr': {
                'url': '',
                'query_params': {
                    'language': '',
                    'model-version': 'latest',
                    'detectOrientation': 'true'
                }
            }
        }
    }
}


class AzureOcrDataServiceProvider(DataServiceProviderInterface):
    """
    Implementation of DataServiceProvider for AZURE-OCR API

    Environment variables:
    OCR_GEN_HTTP_PROXY_URL (Optional): To set http proxy url
    OCR_GEN_HTTP_PROXY_AUTH (Optional): To set http proxy authentication.
        Format is `user:password` encoded as base64
    """

    def __init__(self, config_params_dict: CONFIG_PARAMS_DICT,
                 output_dir: str = None,
                 output_to_supporting_folder: bool = False,
                 overwrite: bool = False,
                 logger: logging.Logger = None,
                 log_level: int = None):
        """Creates an instance of Azure Ocr Data Service Provider.

        Args:
            config_params_dict (CONFIG_PARAMS_DICT): Provider CONFIG values.
            output_dir (str, optional): Directory to generate OCR file,
                if not given will generate into same file location. Defaults to None.
            output_to_supporting_folder (bool, optional): If True, OCR file will be generated to
                same file location but into supporting folder named `* _files`. Defaults to False.
            overwrite (bool, optional): If True, existing OCR file will be overwritten.Defaults to False.
            logger (logging.Logger, optional): logger object. Defaults to None.
            log_level (int, optional): log level. Defaults to None.

        Raises:
            FileNotFoundError: Raises an error if file is not found.
        """
        super(AzureOcrDataServiceProvider, self).__init__(logger, log_level)
        self.config_params_dict = self.get_updated_config_dict(
            config_params_dict['azure'], CONFIG_PARAMS_DICT['azure'])
        self.config_params_dict = copy.deepcopy(
            self.config_params_dict['computer_vision'])
        if output_dir and not os.path.exists(output_dir):
            raise FileNotFoundError(f"{output_dir} not found")
        self.output_dir = output_dir
        self.output_to_supporting_folder = output_to_supporting_folder
        self.overwrite = overwrite

    def submit_request(self, doc_data_list: [DOC_DATA]) -> list:
        """API to submit request of azure ocr data service for asynchorouns call

        Args:
            doc_data_list ([DOC_DATA]): List of input documents. e.g, ['c:/1.jpg','c:/1.pdf']

        Raises:
            NotImplementedError:Raises an error if the method is not implemented

        Returns:
            list: [SUB_RE_API_STRUCTURE]
        """
        raise NotImplementedError

    def receive_response(self, submit_req_response_list: list, rerun_unsucceeded_mode: bool = False) -> list:
        """API to Received azure ocr data service response of asynchorouns call submit request.

        Args:
            submit_req_response_list (list): Response structure of `submit_request` api.
            rerun_unsucceeded_mode (bool, optional): Enabling this mode and passing same request
             -will rerun for unsuccessful call.Defaults to False.

        Raises:
            NotImplementedError: Raises an error if the method is not implemented

        Returns:
            list: [SUB_RE_API_STRUCTURE]
        """

        raise NotImplementedError

    def generate(self, doc_data_list: [DOC_DATA] = None, api_response_list: list = None) -> list:
        """API of azure ocr data service to generate OCR based on OCR provider given

        Args:
            doc_data_list ([DOC_DATA], optional): Use these input files to
                -implement technique and generate output files.Defaults to None.
            api_response_list (list, optional): API response will be generated into output file.Defaults to None.

        Returns:
            list: List of generated ocr file path.
        """
        def _call_azure_ocr_post_api(in_doc_obj):
            gen_res_dict = copy.deepcopy(GENERATE_API_RES_STRUCTURE)
            in_doc = in_doc_obj['doc_path']
            gen_res_dict['input_doc'] = in_doc
            image_data = None
            pages = int(in_doc_obj['pages'])
            output_doc = self.get_output_file(
                in_doc, self.output_dir, self.output_to_supporting_folder,
                suffix='_azure_ocr.json')
            gen_res_dict['output_doc'] = output_doc
            if not self.overwrite and os.path.exists(output_doc):
                return gen_res_dict

            api_query_param = self.config_params_dict['api_ocr']['query_params']
            api_query_param = {k: v for k, v in api_query_param.items() if v}
            api_url = self.config_params_dict['api_ocr']['url']
            sub_key = self.config_params_dict['subscription_key']
            try:
                with open(in_doc, "rb") as reader:
                    image_data = reader.read()
                headers = {'Ocp-Apim-Subscription-Key': sub_key,
                           'Content-Type': 'application/octet-stream'}
                self.set_api_log(api_url)
                http = self.__get_http_handle()
                api_url = f'{api_url}?{urlencode(api_query_param)}'
                response = http.request(
                    "post", api_url,
                    body=image_data,
                    headers=headers)
                infy_ocr_generator_metadata = self.get_image_details(in_doc)
                infy_ocr_generator_metadata['doc_page_num'] = pages
                with open(output_doc, 'w', encoding='utf-8') as f:
                    json_result = ast.literal_eval(
                        response.data.decode('utf-8'))
                    json_result['infy_ocr_generator_metadata'] = infy_ocr_generator_metadata
                    json.dump(json_result, f, ensure_ascii=False, indent=4)
            except Exception as e:
                error_reason_text = response.text
                gen_res_dict['output_doc'] = None
                gen_res_dict['error'] = error_reason_text if error_reason_text else e.args[0]
                self.logger.error(error_reason_text)
                full_trace_error = traceback.format_exc()
                self.logger.error(full_trace_error)
            return gen_res_dict

        start_time = time.time()
        ocr_list = []
        with concurrent.futures.ThreadPoolExecutor(
                max_workers=5,
                thread_name_prefix="th_azure_ocr_gen") as executor:
            thread_pool_dict = {
                executor.submit(
                    _call_azure_ocr_post_api,
                    in_doc_obj
                ): in_doc_obj for in_doc_obj in doc_data_list
            }
            for future in concurrent.futures.as_completed(thread_pool_dict):
                ocr_list.append(future.result())
        self.logger.info(
            f"Total time taken for #{len(doc_data_list)} docs is {round((time.time() - start_time)/60,2)} mins")
        return ocr_list

    def __get_http_handle(self):
        http_proxy_url = os.environ.get("OCR_GEN_HTTP_PROXY_URL")
        http_proxy_auth = os.environ.get("OCR_GEN_HTTP_PROXY_AUTH")
        http = None
        if http_proxy_url:
            if http_proxy_auth:
                auth_header = {
                    'proxy-authorization': f'Basic {http_proxy_auth}'}
                http = urllib3.ProxyManager(
                    http_proxy_url, cert_reqs='CERT_NONE', proxy_headers=auth_header)
            else:
                http = urllib3.ProxyManager(
                    http_proxy_url, cert_reqs='CERT_NONE')
        else:
            http = urllib3.PoolManager()
        return http

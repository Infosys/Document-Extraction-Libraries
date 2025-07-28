# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#
import os
import json
import time
import requests
import pandas as pd
import infy_dpp_sdk
from infy_dpp_sdk.data import *
import infy_gen_ai_sdk
from ...common.file_util import FileUtil

PROCESSEOR_CONTEXT_DATA_NAME = "semantic_search"


class SemanticSearch(infy_dpp_sdk.interface.IProcessor):
    """Semantic Search Processor class"""

    def __init__(self):
        self.__file_sys_handler = self.get_fs_handler()
        self.__app_config = self.get_app_config()
        self.__logger = self.get_logger()

        client_config_data_dict = infy_dpp_sdk.ClientConfigManager().get().dict()
        client_config_data = infy_gen_ai_sdk.ClientConfigData(
            **client_config_data_dict)
        infy_gen_ai_sdk.ClientConfigManager().load(client_config_data)

    def do_execute(self, document_data: DocumentData, context_data: dict, config_data: dict) -> ProcessorResponseData:
        def __get_temp_file_path(work_file_path):
            local_file_path = f'{self.__app_config["CONTAINER"]["APP_DIR_TEMP_PATH"]}/{work_file_path}'
            FileUtil.create_dirs_if_absent(os.path.dirname(local_file_path))
            with self.__file_sys_handler.get_file_object(work_file_path) as f:
                with open(local_file_path, "wb") as output:
                    output.write(f.read())
            return local_file_path
        processor_response_data = infy_dpp_sdk.data.ProcessorResponseData()
        semantic_search_config_data = config_data.get('SemanticSearch', {})
        org_files_full_path = context_data['request_creator']['work_file_path']
        self.__logger.debug("org_files_full_path::%s", org_files_full_path)
        from_files_full_path = __get_temp_file_path(org_files_full_path)
        self.__logger.debug("from_files_full_path::%s", from_files_full_path)
        output_result_folder_path = context_data['request_creator']['result_folder_path']
        output_file_name = semantic_search_config_data.get('output_file_name')
        output_file_path = f"{output_result_folder_path}/{output_file_name}"
        updated_output_file_path = output_file_path.replace(
            '\\', '/').replace('//', '/')
        self.__logger.debug("updated_output_file_path::%s",
                            updated_output_file_path)
        truth_data_file_path = from_files_full_path
        for key, value in semantic_search_config_data.items():
            if key == 'services':
                for service in value:
                    if service.get('enabled'):
                        svc_name = service.get('name')
                        svc_url = service.get('url')
                        if svc_name == 'infy_search_service':
                            svc_max_req_per_min = service.get(
                                'max_requests_per_minute')
                            min_interval = 60 / svc_max_req_per_min
                            self.__logger.info(
                                "Max requests allowed per minute:%s", svc_max_req_per_min)
                            svc_req_payload = service.get('request_payload')
                            svc_generation = svc_req_payload.get('generation')
                            svc_headers = service.get('headers')
                            if svc_generation.get('enabled'):
                                svc_top_k_used = svc_generation.get(
                                    'top_k_used')
                                df = pd.read_excel(truth_data_file_path)
                                for index, row in df.iterrows():
                                    rrf_context_list = []
                                    question = row['Question']
                                    self.__logger.debug(
                                        "Question:%s", question)
                                    svc_req_payload['question'] = question
                                    start_time = time.time()
                                    result = self._call_service(
                                        svc_url, svc_req_payload, svc_headers)
                                    end_time = time.time()
                                    elapsed_time = end_time - start_time
                                    sleep_interval = min_interval-elapsed_time
                                    result_json = result.json()
                                    if result_json.get('responseCde') == 200:
                                        response = result_json.get(
                                            'response')
                                        answers = response.get('answers')
                                        answer = answers[0].get('answer')
                                        self.__logger.debug(
                                            "Answer:%s", answer)
                                        top_k_list = answers[0].get(
                                            'top_k_list')
                                        for item in top_k_list:
                                            if "rrf" in item:
                                                rrf_list = item["rrf"]
                                                rrf_context_list = [
                                                    item.get('content') for item in rrf_list]
                                    else:
                                        response_message = result_json.get(
                                            'responseMsg')
                                        self.__logger.error(
                                            "Error::%s", response_message)
                                        raise ValueError(
                                            f"Semantic search service failed with response message: {response_message}")
                                    context_list = self._build_context_list(
                                        rrf_context_list, svc_top_k_used)
                                    # sleep only when interval is non-negative
                                    if sleep_interval > 0:
                                        self.__logger.debug(
                                            "Sleeping for %.2f seconds", sleep_interval)
                                        time.sleep(sleep_interval)
                                    df.at[index, 'answer'] = answer
                                    if not isinstance(context_list, list):
                                        context_list = list(context_list)
                                    if 'contexts' not in df.columns:
                                        df['contexts'] = None
                                    df.at[index, 'contexts'] = context_list
        df.rename(columns={'Question': 'question',
                  'Ground_Truth': 'ground_truth'}, inplace=True)
        dataframe_list = df.to_dict(orient='records')
        self.__file_sys_handler.write_file(
            updated_output_file_path, json.dumps(dataframe_list, indent=4))

        context_data[PROCESSEOR_CONTEXT_DATA_NAME] = {
            "semantic_search_result_file_path": updated_output_file_path
        }
        server_file_dir = os.path.dirname(updated_output_file_path.replace('\\', '/').replace('//', '/').replace(
            self.__app_config["CONTAINER"]["APP_DIR_TEMP_PATH"].replace('\\', '/').replace('//', '/'), ''))
        local_dir = os.path.dirname(updated_output_file_path)
        self._upload_data(f'{local_dir}', f'{server_file_dir}')
        # Populate response data
        processor_response_data.document_data = document_data
        processor_response_data.context_data = context_data

        return processor_response_data

    def _call_service(self, svc_url, svc_req_payload, svc_headers):
        """This function calls the service and returns the response"""
        result = requests.post(
            svc_url, json=svc_req_payload, timeout=120, headers=svc_headers)

        return result

    def _build_context_list(self, rrf_context_list, top_k_used):
        """This function builds the context list based on the top_k_used value"""
        if top_k_used <= 0:
            raise ValueError("Invalid value for top_k_used")
        context_list = []
        combined_context = ".".join(rrf_context_list[:top_k_used])
        context_list.append(combined_context)
        context_list.extend(rrf_context_list[top_k_used:])
        return context_list

    def _upload_data(self, local_file_path, server_file_path):
        try:
            self.__file_sys_handler.put_folder(
                local_file_path, server_file_path)
            self.__logger.info(
                f'Folder {local_file_path} uploaded successfully')
        except Exception as e:
            self.__logger.error(
                f'Error while uploading data to {server_file_path} : {e}')
            raise e

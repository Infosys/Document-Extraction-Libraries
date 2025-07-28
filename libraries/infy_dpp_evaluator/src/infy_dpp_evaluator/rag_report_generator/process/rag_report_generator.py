# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#


import os
import json
import pandas as pd
import infy_dpp_sdk
from infy_dpp_sdk.data import DocumentData, ProcessorResponseData


from infy_dpp_evaluator.common.file_util import FileUtil

PROCESSEOR_CONTEXT_DATA_NAME = "rag_report_generator"


class RagReportGenerator(infy_dpp_sdk.interface.IProcessor):

    def __init__(self) -> None:
        self.__logger = self.get_logger()
        self.__app_config = infy_dpp_sdk.common.AppConfigManager().get_app_config()
        self.__file_sys_handler = self.get_fs_handler()

    def do_execute(self, document_data: DocumentData, context_data: dict, config_data: dict) -> ProcessorResponseData:
        def __get_temp_file_path(work_file_path):
            local_file_path = f'{self.__app_config["CONTAINER"]["APP_DIR_TEMP_PATH"]}/{work_file_path}'
            FileUtil.create_dirs_if_absent(os.path.dirname(local_file_path))
            with self.__file_sys_handler.get_file_object(work_file_path) as f:
                with open(local_file_path, "wb") as output:
                    output.write(f.read())
            return local_file_path
        processor_response_data = ProcessorResponseData()
        container_path = f'{self.__app_config["CONTAINER"]["APP_DIR_TEMP_PATH"]}'
        rag_metrics_file_path = context_data['rag_evaluator']['rag_metrics_file']
        report_gen_config_data = config_data.get(
            'RagReportGenerator', {})
        work_file_path = context_data['request_creator']['work_file_path']
        report_folder_path = context_data['request_creator']['report_folder_path']
        metric_folder_path = context_data['request_creator']['metric_folder_path']
        container_path = f'{self.__app_config["CONTAINER"]["APP_DIR_TEMP_PATH"]}'
        container_rag_metrics_file_path = __get_temp_file_path(
            rag_metrics_file_path)
        container_work_file_path = __get_temp_file_path(work_file_path)
        container_work_file_path = container_path + work_file_path
        container_report_folder_path = container_path + report_folder_path
        container_metric_folder_path = container_path + metric_folder_path
        container_input_folder_path = os.path.dirname(container_work_file_path)
        report_file_name = report_gen_config_data.get(
            'output_report_file')
        output_file_path = f"{report_folder_path}/{report_file_name}"
        os.makedirs(container_report_folder_path, exist_ok=True)
        container_output_file_path = f"{container_report_folder_path}/{report_file_name}"
        self._merge_excel_json(report_gen_config_data,
                               container_input_folder_path, container_metric_folder_path, container_output_file_path)

        context_data[PROCESSEOR_CONTEXT_DATA_NAME] = {
            'rag_report_file_path': output_file_path,
        }
        processor_response_data.document_data = document_data
        processor_response_data.context_data = context_data

        return processor_response_data

    def _merge_excel_json(self, report_gen_config_data, input_folder_path, metric_folder_path, output_file_path):
        merged_data_list = []
        common_col_val_list = []
        qna_data_pk_col_name = report_gen_config_data.get(
            'qna_data_pk_col_name')
        rag_metrics_pk_col_name = report_gen_config_data.get(
            'rag_metrics_pk_col_name')
        # Loop through the Excel files in the input directory
        file_name = ""
        excel_data_list = []
        json_data_list = []
        for excel_file in [f for f in os.listdir(input_folder_path) if f.endswith('.xlsx')]:
            excel_path = os.path.join(input_folder_path, excel_file)
            excel_data = pd.read_excel(excel_path)
            headers_list = list(excel_data.columns)
            file_name = os.path.splitext(excel_file)[0]
            excel_data_list = []
            for ind in range(len(excel_data)):
                row_dict = {}
                for title in headers_list:
                    row_dict[title] = excel_data[title][ind]
                    if title == qna_data_pk_col_name:
                        common_col_val_list.append(excel_data[title][ind])
                excel_data_list.append(row_dict)
        # Loop through the JSON files in the input directory
        for json_file in [f for f in os.listdir(metric_folder_path) if f.endswith('.json')]:
            json_path = os.path.join(metric_folder_path, json_file)
            with open(json_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            json_data_list = []
            for i in range(len(json_data['records']['answer'])):
                j_data_dict = {}
                for record_key, record_val in json_data['records'].items():
                    j_data_dict[record_key] = record_val[str(i)]
                    if record_key == rag_metrics_pk_col_name:
                        common_col_val_list.append(record_val[str(i)])
                json_data_list.append(j_data_dict)
        common_col_val_list = list(set(common_col_val_list))
        for common_col_val in common_col_val_list:
            excel_row_dict = {}
            json_row_dict = {}
            for excel_row in excel_data_list:
                if qna_data_pk_col_name in excel_row and excel_row[qna_data_pk_col_name] == common_col_val:
                    excel_row_dict = excel_row
                    break
            for json_row in json_data_list:
                if rag_metrics_pk_col_name in json_row and json_row[rag_metrics_pk_col_name] == common_col_val:
                    json_row_dict = json_row
                    break
            excel_keys_lower = {key.lower() for key in excel_row_dict.keys()}
            # Remove common columns from json_row_dict (ignore case)
            json_row_dict = {key: value for key, value in json_row_dict.items(
            ) if key.lower() not in excel_keys_lower}
            prefixed_excel_row_dict = {
                f"{file_name}.{key}": value for key, value in excel_row_dict.items()}

            # Merge the two dictionaries
            merged_dict = {**prefixed_excel_row_dict, **json_row_dict}
            merged_data_list.append(merged_dict)
        # Create the final DataFrame and save to Excel
        final_df = pd.DataFrame(merged_data_list)
        final_df.to_excel(output_file_path, index=False)
        server_file_dir = os.path.dirname(output_file_path.replace('\\', '/').replace('//', '/').replace(
            self.__app_config["CONTAINER"]["APP_DIR_TEMP_PATH"].replace('\\', '/').replace('//', '/'), ''))
        local_dir = os.path.dirname(output_file_path)
        self._upload_data(f'{local_dir}', f'{server_file_dir}')

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

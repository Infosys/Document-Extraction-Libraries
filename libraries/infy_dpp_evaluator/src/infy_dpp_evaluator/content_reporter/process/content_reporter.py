# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#


import os
import json
import infy_dpp_sdk
import pandas as pd
from infy_dpp_sdk.data import DocumentData, ProcessorResponseData
from ...common.file_util import FileUtil
PROCESSEOR_CONTEXT_DATA_NAME = "content_reporter"


class ContentReporter(infy_dpp_sdk.interface.IProcessor):

    def __init__(self) -> None:
        self.__logger = self.get_logger()
        self.__app_config = self.get_app_config()
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
        content_reporter_config_data = config_data.get('ContentReporter', {})
        try:
            org_files_full_path = context_data['request_creator']['work_file_path']
            from_files_full_path = __get_temp_file_path(org_files_full_path)
            output_result_folder_path = context_data['request_creator']['result_folder_path']
            output_report_folder_path = context_data['request_creator']['report_folder_path']
            truth_data_file_path = from_files_full_path
            qna_metrics_file_path = context_data['content_evaluator']['qna_metrics_file_path']

            # Read the truth data file into a DataFrame
            truth_data_df = pd.read_excel(truth_data_file_path)
            # Read the qna metrics JSON file
            qna_metrics_list = json.loads(self.__file_sys_handler.read_file(
                qna_metrics_file_path))
            # Convert the DataFrame to a list of dictionaries
            rows_data = truth_data_df.to_dict(orient='records')

            for qna_metrics in qna_metrics_list:
                q_no = qna_metrics['Q_No']
                for row_data in rows_data:
                    if row_data['Q_No'] == q_no:
                        for key, value in qna_metrics.items():
                            if key != 'Q_No':
                                row_data[key] = value

            # Save data into a json file
            output_qna_report_file_path = f"{output_result_folder_path}/qna_report.json"
            self.__file_sys_handler.write_file(
                output_qna_report_file_path, json.dumps(rows_data, indent=4))

            # Convert json file to csv file
            output_qna_report_csv_file_path = f"{output_report_folder_path}/qna_report.csv".replace(
                '\\', '/').replace('//', '/')
            qna_report_local_csv_file_path = f'{self.__app_config["CONTAINER"]["APP_DIR_TEMP_PATH"]}/{output_qna_report_csv_file_path}'.replace(
                '\\', '/').replace('//', '/')
            FileUtil.create_dirs_if_absent(
                os.path.dirname(qna_report_local_csv_file_path))
            # Read the JSON file into a DataFrame
            qna_report_csv_json_data = json.loads(
                self.__file_sys_handler.read_file(output_qna_report_file_path))
            qna_report_df = pd.DataFrame(qna_report_csv_json_data)
            # Convert the DataFrame to a CSV file
            qna_report_df.to_csv(qna_report_local_csv_file_path, index=False)
            self.__upload_file_data(
                qna_report_local_csv_file_path, output_qna_report_csv_file_path)

            # Convert the csv file to a xlsx file
            output_qna_report_excel_file_path = f"{output_report_folder_path}/qna_report.xlsx".replace(
                '\\', '/').replace('//', '/')
            qna_report_local_xlsx_file_path = f'{self.__app_config["CONTAINER"]["APP_DIR_TEMP_PATH"]}/{output_qna_report_excel_file_path}'.replace(
                '\\', '/').replace('//', '/')
            FileUtil.create_dirs_if_absent(
                os.path.dirname(qna_report_local_xlsx_file_path))
            pd.read_csv(qna_report_local_csv_file_path).to_excel(
                qna_report_local_xlsx_file_path, index=False)
            self.__upload_file_data(
                qna_report_local_xlsx_file_path, output_qna_report_excel_file_path)

        except Exception as e:
            print("ERROR: ", e)
            self.__logger.error(e)

        context_data[PROCESSEOR_CONTEXT_DATA_NAME] = {
            "report_file_path": output_qna_report_file_path,
            "report_csv_file_path": output_qna_report_csv_file_path,
            "report_xlsx_file_path": output_qna_report_excel_file_path
        }
        processor_response_data.document_data = document_data
        processor_response_data.context_data = context_data

        return processor_response_data

    def __upload_file_data(self, local_file_path, server_file_path):
        try:
            self.__file_sys_handler.put_file(
                local_file_path, server_file_path)
            self.__logger.info(
                'Folder %s uploaded successfully', local_file_path)
        except Exception as e:
            self.__logger.error(
                'Error while uploading data to %s: %s', server_file_path, e)
            raise e

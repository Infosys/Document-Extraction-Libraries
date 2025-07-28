# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#
import os
import json
import pandas as pd
import infy_dpp_sdk
from infy_dpp_sdk.data.document_data import DocumentData
from infy_dpp_sdk.data.processor_response_data import ProcessorResponseData


PROCESSEOR_CONTEXT_DATA_NAME = "qna_consolidator"


class QnaConsolidator(infy_dpp_sdk.interface.IProcessor):

    def __init__(self) -> None:
        self.__logger = self.get_logger()
        self.__file_sys_handler = self.get_fs_handler()
        self.__app_config = self.get_app_config()

    def do_execute(self, document_data: DocumentData, context_data: dict, config_data: dict) -> ProcessorResponseData:

        processor_response_data = ProcessorResponseData()
        qna_consolidator_config_data = config_data.get('QnaConsolidator', {})
        generated_qna_file_path = context_data.get(
            'qna_generator', {}).get('qna_file_path', "")
        generated_qna_data = json.loads(self.__file_sys_handler.read_file(
            generated_qna_file_path))

        dir_path = self.__file_sys_handler.get_bucket_name()
        container_path = f'{self.__app_config["CONTAINER"]["APP_DIR_TEMP_PATH"]}'

        group_request_file = context_data.get(
            'request_creator').get('group_request_file')
        group_id = group_request_file.replace('_group_request.json', '')

        output_root_path = qna_consolidator_config_data.get('output_root_path')

        container_output_root_path = container_path + output_root_path

        # self.__file_sys_handler.create_folders(
        #     f"{container_output_root_path}/{group_id}")
        os.makedirs(container_output_root_path+group_id, exist_ok=True)
        # relative_qna_file_path = f"{output_root_path}/{group_id}/question_data.xlsx"
        relative_qna_file_path = f"{group_id}/question_data.xlsx"
        # question_data_file_path = f"{dir_path}/{relative_qna_file_path}"
        question_data_file_path = f"{container_output_root_path}{relative_qna_file_path}"

        updated_question_data_file_path = question_data_file_path.replace(
            '\\', '/').replace('//', '/')
        self.__logger.debug("updated_question_data_file_path::%s",
                            updated_question_data_file_path)

        self.create_excel(updated_question_data_file_path,
                          generated_qna_data, qna_consolidator_config_data)

        context_data[PROCESSEOR_CONTEXT_DATA_NAME] = {
            "qna_file_path": output_root_path+relative_qna_file_path
        }
        processor_response_data.document_data = document_data
        processor_response_data.context_data = context_data

        return processor_response_data

    def create_excel(self, excel_file_path, json_data, qna_consolidator_config_data):
        """Create an Excel file from qna_data JSON

        Args:
            excel_file_path (_type_): question_data.xlsx file path
            json_data (_type_): generated qna_data.json
        """
        data = {}
        for excel_header_data in qna_consolidator_config_data.get('transform').keys():
            data.update({excel_header_data: []})

        Q_No_format = qna_consolidator_config_data.get('transform').get("Q_No")
        prefix = Q_No_format.rstrip("#")
        num_digits = len(Q_No_format) - len(prefix)

        self.__logger.debug("excel_file_path::%s", excel_file_path)

        if not os.path.exists(excel_file_path):
            for index, item in enumerate(json_data):
                q_no = index + 1
                formatted_q_no = f"{prefix}{q_no:0{num_digits}d}"
                for col_title, val in qna_consolidator_config_data.get('transform').items():
                    if col_title == "Q_No":
                        data[col_title].append(formatted_q_no)
                    elif val == "page_no":
                        data[col_title].append(
                            ', '.join(map(str, item.get(val))))
                    else:
                        data[col_title].append(item.get(val, ""))

            df = pd.DataFrame(data)
            df.to_excel(excel_file_path, index=False)
        else:
            df = pd.read_excel(excel_file_path)
            if not df.empty:
                last_que = df['Q_No'].iloc[-1]
            else:
                # Handle the case where the DataFrame is empty
                last_que = None

            for index, item in enumerate(json_data):
                if last_que:
                    q_no = int(last_que.removeprefix(prefix))+index + 1
                else:
                    q_no = index + 1
                formatted_q_no = f"{prefix}{q_no:0{num_digits}d}"
                for col_title, val in qna_consolidator_config_data.get('transform').items():
                    if col_title == "Q_No":
                        data[col_title].append(formatted_q_no)
                    elif val == "page_no":
                        data[col_title].append(
                            ', '.join(map(str, item.get(val))))
                    else:
                        data[col_title].append(item.get(val, ""))

            df = pd.concat([df, pd.DataFrame(data)])
            df.to_excel(excel_file_path, index=False)
        server_file_dir = os.path.dirname(excel_file_path.replace('\\', '/').replace('//', '/').replace(
            self.__app_config["CONTAINER"]["APP_DIR_TEMP_PATH"].replace('\\', '/').replace('//', '/'), ''))
        local_dir = os.path.dirname(excel_file_path)
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

# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#
import os
import json
import infy_dpp_sdk
import infy_fs_utils
from ...common.file_util import FileUtil


class QnaGeneratorMode:
    def __init__(self, PROCESSEOR_CONTEXT_DATA_NAME):
        self.__logger = infy_fs_utils.manager.FileSystemLoggingManager().get_fs_logging_handler(
            infy_dpp_sdk.common.Constants.FSLH_DPP).get_logger()
        self.__app_config = infy_dpp_sdk.common.AppConfigManager().get_app_config()
        self.__file_sys_handler = infy_fs_utils.manager.FileSystemManager(
        ).get_fs_handler(infy_dpp_sdk.common.Constants.FSH_DPP)
        self.PROCESSEOR_CONTEXT_DATA_NAME = PROCESSEOR_CONTEXT_DATA_NAME

    def get_qna_generator_mode_dir_created(self, from_request_file_config):
        response_list = []
        work_root_path = from_request_file_config.get('work_root_path')
        storage_uri = FileUtil.safe_file_path(
            self.__file_sys_handler.get_storage_root_uri().split("://")[1])
        read_path = from_request_file_config.get('read_path')
        save_path = from_request_file_config.get('save_path')
        self.__file_sys_handler.create_folders(save_path)
        request_files_found = self.__file_sys_handler.list_files(read_path)
        if request_files_found:
            request_file = request_files_found[0]
            group_id = os.path.basename(request_file).replace(
                '_group_request.json', '')
            sub_folder = f'{work_root_path}/queue/{group_id}'
            # for request_file in request_files_found:
            self.__logger.info(f"Processing file {request_file}")
            request_file_content = self.__file_sys_handler.read_file(
                request_file)
            request_file_content = json.loads(request_file_content)
            work_file_path_list = request_file_content.get(
                'working_file_path_list')
            for work_file_path in work_file_path_list:
                work_file_folder = f'{work_file_path}_files'
                all_work_files_list = self.__file_sys_handler.list_files(
                    work_file_folder)
                processor_reponse_data_json_path = [
                    x for x in all_work_files_list if x.endswith('processor_response_data.json')][0]
                document_data_json = json.loads(self.__file_sys_handler.read_file(
                    processor_reponse_data_json_path))

                # ---- locking the file -----
                input_file_path = document_data_json['document_data'][
                    'metadata']['standard_data']['filepath']['value']
                should_start_process = True
                should_start_process = FileUtil.generate_file_lock(input_file_path, sub_folder,
                                                                   self.__file_sys_handler)
                if not should_start_process:
                    continue

                # ---- Create response data -----
                document_data = document_data_json['document_data']
                context_data = document_data_json.get(
                    'context_data', {})
                message_data = infy_dpp_sdk.data.MessageData()
                response_data = infy_dpp_sdk.data.ProcessorResponseData(
                    document_data=document_data, context_data=context_data)
                response_list.append(response_data)
            self.__file_sys_handler.move_file(request_file, save_path)
            # self.__file_sys_handler.copy_file(request_file, save_path)
        else:
            message_data = infy_dpp_sdk.data.MessageData()
            message_item_data = infy_dpp_sdk.data.MessageItemData(
                message_code=infy_dpp_sdk.data.MessageCodeEnum.INFO_NO_RECORDS_FOUND,
                message_type=infy_dpp_sdk.data.MessageTypeEnum.INFO,
                message_text=f"No files found in {read_path}, stopping pipeline execution")
            message_data.messages.append(message_item_data)

            response_list.append(infy_dpp_sdk.data.ProcessorResponseData(
                document_data=infy_dpp_sdk.data.DocumentData(),
                context_data={},
                message_data=message_data
            ))

        return response_list

# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#
import os
import json
from typing import List
import infy_dpp_sdk
from infy_dpp_sdk.data import *
from infy_dpp_sdk.data.document_data import DocumentData
from infy_dpp_sdk.data.processor_response_data import ProcessorResponseData


from infy_dpp_core.common.file_util import FileUtil

PROCESSEOR_CONTEXT_DATA_NAME = "request_creator"


class RequestCreator(infy_dpp_sdk.interface.IProcessor):

    def __init__(self) -> None:
        self.__logger = self.get_logger()
        self.__file_sys_handler = self.get_fs_handler()

    def do_execute(self, document_data: DocumentData, context_data: dict, config_data: dict) -> ProcessorResponseData:
        response_list = self.__get_document_data(config_data)
        return response_list[0]

    def do_execute_batch(self, document_data_list: List[DocumentData], context_data_list: List[dict], config_data: dict) -> List[ProcessorResponseData]:
        """For do_execute_batch refer to the IProcessor interface. 
        Here overriding exclusively for request creator alone."""
        return self.__get_document_data(config_data)

    def __get_document_data(self, config_data: dict):
        response_list = []
        work_file_path_list = []
        processor_config_data = config_data.get('RequestCreator', {})
        from_data_file_config = processor_config_data.get('from_data_file')
        from_request_file_config = processor_config_data.get(
            'from_request_file')
        work_root_path = from_data_file_config.get('work_root_path')
        # queue_data = from_data_file_config.get('queue')
        batch_size = from_data_file_config.get('batch_size')
        req_file_save_root_path = from_data_file_config.get(
            'to_request_file').get('save_path')

        if from_data_file_config.get("enabled"):
            # --------generate group id & request file----------------
            group_id = f'G-{FileUtil.get_uuid()}'
            sub_folder = f'{work_root_path}/queue/{group_id}'
            request_file = f'{group_id}_group_request.json'
            request_file_path = f'{req_file_save_root_path}/{request_file}'
            self.__file_sys_handler.create_folders(f'{sub_folder}')
            self.__file_sys_handler.create_folders(
                f'{req_file_save_root_path}')
            
            input_files = self.__read_files(config_data, batch_size)
            if input_files:
                for input_doc in input_files:
                    documend_id = FileUtil.get_uuid()
                    doc_dir_name = f"D-{documend_id}"
                    self.__logger.info(f"Processing file {input_doc}")
                    # ---- Check if file is already processed -----
                    should_start_process = True
                    # if queue_data.get('enabled'):
                    #     # should_start_process = FileUtil.generate_file_lock(input_doc, queue_data.get('queue_root_path'),
                    #     #                                                    self.__file_sys_handler)
                    should_start_process = FileUtil.generate_file_lock(input_doc, sub_folder,
                                                                    self.__file_sys_handler)
                    if not should_start_process:
                        continue
                    # ---- Create file paths -----
                    work_file = FileUtil.safe_file_path(
                        f"{work_root_path}/{doc_dir_name}/{os.path.basename(input_doc)}")
                    supporting_files = FileUtil.safe_file_path(
                        f"{work_file}_files/")
                    # storage_uri = FileUtil.safe_file_path(self.__file_sys_handler.get_storage_uri().split("://")[1])
                    storage_uri = FileUtil.safe_file_path(
                        self.__file_sys_handler.get_storage_root_uri().split("://")[1])
                    temp_input_doc = FileUtil.safe_file_path(
                        input_doc).replace(storage_uri, '')

                    # ---- Create supporting files folder -----
                    self.__file_sys_handler.create_folders(supporting_files)

                    # ---- Copy input file to work folder -----
                    self.__file_sys_handler.copy_file(temp_input_doc, work_file)

                    # ---- Create response data -----
                    metadata = infy_dpp_sdk.data.MetaData(
                        standard_data=infy_dpp_sdk.data.StandardData(
                            filepath=infy_dpp_sdk.data.ValueData(value=input_doc)))
                    document_data = infy_dpp_sdk.data.DocumentData(
                        document_id=documend_id, metadata=metadata)
                    context_data = {
                        PROCESSEOR_CONTEXT_DATA_NAME: {
                            "work_file_path": work_file,
                            "group_request_file": request_file
                        }
                    }
                    message_data = infy_dpp_sdk.data.MessageData()
                    response_data = infy_dpp_sdk.data.ProcessorResponseData(
                        document_data=document_data, context_data=context_data)
                    response_list.append(response_data)

                    # ---- Create work file path list -----
                    work_file_path_list.append(work_file)
                request_file_content = {
                    "working_file_path_list": work_file_path_list
                }
                self.__file_sys_handler.write_file(
                    request_file_path, json.dumps(request_file_content, indent=4))

        if from_request_file_config.get("enabled"):
            storage_uri = FileUtil.safe_file_path(
                self.__file_sys_handler.get_storage_root_uri().split("://")[1])
            read_path = from_request_file_config.get('read_path')
            save_path = from_request_file_config.get('save_path')
            self.__file_sys_handler.create_folders(save_path)
            request_files_found = self.__file_sys_handler.list_files(read_path)
            # TODO: sort files by creation time in file sys handler
            # request_files_found = [
            #     f'{storage_uri}/{x}' for x in request_files_found if x.endswith(".json")]
            # request_files_found.sort(key=os.path.getctime)
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
                
        if len(response_list) < 1:
            message_data = infy_dpp_sdk.data.MessageData()
            message_item_data = infy_dpp_sdk.data.MessageItemData(
            message_code=infy_dpp_sdk.data.MessageCodeEnum.INFO_NO_RECORDS_FOUND,   
            message_type=infy_dpp_sdk.data.MessageTypeEnum.INFO,
            message_text="File Not Found, stopping pipeline execution")
            message_data.messages.append(message_item_data)

            response_list.append(infy_dpp_sdk.data.ProcessorResponseData(
                document_data=infy_dpp_sdk.data.DocumentData(),
                context_data={},
                message_data=message_data
            ))
        return response_list

    def __read_files(self, config_data: dict, batch_size: int) -> List[str]:
        req_config_data = config_data.get(
            'RequestCreator', {}).get('from_data_file')
        read_path = req_config_data.get('read_path')
        # TODO: [added by raj] add logic to include/exclude files
        # found_files = self.__file_sys_handler.list_files1(read_path)
        found_files = self.__file_sys_handler.list_files(read_path)
        if len(found_files) > 0:
            found_files = found_files[0:batch_size]
        else:
            self.__logger.info(f"No files found in {read_path}, stopping pipeline execution")
        return found_files

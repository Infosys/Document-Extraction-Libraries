# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                   #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import json
import os
import infy_dpp_sdk
import infy_fs_utils
from infy_dpp_segmentation.common.file_util import FileUtil
from infy_dpp_segmentation.segment_sequencer.process.segment_sequencer import SegmentSequencer


class SegmentDataProcessor:
    def __init__(self) -> None:
        self.__logger = infy_fs_utils.manager.FileSystemLoggingManager().get_fs_logging_handler(infy_dpp_sdk.common.Constants.FSLH_DPP).get_logger()
        self.__app_config = infy_dpp_sdk.common.AppConfigManager().get_app_config()
        self.__file_sys_handler = infy_fs_utils.manager.FileSystemManager().get_fs_handler(infy_dpp_sdk.common.Constants.FSH_DPP)    
    def get_files(self,work_files_path_list):
        server_files_list,local_file_path_list=[],[]
        for work_files_path in work_files_path_list:
            server_files_list.extend(self.__file_sys_handler.list_files1(work_files_path))
        files_list = [x for x in server_files_list if not x.endswith('.json')]
        self.__logger.info(f'files to be processed list {files_list}')
        for file_path in files_list:
            local_file_path= f'{self.__app_config["DEFAULT"]["APP_DIR_TEMP_PATH"]}/{file_path}'
            if os.path.exists(local_file_path):
                local_file_path_list.append(local_file_path)
            else:        
                FileUtil.create_dirs_if_absent(os.path.dirname(local_file_path))
                # file_system_manager_instance.get_file_object(edcoded_files_dir)
                with self.__file_sys_handler.get_file_object(file_path) as input:
                    with open(local_file_path,"wb") as output:
                        output.write(input.read())
                        local_file_path_list.append(local_file_path)
        self.__logger.info(f'local_file_path_list={local_file_path_list}')
        return local_file_path_list,server_files_list
    def parse_segment_data(self,config_file_data,document_data_path_list):
        processor_response_data = infy_dpp_sdk.data.ProcessorResponseData()
        segment_generator_obj = SegmentSequencer(processor_response_data)
        for document_data_path in document_data_path_list:
            org_document_data_json=json.loads(self.__file_sys_handler.read_file(document_data_path))
            org_document_data =  org_document_data_json['document_data']
            org_context_data = org_document_data_json.get('context_data',{})
            document_data=infy_dpp_sdk.data.DocumentData(document_id=org_document_data['document_id'],
                                                        metadata=org_document_data['metadata'],
                                            page_data=org_document_data['page_data'],
                                            business_attribute_data=org_document_data['business_attribute_data'],
                                            text_data=org_document_data['text_data'],
                                            raw_data=org_document_data['raw_data']) 
            processor_response = segment_generator_obj.do_execute(document_data=document_data,context_data=org_context_data,config_data=config_file_data)
            processor_data_json = json.loads(infy_dpp_sdk.common.InfyJSONEncoder().encode(processor_response))
            self._write_data(document_data_path,json.dumps(processor_data_json,indent=4))
            self.__logger.info(f'updated document data has been written here = {document_data_path}')
            
    def _write_data(self,file_path,data):
        try:
            self.__file_sys_handler.write_file(file_path,data)
            self.__logger.info(f'File {file_path} written successfully')
        except Exception as e:
            self.__logger.error(f'Error while writing data to {file_path} : {e}')
            raise e
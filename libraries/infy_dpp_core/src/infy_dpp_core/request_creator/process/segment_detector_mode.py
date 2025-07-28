# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#
import os
import infy_dpp_sdk
import infy_fs_utils
from ...common.file_util import FileUtil


class SegmentDetectorMode:
    def __init__(self, PROCESSEOR_CONTEXT_DATA_NAME):
        self.__logger = infy_fs_utils.manager.FileSystemLoggingManager().get_fs_logging_handler(
            infy_dpp_sdk.common.Constants.FSLH_DPP).get_logger()
        self.__app_config = infy_dpp_sdk.common.AppConfigManager().get_app_config()
        self.__file_sys_handler = infy_fs_utils.manager.FileSystemManager(
        ).get_fs_handler(infy_dpp_sdk.common.Constants.FSH_DPP)
        self.PROCESSEOR_CONTEXT_DATA_NAME = PROCESSEOR_CONTEXT_DATA_NAME

    def get_segment_detector_mode_dir_created(self, input_files, work_root_path):
        response_list = []
        if input_files and work_root_path:
            response_data_list = []
            document_id = FileUtil.get_uuid()
            doc_dir_name = f"D-{document_id}"
            # ---- Create file paths -----
            work_folder_root_path = FileUtil.safe_file_path(
                f"{work_root_path}/{doc_dir_name}")
            self.__file_sys_handler.create_folders(work_folder_root_path)
            work_folder_docs_path = FileUtil.safe_file_path(
                f"{work_root_path}/{doc_dir_name}/docs")
            self.__file_sys_handler.create_folders(work_folder_docs_path)
            result_data_path = FileUtil.safe_file_path(
                f"{work_folder_root_path}/result")
            self.__file_sys_handler.create_folders(result_data_path)
            docs_truth_data_path = FileUtil.safe_file_path(
                f"{work_folder_root_path}/docs_truth_data")
            self.__file_sys_handler.create_folders(docs_truth_data_path)
            for input_doc in input_files:
                sub_folder = os.path.basename(os.path.dirname(input_doc))
                if sub_folder == 'prev_model_ext_data':
                    prev_docs_ext_data = FileUtil.safe_file_path(
                        f"{work_folder_root_path}/prev_model_ext_data")
                    self.__file_sys_handler.create_folders(
                        prev_docs_ext_data)
                else:
                    prev_docs_ext_data = None

            for input_doc in input_files:
                self.__logger.info(f"Processing file {input_doc}")
                _, extension = os.path.splitext(input_doc)
                if not (extension == ".xlsx" or extension == ".csv" or extension == ".json" or extension == ".html"):
                    if 'bbox_images' in os.path.normpath(input_doc).split(os.sep):
                        continue
                    sub_folder = os.path.basename(
                        os.path.dirname(input_doc))
                    # ---- Create file paths -----
                    work_file = FileUtil.safe_file_path(
                        f"{work_folder_docs_path}/{sub_folder}/{os.path.basename(input_doc)}")
                    supporting_files_folder = FileUtil.safe_file_path(
                        f"{work_file}_files/")
                else:
                    sub_folder = os.path.basename(
                        os.path.dirname(input_doc))
                    if sub_folder != 'docs_truth_data':
                        sub_folder = 'docs_truth_data/' + sub_folder
                    # ---- Create file paths -----
                    work_file = FileUtil.safe_file_path(
                        f"{work_folder_root_path}/{sub_folder}/{os.path.basename(input_doc)}")
                    supporting_files_folder = FileUtil.safe_file_path(
                        f"{work_folder_root_path}/{sub_folder}/")
                    # storage_uri = FileUtil.safe_file_path(self.__file_sys_handler.get_storage_uri().split("://")[1])
                storage_uri = FileUtil.safe_file_path(
                    self.__file_sys_handler.get_storage_root_uri().split("://")[1])
                temp_input_doc = FileUtil.safe_file_path(
                    input_doc).replace(storage_uri, '')
                # ---- Create supporting files folder -----
                self.__file_sys_handler.create_folders(
                    supporting_files_folder)
                # ---- Copy input file to work folder -----
                self.__file_sys_handler.copy_file(
                    temp_input_doc, work_file)
                # ---- Create response data -----
            metadata = infy_dpp_sdk.data.MetaData(
                standard_data=infy_dpp_sdk.data.StandardData(
                    filepath=infy_dpp_sdk.data.ValueData(value=work_root_path)))
            document_data = infy_dpp_sdk.data.DocumentData(
                document_id=document_id, metadata=metadata)
            context_data = {
                self.PROCESSEOR_CONTEXT_DATA_NAME: {
                    "work_root_path": work_root_path,
                    "work_file_path": work_folder_docs_path,
                    "result_data_path": result_data_path,
                    "docs_truth_data_path": docs_truth_data_path,
                    "prev_docs_ext_data_path": prev_docs_ext_data
                }
            }
            message_data = infy_dpp_sdk.data.MessageData()
            response_data = infy_dpp_sdk.data.ProcessorResponseData(
                document_data=document_data, context_data=context_data)
            response_data_list.append(response_data)
            response_list = response_data_list
        return response_list

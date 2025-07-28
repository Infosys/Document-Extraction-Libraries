# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import json
import os
import pandas as pd
from typing import List
import infy_dpp_sdk
from infy_dpp_sdk.data import *
from infy_dpp_sdk.data.document_data import DocumentData
from infy_dpp_sdk.data.processor_response_data import ProcessorResponseData

from infy_dpp_core.common.file_util import FileUtil


PROCESSEOR_CONTEXT_DATA_NAME = "request_closer"


class RequestCloserV2(infy_dpp_sdk.interface.IProcessor):

    def __init__(self) -> None:
        self.__file_sys_handler = self.get_fs_handler()
        self.__app_config = self.get_app_config()
        self.__logger = self.get_logger()

    def do_execute(self, document_data: DocumentData, context_data: dict, config_data: dict) -> ProcessorResponseData:
        def __get_temp_file_path(work_file_path):
            local_file_path = f'{self.__app_config["CONTAINER"]["APP_DIR_TEMP_PATH"]}/{work_file_path}'
            FileUtil.create_dirs_if_absent(os.path.dirname(local_file_path))
            with self.__file_sys_handler.get_file_object(work_file_path) as f:
                with open(local_file_path, "wb") as output:
                    output.write(f.read())
            return local_file_path

        response_data = infy_dpp_sdk.data.ProcessorResponseData(
            document_data=document_data, context_data=context_data)
        doc_id = document_data.document_id
        if not doc_id:
            return response_data
        processor_config_data = config_data.get('RequestCloser', {})
        work_root_path = processor_config_data.get('work_root_path')
        work_file_path = context_data.get(
            'request_creator').get('work_file_path')
        if not context_data.get('rag_report_generator'):
            work_folder_path = os.path.dirname(work_file_path)
        else:
            work_folder_path = work_file_path
        if not context_data.get('segment_detector'):
            # ------ Create output document directory --------------
            output_path = FileUtil.safe_file_path(
                f"{processor_config_data.get('output_root_path')}/D-{doc_id}")
            self.__file_sys_handler.create_folders(output_path)

            # ------ Save document data in output location ------
            document_data_file = FileUtil.safe_file_path(
                f"{output_path}/document_data.json")
            self.__file_sys_handler.write_file(
                document_data_file, infy_dpp_sdk.common.PydanticUtil.get_json_str(
                    document_data, indent=4))
        else:
            output_path = context_data.get(
                'segment_evaluator').get('segment_evaluator_data_path')[0]
            output_path = os.path.dirname(os.path.dirname(output_path))
            # ------ Save document data in output location ------
            document_data_file = FileUtil.safe_file_path(
                f"{output_path}/document_data.json")
            self.__file_sys_handler.write_file(
                document_data_file, infy_dpp_sdk.common.PydanticUtil.get_json_str(
                    document_data, indent=4))

        # ------ Move original input file to output location ---------
        if context_data.get('request_creator').get('work_file_path').endswith(('.json', '.xlsx')):
            original_file = document_data.metadata.standard_data.filepath.value
            original_file_name = document_data.metadata.standard_data.filename.value
            # storage_uri = FileUtil.safe_file_path(self.__file_sys_handler.get_storage_uri().split("://")[1])
            storage_uri = FileUtil.safe_file_path(
                self.__file_sys_handler.get_storage_root_uri().split("://")[1])
            temp_original_file = FileUtil.safe_file_path(
                original_file).replace(storage_uri, '')
            data_file_output_path = processor_config_data.get(
                'data_file').get('output_root_path')
            if data_file_output_path:
                self.__file_sys_handler.move_file(
                    temp_original_file, output_path+"/"+original_file_name)
        else:
            if context_data.get('segment_detector'):
                output_path = context_data.get('segment_evaluator').get(
                    'segment_evaluator_data_path')[0]
                output_path = os.path.dirname(os.path.dirname(output_path))
                docs_truth_input_files = self.__file_sys_handler.list_files(
                    "/data/input/docs_truth_data")
                root_input_folder = self.__file_sys_handler.list_files(
                    "/data/input")
                storage_uri = FileUtil.safe_file_path(
                    self.__file_sys_handler.get_storage_root_uri().split("://")[1])
                docs_truth_output_path = FileUtil.safe_file_path(
                    output_path+"/docs_truth_data")
                self.__file_sys_handler.create_folders(docs_truth_output_path)
                docs_truth_images_path = FileUtil.safe_file_path(
                    output_path+"/docs_truth_data/bbox_images")
                self.__file_sys_handler.create_folders(docs_truth_images_path)
                for files in docs_truth_input_files:
                    _, extension = os.path.splitext(files)
                    if 'bbox_images' in os.path.normpath(files).split(os.sep) and not (extension == ".xlsx" or extension == ".csv"):
                        temp_original_file = FileUtil.safe_file_path(
                            files).replace(storage_uri, '')
                        # Extract the subpath after bbox_images
                        subpath_after_bbox_images = os.path.relpath(
                            files, "/data/input/docs_truth_data/bbox_images")
                        # Create the necessary directories
                        target_path = os.path.join(
                            docs_truth_images_path, os.path.dirname(subpath_after_bbox_images))
                        self.__file_sys_handler.create_folders(target_path)
                        # Move the file to the target directory
                        self.__file_sys_handler.move_file(
                            temp_original_file, os.path.join(target_path, os.path.basename(files)))
                    else:
                        temp_original_file = FileUtil.safe_file_path(
                            files).replace(storage_uri, '')
                        base_dirname = os.path.basename(os.path.dirname(files))
                        if base_dirname != 'docs_truth_data':
                            truth_tables_path = docs_truth_output_path + "/" + base_dirname
                            self.__file_sys_handler.create_folders(
                                truth_tables_path)
                            self.__file_sys_handler.move_file(
                                temp_original_file, truth_tables_path+"/"+os.path.basename(files))
                        else:
                            self.__file_sys_handler.move_file(
                                temp_original_file, docs_truth_output_path+"/"+os.path.basename(files))

                docs_ext_path = context_data.get(
                    'segment_detector').get('yolox_aggregate_data_path')
                result_files = self.__file_sys_handler.list_files(
                    os.path.dirname(docs_ext_path))
                docs_result_output_path = FileUtil.safe_file_path(
                    output_path+"/result")
                self.__file_sys_handler.create_folders(docs_result_output_path)
                for files in result_files:
                    temp_original_file = FileUtil.safe_file_path(
                        files).replace(storage_uri, '')
                    self.__file_sys_handler.copy_file(
                        temp_original_file, docs_result_output_path+"/"+os.path.basename(files))

                for files in root_input_folder:
                    _, extension = os.path.splitext(files)
                    if 'prev_model_ext_data' in os.path.normpath(files).split(os.sep) and extension == ".json":
                        temp_original_file = FileUtil.safe_file_path(
                            files).replace(storage_uri, '')
                        self.__file_sys_handler.move_file(
                            temp_original_file, docs_result_output_path+"/"+os.path.basename(files))

                docs_folder_path = FileUtil.safe_file_path(output_path+"/docs")
                self.__file_sys_handler.create_folders(docs_folder_path)
                for files in root_input_folder:
                    _, extension = os.path.splitext(files)
                    if 'docs' in os.path.normpath(files).split(os.sep):
                        temp_original_file = FileUtil.safe_file_path(
                            files).replace(storage_uri, '')
                        base_dirname = os.path.basename(os.path.dirname(files))
                        target_path = docs_folder_path + "/" + base_dirname
                        self.__file_sys_handler.create_folders(target_path)
                        # Move the file to the target directory
                        self.__file_sys_handler.move_file(
                            temp_original_file, target_path+"/"+os.path.basename(files))
            else:
                org_input_files = self.__file_sys_handler.list_files(
                    "/data/input/")
                storage_uri = FileUtil.safe_file_path(
                    self.__file_sys_handler.get_storage_root_uri().split("://")[1])
                for files in org_input_files:
                    temp_original_file = FileUtil.safe_file_path(
                        files).replace(storage_uri, '')
                    self.__file_sys_handler.move_file(
                        temp_original_file, output_path+"/"+os.path.basename(files))

        # ------ Save rag_result json ------
        reader_context = context_data.get('reader', {})
        if reader_context:
            work_file = context_data.get('request_creator', {}).get(
                'work_file_path')
            from_files_full_path = __get_temp_file_path(work_file)
            out_file_full_path = f'{from_files_full_path}_files'
            rag_result = self._get_rag_result(
                context_data, from_files_full_path)
            rag_result_path = os.path.join(
                out_file_full_path, "rag_result.json")
            FileUtil.save_to_json(
                rag_result_path, rag_result)
            # upload the json file to the work location
            server_file_dir = os.path.dirname(rag_result_path.replace('\\', '/').replace('//', '/').replace(
                self.__app_config["CONTAINER"]["APP_DIR_TEMP_PATH"].replace('\\', '/').replace('//', '/'), ''))
            local_dir = os.path.dirname(rag_result_path)
            self._upload_data(f'{local_dir}', f'{server_file_dir}')

        if processor_config_data.get('from_request_file', {}).get('enabled'):
            request_read_path = processor_config_data.get(
                'from_request_file').get('read_path')
            request_save_path = processor_config_data.get(
                'from_request_file').get('save_path')
            group_request_file = context_data.get(
                'request_creator').get('group_request_file')
            group_id = group_request_file.replace('_group_request.json', '')
            request_file_path = f'{request_read_path}/{group_request_file}'
            sub_folder = f'{work_root_path}/queue/{group_id}'
            original_file = document_data.metadata.standard_data.filepath.value
            # ----- Unlock queue file -----
            FileUtil.unlock_file(original_file, sub_folder,
                                 self.__file_sys_handler)

            # ------ Move request file to complete location -------
            if self.__file_sys_handler.exists(sub_folder):
                total_hash_files = self.__file_sys_handler.list_files(
                    sub_folder)
                if len(total_hash_files) == 0:
                    self.__file_sys_handler.create_folders(request_save_path)
                    self.__file_sys_handler.move_file(
                        request_file_path, request_save_path)
                    self.__file_sys_handler.delete_folder(sub_folder)
            else:
                self.__file_sys_handler.create_folders(request_save_path)
                self.__file_sys_handler.move_file(
                    request_file_path, request_save_path)

        context_data[PROCESSEOR_CONTEXT_DATA_NAME] = {
            "output_folder_path": output_path,
            "work_folder_path": work_folder_path
        }
        response_data.document_data = document_data
        response_data.context_data = context_data

        # ------ Save processor response data in work location ------
        filename = document_data.metadata.standard_data.filename.value
        if context_data.get('rag_report_generator'):
            doc_work_location = f"{work_root_path}/D-{document_data.document_id}/reports"
        else:
            if context_data.get('segment_detector'):
                doc_work_location = f"{work_root_path}/D-{document_data.document_id}/{filename}"
            else:
                doc_work_location = f"{work_root_path}/D-{document_data.document_id}/{filename}_files"
        self.__file_sys_handler.write_file(
            f"{doc_work_location}/processor_response_data.json",
            infy_dpp_sdk.common.PydanticUtil.get_json_str(response_data, indent=4))
        return response_data

    def _get_rag_result(self, context_data, from_files_full_path):
        def _get_dataset(i):
            top_k_matches_list = query_retriever_context.get(
                "queries")[i].get("top_k_matches")
            match_list = [match for match_dict in top_k_matches_list for match_list in match_dict.values()
                          for match in match_list]
            data = {
                "Content": [match.get("content") for match in match_list],
                "Score": [match.get("score") for match in match_list],
                "Metadata-page_no": [match.get("meta_data"
                                               ).get("page_no") for match in match_list],
                "Metadata-doc_name": [match.get("meta_data"
                                                ).get("doc_name") for match in match_list]
            }
            pd.DataFrame(data)

            content_list = []
            chunk_list = []

            for j in range(len(match_list)):
                content_list.append(pd.DataFrame(data)['Content'][j])
                chunk_list.append(
                    str(pd.DataFrame(data)['Metadata-page_no'][j]))

            q_no = str(excel_data.Q_No[i])
            question = query_retriever_context.get(
                "queries")[i].get("question")

            ground_truth = str(excel_data.Ground_Truth[i])
            file_name = str(excel_data.Document_Name[i])
            page_no = str(excel_data.Ground_Truth_Page[i])

            output_list = reader_context.get("output")
            model_output = output_list[i].get("model_output")

            if (isinstance(model_output, dict)):
                output = str(model_output.get("answer"))
            else:
                output = model_output

            text = {"question": question, "contexts": content_list, "ground_truth": ground_truth, "answer": output, "additional_field_Q_No": q_no,
                    "additional_field_chunk_num": chunk_list, "additional_field_file_name": file_name, "additional_field_page_no": page_no}

            return text

        dataset_list = []
        reader_context = context_data.get('reader', {})
        query_retriever_context = context_data.get('query_retriever', {})
        excel_data = pd.read_excel(from_files_full_path)
        total_question = len(excel_data.Question)
        for i in range(total_question):
            dataset = _get_dataset(i)
            dataset_list.append(dataset)

        return dataset_list

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

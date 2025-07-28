# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#
import os
from typing import List
import infy_dpp_sdk
from infy_dpp_sdk.data import DocumentData, ProcessorResponseData
from infy_dpp_evaluator.common.file_util import FileUtil
from infy_dpp_evaluator.segment_detector.service.table_detector_yolox_service import TableDetectorYoloxService
from infy_dpp_evaluator.segment_detector.service.table_detector_aggregator_service import TableDetectorAggregatorService

PROCESSEOR_CONTEXT_DATA_NAME = "segment_detector"


class SegmentDetector(infy_dpp_sdk.interface.IProcessor):
    def __init__(self):
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

        self.__logger.debug('Segment Detection Started')
        yolox_file_path_list = []
        processor_response_data = ProcessorResponseData()
        segment_detector_config_data = config_data.get('SegmentDetector', {})
        org_files_full_path = context_data['request_creator']['work_file_path']
        result_data_path = context_data['request_creator']['result_data_path']
        docs_truth_data_path = context_data['request_creator']['docs_truth_data_path']
        context_data[PROCESSEOR_CONTEXT_DATA_NAME] = {}
        images_file_path_list = self.__read_files(org_files_full_path)
        docs_truth_data_path = self.__read_files(docs_truth_data_path)
        for technique in segment_detector_config_data.get('techniques', []):
            if not technique.get("enabled"):
                continue
            else:
                input_file_type = technique.get("input_file_type")
                model_provider_name = technique.get("model_provider_name")
                technique_name = technique.get("name")
                file_exten_list = technique.get('filter').get('include')
                model_provider_dict = {}
                if model_provider_name:
                    model_provider_dict = [modelProviders for modelProviders in segment_detector_config_data.get(
                        "modelProviders") if modelProviders.get("provider_name") == model_provider_name][0]

                if input_file_type == 'image':
                    if technique_name == "img_yolox_table_detector":
                        image_full_file_path = []
                        image_jpeg_files_path_list = [
                            image_path for image_path in images_file_path_list if os.path.splitext(image_path)[1][1:] in file_exten_list]
                        # in images_file_path_list if image_path.lower().endswith(('.jpg', '.jpeg'))]
                        for image_path in image_jpeg_files_path_list:
                            image_full_file_path.append(
                                __get_temp_file_path(image_path))
                        for docs_truth_data_path in docs_truth_data_path:
                            docs_truth_data_path = __get_temp_file_path(
                                docs_truth_data_path)

                        yolox_table_detector_obj = TableDetectorYoloxService(
                            self.__file_sys_handler, self.__app_config, self.__logger, model_provider_dict)
                        yolox_file_path_list = yolox_table_detector_obj.detect_table(
                            image_full_file_path)
                    context_data[PROCESSEOR_CONTEXT_DATA_NAME]['yolox_file_path_list'] = images_file_path_list
                    yolox_table_aggregator_obj = TableDetectorAggregatorService(
                        self.__file_sys_handler, self.__app_config, self.__logger, model_provider_dict)
                    yolox_aggregate_data_path = yolox_table_aggregator_obj.aggregate_data_from_folders(
                        org_files_full_path, result_data_path)
                    context_data[PROCESSEOR_CONTEXT_DATA_NAME]['yolox_aggregate_data_path'] = yolox_aggregate_data_path
        processor_response_data.document_data = document_data
        processor_response_data.context_data = context_data

        self.__logger.debug('Segment Detection Completed')

        return processor_response_data

    def __read_files(self, from_files_folder_path) -> List[str]:
        found_files = self.__file_sys_handler.list_files(
            from_files_folder_path)
        if len(found_files) > 0:
            self.__logger.info(
                "Found %d files in %s", len(found_files), from_files_folder_path)
        else:
            self.__logger.info(
                "No files found in %s, stopping pipeline execution", from_files_folder_path)
        return found_files

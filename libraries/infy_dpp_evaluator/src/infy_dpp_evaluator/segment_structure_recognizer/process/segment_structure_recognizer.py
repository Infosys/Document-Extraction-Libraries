"""Module for segment structure recognition"""
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
from infy_dpp_evaluator.segment_structure_recognizer.service.table_structure_recognizer_aggregator_service import TableStructureRecognizerAggregatorService
from infy_dpp_evaluator.segment_structure_recognizer.service.table_structure_recognizer_ld_service import TableStructureRecognizerLdService


PROCESSEOR_CONTEXT_DATA_NAME = "segment_structure_recognizer"


class SegmentStructureRecognizer(infy_dpp_sdk.interface.IProcessor):
    """Class for segment structure recognition"""

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

        self.__logger.debug('Segment Structure Recognition Started')
        ld_file_path_list = []
        tsr_aggregate_data_path = None
        processor_response_data = ProcessorResponseData()
        ssr_config_data = config_data.get(
            'SegmentStructureRecognizer', {})
        org_files_full_path = context_data['request_creator']['work_file_path']
        result_data_path = context_data['request_creator']['result_data_path']
        docs_truth_data_path = context_data['request_creator']['docs_truth_data_path']
        context_data[PROCESSEOR_CONTEXT_DATA_NAME] = {}
        images_file_path_list_all = self.__list_files(org_files_full_path)
        # Remove files having '_files' in their path
        images_file_path_list = [
            file for file in images_file_path_list_all if '_files' not in file]
        docs_truth_data_path = self.__list_files(docs_truth_data_path)
        techniques = ssr_config_data.get('techniques', [])
        dataset_name_with_version = ssr_config_data.get(
            'dataset_name_with_version', "")
        output_file_prefix = ssr_config_data.get(
            'output_file_prefix', "")

        # input_root_path = ssr_config_data.get(
        #     'input_root_path')+f"D-{FileUtil.get_uuid()}"
        # from_file_path = context_data['segment_evaluator']['segment_evaluator_data_path'][0]
        # /data/output/D-6d627a57-699e-4b86-957b-33c99d2d8e20/metrics/extracted_data_metrics.json
        # from_file_dir = os.path.dirname(from_file_path)
        # docs_truth_data_path = f'{self.__app_config["CONTAINER"]["APP_DIR_TEMP_PATH"]}/{docs_truth_data_path}'
        # sd_metrics_file_path = f'{self.__app_config["CONTAINER"]["APP_DIR_TEMP_PATH"]}/{from_file_dir}'
        # FileUtil.create_dirs_if_absent(from_file_path)
        # FileUtil.create_dirs_if_absent(docs_truth_data_path)
        for technique in techniques:
            if not technique.get("enabled"):
                continue
            else:
                input_file_type = technique.get("input_file_type")
                text_provider_name = technique.get("text_provider_name")
                # model_provider_name = technique.get("model_provider_name")
                # tsr_provider_name = technique.get("tsr_provider_name")
                technique_name = technique.get("name")
                segment_bbox_source = technique.get("segment_bbox_source", {})
                file_exten_list = technique.get('filter').get('include')
                truth_data = segment_bbox_source.get("truth_data")
                detector = segment_bbox_source.get("detector")
                bbox_source = 'truth_data' if truth_data else 'detector'

                text_provider_dict = {}
                if text_provider_name:
                    text_provider_dict = [textProviders for textProviders in ssr_config_data.get(
                        "textProviders") if textProviders.get("provider_name") == text_provider_name][0]
                if input_file_type == 'image':
                    # if technique_name == "img_infy_opencv_ld":
                    if technique_name == "img_infy_opencv_ld" or technique_name == "img_infy_rgb_ld":
                        image_full_file_path = []
                        image_jpeg_files_path_list = [
                            image_path for image_path in images_file_path_list if os.path.splitext(image_path)[1][1:] in file_exten_list]
                        # image_path for image_path
                        # in images_file_path_list if image_path.lower().endswith(('.jpg', '.jpeg'))]
                        for image_path in image_jpeg_files_path_list:
                            image_full_file_path.append(
                                __get_temp_file_path(image_path))
                        for docs_truth_data_path in docs_truth_data_path:
                            docs_truth_data_path = __get_temp_file_path(
                                docs_truth_data_path)

                        tsr_ld_service_obj = TableStructureRecognizerLdService(
                            self.__file_sys_handler, self.__app_config, self.__logger, text_provider_dict, technique_name)
                        ld_file_path_list = tsr_ld_service_obj.recognize_structure(
                            image_full_file_path, bbox_source, docs_truth_data_path, technique_name, result_data_path)
                    # context_data[PROCESSEOR_CONTEXT_DATA_NAME]['opencv_ld_file_path_list'] = opencv_ld_file_path_list
                    tsr_aggregator_obj = TableStructureRecognizerAggregatorService(
                        self.__file_sys_handler, self.__app_config, self.__logger, text_provider_dict, dataset_name_with_version, output_file_prefix)
                    tsr_aggregate_data_path = tsr_aggregator_obj.aggregate_data_from_folders(
                        org_files_full_path, result_data_path, technique_name)
                    # context_data[PROCESSEOR_CONTEXT_DATA_NAME]['tsr_aggregate_data_path'] = tsr_aggregate_data_path

                    # docs_truth_data_path = context_data['request_creator']['docs_truth_data_path']
                    # context_data[PROCESSEOR_CONTEXT_DATA_NAME]['ssr_result'] = images_file_path_list
        context_data[PROCESSEOR_CONTEXT_DATA_NAME] = {
            "ld_file_path_list": ld_file_path_list,
            "tsr_aggregate_data_path": tsr_aggregate_data_path
        }

        processor_response_data.document_data = document_data
        processor_response_data.context_data = context_data
        self.__logger.debug('Segment Structure Recognition Completed')

        return processor_response_data

    def __list_files(self, from_files_folder_path) -> List[str]:
        found_files = self.__file_sys_handler.list_files(
            from_files_folder_path)
        found_files = [
            file for file in found_files if not file.endswith('.html')]
        if len(found_files) > 0:
            self.__logger.info(
                "Found %d files in %s", len(found_files), from_files_folder_path)
        else:
            self.__logger.info(
                "No files found in %s, stopping pipeline execution", from_files_folder_path)
        return found_files

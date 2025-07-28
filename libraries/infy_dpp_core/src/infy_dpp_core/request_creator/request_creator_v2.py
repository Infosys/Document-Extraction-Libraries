# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#
import os
from typing import List
import infy_dpp_sdk
from infy_dpp_sdk.data.document_data import DocumentData
from infy_dpp_sdk.data.processor_response_data import ProcessorResponseData
from .process.content_evaluation_mode import ContentEvaluationMode
from .process.report_mode import ReportMode
from .process.segment_detector_mode import SegmentDetectorMode
from .process.qna_generator_mode import QnaGeneratorMode
from .process.inference_mode import InferenceMode
from .process.evaluation_mode import EvaluationMode
from .process.rag_evaluation_mode import RagEvaluationMode


PROCESSEOR_CONTEXT_DATA_NAME = "request_creator"


class RequestCreatorV2(infy_dpp_sdk.interface.IProcessor):

    def __init__(self) -> None:
        self.__file_sys_handler = self.get_fs_handler()
        self.__app_config = self.get_app_config()
        self.__logger = self.get_logger()

    def do_execute(self, document_data: DocumentData, context_data: dict, config_data: dict) -> ProcessorResponseData:

        response_list = self.__get_document_data(config_data)
        return response_list[0]

    def do_execute_batch(self, document_data_list: List[DocumentData], context_data_list: List[dict], config_data: dict) -> List[ProcessorResponseData]:
        """For do_execute_batch refer to the IProcessor interface.
        Here overriding exclusively for request creator alone."""
        return self.__get_document_data(config_data)

    def __get_document_data(self, config_data: dict):
        response_list = []
        processor_config_data = config_data.get('RequestCreator', {})
        inference_mode = processor_config_data.get(
            'inference', {}).get('enabled')
        evaluation_mode = processor_config_data.get(
            'evaluation', {}).get('enabled')
        report_mode = processor_config_data.get('report', {}).get('enabled')
        qna_generator_mode = processor_config_data.get(
            'qna_generator', {}).get('enabled')
        segment_detector_mode = processor_config_data.get(
            'segmentDetection', {}).get('enabled')
        content_evaluation_mode = processor_config_data.get(
            'content_evaluation', {}).get('enabled')
        rag_evaluation_mode = processor_config_data.get(
            'rag_evaluation', {}).get('enabled')

        if inference_mode:
            action_config_data = processor_config_data.get('inference', {})
        elif evaluation_mode:
            action_config_data = processor_config_data.get('evaluation', {})
        elif report_mode:
            action_config_data = processor_config_data.get('report', {})
        elif qna_generator_mode:
            action_config_data = processor_config_data.get('qna_generator', {})
        elif segment_detector_mode:
            action_config_data = processor_config_data.get(
                'segmentDetection', {})
        elif content_evaluation_mode:
            action_config_data = processor_config_data.get(
                'content_evaluation', {})
        elif rag_evaluation_mode:
            action_config_data = processor_config_data.get(
                'rag_evaluation', {})

        from_data_file_config = action_config_data.get('from_data_file')
        if from_data_file_config:
            work_root_path = from_data_file_config.get('work_root_path')
            input_files = self.__read_files(from_data_file_config)
            if input_files:
                if content_evaluation_mode:
                    content_evaluation_mode_obj = ContentEvaluationMode(
                        PROCESSEOR_CONTEXT_DATA_NAME)
                    response_list = content_evaluation_mode_obj.get_content_eval_mode_dir_created(
                        input_files, work_root_path)
                elif rag_evaluation_mode:
                    rag_evaluation_mode_obj = RagEvaluationMode(
                        PROCESSEOR_CONTEXT_DATA_NAME)
                    response_list = rag_evaluation_mode_obj.create_rag_eval_mode_dirs(
                        input_files, work_root_path)
                elif report_mode:
                    report_mode_obj = ReportMode(
                        PROCESSEOR_CONTEXT_DATA_NAME)
                    response_list = report_mode_obj.get_report_mode_dir_created(
                        input_files, work_root_path)
                elif segment_detector_mode:
                    segment_detector_mode_obj = SegmentDetectorMode(
                        PROCESSEOR_CONTEXT_DATA_NAME)
                    response_list = segment_detector_mode_obj.get_segment_detector_mode_dir_created(
                        input_files, work_root_path)
                else:
                    for input_doc in input_files:
                        _, extension = os.path.splitext(input_doc)
                        if inference_mode and extension == ".xlsx":
                            inference_mode_obj = InferenceMode(
                                PROCESSEOR_CONTEXT_DATA_NAME)
                            response_list = inference_mode_obj.get_inference_mode_dir_created(
                                input_doc, from_data_file_config)

                        elif evaluation_mode and extension == ".json":
                            evaluation_mode_obj = EvaluationMode(
                                PROCESSEOR_CONTEXT_DATA_NAME)
                            response_list = evaluation_mode_obj.get_evaluation_mode_dir_created(
                                input_doc, from_data_file_config)

        if qna_generator_mode:
            from_request_file_config = action_config_data.get(
                'from_request_file')
            qna_generator_mode_obj = QnaGeneratorMode(
                PROCESSEOR_CONTEXT_DATA_NAME)
            response_list = qna_generator_mode_obj.get_qna_generator_mode_dir_created(
                from_request_file_config)

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

    def __read_files(self, config_data: dict) -> List[str]:
        # req_config_data = config_data.get(
        #     'RequestCreator', {}).get('from_data_file')
        req_config_data = config_data
        read_path = req_config_data.get('read_path')
        # logic to include/exclude files
        found_files = self.__file_sys_handler.list_files(read_path)

        if len(found_files) > 0:
            self.__logger.info(
                "Found %d files in %s", len(found_files), read_path)
        else:
            self.__logger.info(
                "No files found in %s, stopping pipeline execution", read_path)
        return found_files

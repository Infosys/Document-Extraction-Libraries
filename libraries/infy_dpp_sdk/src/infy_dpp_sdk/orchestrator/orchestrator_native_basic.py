# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import json
import logging
import importlib
import traceback
from typing import List
from deprecated import deprecated
import infy_fs_utils
from ..interface import IOrchestratorNative, IProcessor
from ..data import DocumentData, ProcessorResponseData, MessageCodeEnum
from ..common import Constants
from ..common._internal.processor_helper import ProcessorHelper
from ..common._internal.config_data_helper import ConfigDataHelper


class OrchestratorNativeBasic(IOrchestratorNative):
    """Orchestrator that invokes processors natively."""

    __fs_handler: infy_fs_utils.interface.IFileSystemHandler = None
    __logger: logging.Logger = None

    class Model():
        """Model class (MVC model)"""
        input_config_file_path: None
        input_config_data: None

    @deprecated(version='0.0.10', reason="This class is deprecated. Please use new class OrchestratorNative.")
    def __init__(self, input_config_data: dict = None,
                 input_config_file_path: str = None):
        self.__fs_handler = infy_fs_utils.manager.FileSystemManager(
        ).get_fs_handler(Constants.FSH_DPP)
        if infy_fs_utils.manager.FileSystemLoggingManager().has_fs_logging_handler(Constants.FSLH_DPP):
            self.__logger = infy_fs_utils.manager.FileSystemLoggingManager(
            ).get_fs_logging_handler(Constants.FSLH_DPP).get_logger()
        else:
            self.__logger = logging.getLogger(__name__)
        config_data_helper_obj = ConfigDataHelper(self.__logger)
        model = self.Model()
        if input_config_file_path:
            _input_config_data = json.loads(self.__fs_handler.read_file(
                input_config_file_path))
        elif input_config_data:
            _input_config_data = input_config_data
        else:
            raise ValueError(
                'input_config_data or input_config_file_path is required')

        model.input_config_data = config_data_helper_obj.do_interpolation(
            _input_config_data)
        self.__model = model

    @deprecated(version='0.0.10', reason="This class is deprecated. Please use new class OrchestratorNative.")
    def run_batch(self, document_data_list: List[DocumentData] = None,
                  context_data_list: List[dict] = None) -> List[ProcessorResponseData]:
        """
        Run the orchestrator pipeline.

        Args:
            document_data_list (List[DocumentData], optional): List of document data.
            context_data_list (List[dict], optional): List of context data.

        Returns:
            List[ProcessorResponseData]: List of processor response data.
        """
        self.__logger.debug('Entering run_batch')
        processor_response_data_list = []
        for processor_input_config_data in self.__model.input_config_data.get('processor_list'):
            self.__logger.info('Current processor: '
                               + processor_input_config_data['processor_namespace'] + '->'
                               + processor_input_config_data['processor_class_name'])
            if not processor_input_config_data.get('enabled'):
                self.__logger.debug(
                    'Processor skipped as processor is not enabled')
                continue

            document_data_list = document_data_list if document_data_list else [
                DocumentData()]
            context_data_list = context_data_list if context_data_list else [
                {}]

            # ------------ Auto import the processors ------------------
            library = importlib.import_module(
                processor_input_config_data['processor_namespace'])
            my_processor_obj: IProcessor = getattr(
                library, processor_input_config_data['processor_class_name'])()

            # ------------ Filter the config data ------------------
            filtered_config_data = {}
            for processor_input_config_name in processor_input_config_data.get('processor_input_config_name_list', []):
                filtered_config_data[processor_input_config_name] = self.__model.input_config_data.get(
                    'processor_input_config').get(processor_input_config_name)

            # ------------ Call the pre run hook ------------------
            my_processor_obj, processor_response_data_list = self.pre_run_hook(
                my_processor_obj, filtered_config_data, processor_response_data_list)
            # ------------ Skip processor execution when pre run hook returns None ------------------
            if not my_processor_obj:
                self.__logger.debug(
                    'Processor skipped as pre_run_hook returned None')
                continue

            # ------------ Call the processor ------------------
            try:
                new_processor_response_list = my_processor_obj.do_execute_batch(
                    document_data_list, context_data_list, filtered_config_data)
            except Exception as ex:
                full_trace_error = traceback.format_exc()
                self.__logger.error(full_trace_error)
                new_processor_response_list = []
                for document_data, context_data in zip(document_data_list, context_data_list):
                    _processor_response_data = ProcessorHelper.create_processor_response_data(
                        document_data, context_data, ex)
                    new_processor_response_list.append(
                        _processor_response_data)

            # ------------ Call the post run hook ------------------
            processor_response_data_list = self.post_run_hook(
                my_processor_obj, filtered_config_data, processor_response_data_list,
                new_processor_response_list)

            # ------------ Skip processor execution when document id is None ------------------
            document_data_list_temp, context_data_list_temp = [], []
            # file_not_found = False

            stop_orchestrator = False

            server_exception_message_list = []
            for processor_response_data in processor_response_data_list:
                server_exception_message_list.extend(ProcessorHelper.get_messages(
                    processor_response_data, MessageCodeEnum.SERVER_ERR_UNHANDLED_EXCEPTION))

            if server_exception_message_list:
                stop_orchestrator = True
                message = "\n".join([str(x)
                                    for x in server_exception_message_list])
                self.__logger.error(message)
                print(message)

            no_records_found_message_list = []
            for processor_response_data in processor_response_data_list:
                no_records_found_message_list.extend(ProcessorHelper.get_messages(
                    processor_response_data, MessageCodeEnum.INFO_NO_RECORDS_FOUND))

            if no_records_found_message_list:
                stop_orchestrator = True
                message = "\n".join([str(x)
                                    for x in no_records_found_message_list])
                self.__logger.info(message)
                print(message)

            for processor_response_data in processor_response_data_list:
                if processor_response_data.document_data.document_id:
                    document_data_list_temp.append(
                        processor_response_data.document_data)
                    context_data_list_temp.append(
                        processor_response_data.context_data)
                # if processor_response_data.message_data and processor_response_data.message_data.messages \
                #         and processor_response_data.message_data.messages[0].message_code == MessageCodeEnum.INFO_NO_RECORDS_FOUND:
                #     file_not_found = True
                #     message = f"{processor_response_data.message_data.messages[0].message_text}"
                #     break
            if stop_orchestrator:
                # self.__logger.debug(message)
                # print(message)
                break
            document_data_list, context_data_list = document_data_list_temp, context_data_list_temp

        self.__logger.debug('Exiting run_batch')
        return processor_response_data_list

    def pre_run_hook(self, processor_instance: object, config_data: dict,
                     processor_response_data_list: List[ProcessorResponseData]) \
            -> (object, List[ProcessorResponseData]):
        """
        Pre run hook for the processor.

        Args:
            processor_instance (object): Processor instance.
            config_data (dict): Configuration data.
            processor_response_data_list (List[ProcessorResponseData]): List of processor response data.

        Returns:
            tuple: Processor instance and list of processor response data.
        """
        return processor_instance, processor_response_data_list

    def post_run_hook(self, processor_instance: object, config_data: dict,
                      processor_response_data_list: List[ProcessorResponseData],
                      new_processor_response_data_list: List[ProcessorResponseData]) \
            -> List[ProcessorResponseData]:
        """
        Post run hook for the processor.

        Args:
            processor_instance (object): Processor instance.
            config_data (dict): Configuration data.
            processor_response_data_list (List[ProcessorResponseData]): List of processor response data.
            new_processor_response_data_list (List[ProcessorResponseData]): List of new processor response data.

        Returns:
            List[ProcessorResponseData]: Updated list of processor response data.
        """
        return new_processor_response_data_list

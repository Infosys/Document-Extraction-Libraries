# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                   #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import json
import logging
import importlib
from typing import List
import infy_fs_utils

from ..interface import IOrchestratorNative, IProcessor
from ..data import DocumentData, ProcessorResponseData
from ..common import Constants


class OrchestratorNativeBasic(IOrchestratorNative):
    """Orchestrator Native Implementation class"""

    __fs_handler: infy_fs_utils.interface.IFileSystemHandler = None
    __logger: logging.Logger = None

    class Model():
        """Model class (MVC model)"""
        input_config_file_path: None
        input_config_data: None

    def __init__(self, input_config_data: dict = None,
                 input_config_file_path: str = None):
        self.__fs_handler = infy_fs_utils.manager.FileSystemManager(
        ).get_fs_handler(Constants.FSH_DPP)
        if infy_fs_utils.manager.FileSystemLoggingManager().has_fs_logging_handler(Constants.FSLH_DPP):
            self.__logger = infy_fs_utils.manager.FileSystemLoggingManager(
            ).get_fs_logging_handler(Constants.FSLH_DPP).get_logger()
        else:
            self.__logger = logging.getLogger(__name__)

        model = self.Model()
        if input_config_file_path:
            model.input_config_data = json.loads(self.__fs_handler.read_file(
                input_config_file_path))
        elif input_config_data:
            model.input_config_data = input_config_data
        else:
            raise ValueError(
                'input_config_data or input_config_file_path is required')
        self.__model = model

    def run_batch(self, document_data_list: List[DocumentData] = None,
                  context_data_list: List[dict] = None) -> List[ProcessorResponseData]:
        """Run the orchestrator pipeline"""
        self.__logger.debug('Entering run_batch')
        processor_response_data_list = []
        for config_entry in self.__model.input_config_data.get('processor_list'):
            self.__logger.info('Current processor: '
                               + config_entry['processor_namespace'] + '->'
                               + config_entry['processor_class_name'])
            if not config_entry.get('enabled'):
                self.__logger.debug(
                    'Processor skipped as processor is not enabled')
                continue

            document_data_list = document_data_list if document_data_list else [
                DocumentData()]
            context_data_list = context_data_list if context_data_list else [
                {}]

            # ------------ Auto import the processors ------------------
            library = importlib.import_module(
                config_entry['processor_namespace'])
            my_processor_obj: IProcessor = getattr(
                library, config_entry['processor_class_name'])()

            # ------------ Filter the config data ------------------
            filtered_config_data = {}
            for proc_config_dep in config_entry.get('processor_input_config_name_list', []):
                filtered_config_data[proc_config_dep] = self.__model.input_config_data.get(
                    'processor_input_config').get(proc_config_dep)

            # ------------ Call the pre run hook ------------------
            my_processor_obj, processor_response_data_list = self.pre_run_hook(
                my_processor_obj, filtered_config_data, processor_response_data_list)
            # ------------ Skip processor execution when pre run hook returns None ------------------
            if not my_processor_obj:
                self.__logger.debug(
                    'Processor skipped as pre_run_hook returned None')
                continue

            # ------------ Call the processor ------------------
            new_processor_response_list = my_processor_obj.do_execute_batch(
                document_data_list, context_data_list, filtered_config_data)

            # ------------ Call the post run hook ------------------
            processor_response_data_list = self.post_run_hook(
                my_processor_obj, filtered_config_data, processor_response_data_list, new_processor_response_list)

            # ------------ Skip processor execution when document id is None ------------------
            document_data_list_temp, context_data_list_temp = [], []
            for response_data in processor_response_data_list:
                if response_data.document_data.document_id:
                    document_data_list_temp.append(response_data.document_data)
                    context_data_list_temp.append(response_data.context_data)
            document_data_list, context_data_list = document_data_list_temp, context_data_list_temp
        self.__logger.debug('Exiting run_batch')
        return processor_response_data_list

    def pre_run_hook(self, processor_instance: object, config_data: dict,
                     processor_response_data_list: List[ProcessorResponseData]) \
            -> (object, List[ProcessorResponseData]):
        """ Pre run hook for the processor """
        return processor_instance, processor_response_data_list

    def post_run_hook(self, processor_instance: object, config_data: dict,
                      processor_response_data_list: List[ProcessorResponseData],
                      new_processor_response_data_list: List[ProcessorResponseData]) -> List[ProcessorResponseData]:
        """ Post run hook for the processor """
        return new_processor_response_data_list

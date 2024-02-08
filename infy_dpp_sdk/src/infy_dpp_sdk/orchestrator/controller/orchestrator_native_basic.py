# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import json
import importlib
from typing import List

import infy_dpp_sdk

from ...data.document_data import DocumentData
from ...data.processor_response_data import ProcessorResponseData
from ...interface.i_orchestrator_native import IOrchestratorNative


class OrchestratorNativeBasic(IOrchestratorNative):
    """Orchestrator Native Implementation class"""

    def __init__(self, pipeline_input_config_data: dict = None,
                 pipeline_input_config_file_path: str = None):
        if pipeline_input_config_file_path:
            with open(pipeline_input_config_file_path, encoding='utf-8') as file:
                __pipeline_input_config_data = json.load(file)
        elif pipeline_input_config_data:
            __pipeline_input_config_data = pipeline_input_config_data
        else:
            raise ValueError(
                'pipeline_input_config_data or pipeline_input_config_file_path is required')
        self.__pipeline_input_config_data = __pipeline_input_config_data

    def run_batch(self, document_data_list: List[DocumentData] = None,
                  context_data_list: List[dict] = None) -> List[ProcessorResponseData]:
        """Run the orchestrator pipeline"""
        processor_response_data_list = []
        for config_entry in self.__pipeline_input_config_data.get('processor_list'):
            if not config_entry.get('enabled'):
                continue

            document_data_list = document_data_list if document_data_list else [
                DocumentData()]
            context_data_list = context_data_list if context_data_list else [
                {}]

            # ------------ Auto import the processors ------------------
            library = importlib.import_module(
                config_entry['processor_namespace'])
            my_processor_obj: infy_dpp_sdk.interface.IProcessor = getattr(
                library, config_entry['processor_class_name'])()

            # ------------ Filter the config data ------------------
            filtered_config_data = {}
            for proc_config_dep in config_entry.get('processor_input_config_name_list', []):
                filtered_config_data[proc_config_dep] = self.__pipeline_input_config_data.get(
                    'processor_input_config').get(proc_config_dep)

            # ------------ Call the pre run hook ------------------
            my_processor_obj, processor_response_data_list = self.pre_run_hook(
                my_processor_obj, filtered_config_data, processor_response_data_list)
            # ------------ Skip processor execution when pre run hook returns None ------------------
            if not my_processor_obj:
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

# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#


import json
import logging
import importlib
import traceback
import infy_fs_utils
from ...interface import IProcessor
from ...data import (ControllerRequestData, ControllerResponseData)
from ...common.dpp_json_encoder import DppJSONEncoder
from ...common import Constants
from ...common.snapshot_util import SnapshotUtil
from ...common.processor_helper import ProcessorHelper


class NativeOperator():
    """Orchestrator for native calls"""

    def __init__(self) -> None:
        self.__fs_handler = infy_fs_utils.manager.FileSystemManager(
        ).get_fs_handler(Constants.FSH_DPP)
        if infy_fs_utils.manager.FileSystemLoggingManager().has_fs_logging_handler(Constants.FSLH_DPP):
            self.__logger = infy_fs_utils.manager.FileSystemLoggingManager(
            ).get_fs_logging_handler(Constants.FSLH_DPP).get_logger()
        else:
            self.__logger = logging.getLogger(__name__)

    def execute_processor(self, processor_deployment_config_data: dict,
                          processor_input_config_data: dict):
        """Execute a processor"""

        new_output_variables_dict = {}
        try:

            # ------------ Auto import the processors ------------------
            library = importlib.import_module(
                processor_input_config_data['processor_namespace'])
            my_processor_obj: IProcessor = getattr(
                library, processor_input_config_data['processor_class_name'])()

            # ------------ Read the controller request file ------------------
            controller_request_file_path = processor_deployment_config_data.get('args', {}).get(
                'request_file_path', None)
            if controller_request_file_path:
                controller_request_file_data = json.loads(self.__fs_handler.read_file(
                    controller_request_file_path))
                input_config_file_data = json.loads(self.__fs_handler.read_file(
                    controller_request_file_data['input_config_file_path']))
            else:
                raise ValueError(
                    'controller_request_file_path is required')

            # # ------------ Filter the config data ------------------
            # filtered_config_data = {}
            # for processor_input_config_name in processor_input_config_data.get(
            #         'processor_input_config_name_list', []):
            #     filtered_config_data[processor_input_config_name] = input_config_file_data.get(
            #         'processor_input_config').get(processor_input_config_name)

            controller_request_data: ControllerRequestData = ControllerRequestData(
                **controller_request_file_data)
            snapshot_util = SnapshotUtil()
            document_data_list, context_data_list, _ = snapshot_util.load_snapshots(
                controller_request_data)
            config_data = processor_input_config_data.get(
                'processor_input_config', {})

            # # ------------ Read document data and context data list ----------
            # snapshot_dir_root_path = controller_request_file_data['snapshot_dir_root_path'] + "/"
            # document_data_file_path_list = [
            #     snapshot_dir_root_path +
            #     x['snapshot']['document_data_file_path'] for x in controller_request_file_data['records']]
            # document_data_list = [DocumentData(**json.loads(self.__fs_handler.read_file(
            #     x))) for x in document_data_file_path_list]
            # context_data_file_path_list = [
            #     snapshot_dir_root_path +
            #     x['snapshot']['context_data_file_path'] for x in controller_request_file_data['records']]
            # context_data_list = [json.loads(self.__fs_handler.read_file(
            #     x)) for x in context_data_file_path_list]

            # ------------ Call the processor ------------------
            try:
                new_processor_response_list = my_processor_obj.do_execute_batch(
                    document_data_list, context_data_list, config_data)
            except Exception as ex:
                full_trace_error = traceback.format_exc()
                self.__logger.error(full_trace_error)
                new_processor_response_list = []
                for document_data, context_data in zip(document_data_list, context_data_list):
                    _processor_response_data = ProcessorHelper.create_processor_response_data(
                        document_data, context_data, ex)
                    new_processor_response_list.append(
                        _processor_response_data)

            controller_response_data: ControllerResponseData = snapshot_util.save_snapshots(
                controller_request_data, new_processor_response_list)

            dpp_controller_res_file_path = self.__create_controller_response_file(
                controller_response_data)

            output_variables_dict = processor_deployment_config_data['output']['variables']

            if output_variables_dict:
                for output_variable, _ in output_variables_dict.items():
                    new_output_variables_dict[output_variable] = dpp_controller_res_file_path

        except Exception as ex:
            raise Exception(ex) from ex
        return new_output_variables_dict

    def __create_controller_response_file(self, controller_response_data: ControllerResponseData):
        temp_folder_path = Constants.ORCHESTRATOR_ROOT_PATH
        request_id = controller_response_data.request_id
        self.__fs_handler.create_folders(temp_folder_path)
        json_file_path = f"{temp_folder_path}/{request_id}_dpp_controller_response.json"
        self.__logger.info("Processor input config file path - %s",
                           json_file_path)
        # Due to TypeError: Object of type ProcessorFilterData is not JSON serializable
        controller_response_data = json.loads(
            DppJSONEncoder().encode(controller_response_data))
        data_as_json_str = json.dumps(controller_response_data, indent=4)
        self.__fs_handler.write_file(
            json_file_path, data_as_json_str, encoding='utf-8')
        # rel_path = json_file_path.replace(data_root_path, "")
        # return rel_path
        return json_file_path

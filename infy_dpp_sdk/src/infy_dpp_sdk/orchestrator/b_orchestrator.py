# ===============================================================================================================#
# Copyright 2022 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

from abc import ABC, abstractmethod
import json
from typing import List
import logging
import time
import uuid
import concurrent.futures
import infy_fs_utils
from ..data import (ControllerRequestData, ControllerResponseData,
                    ProcessorFilterData, ProcessorResponseData, MessageCodeEnum)
from ..common.dpp_json_encoder import DppJSONEncoder
from ..common import Constants
from ..common.snapshot_util import SnapshotUtil
from ..common.processor_helper import ProcessorHelper
from ..interface import IOrchestrator


class BOrchestrator(IOrchestrator, ABC):
    """Base class for orchestrator"""

    _fs_handler: infy_fs_utils.interface.IFileSystemHandler = None
    _logger: logging.Logger = None
    __PROCESSOR_DISABLED = "disabled"

    def __init__(self, input_config_file_path: str, deployment_config_file_path: str = None):
        super().__init__(input_config_file_path, deployment_config_file_path)
        self.__model = self._get_model()
        self._logger = self._get_logger()
        self._fs_handler = self._get_fs_handler()
        self.__processor_exec_list = None
        self.__processor_exec_output_dict = None

    # ---------- Abstract Methods ---------
    @abstractmethod
    def execute_processor(self, processor_input_config_data: dict,
                          processor_deployment_config_data: dict,
                          orchestrator_config_data: dict) -> dict:
        """Execute a processor"""
        raise NotImplementedError("execute_processor not implemented")

    # ---------- Public Methods ---------
    def run_batch(self, context_data: dict = None):
        model = self.__model
        snapshot_util = SnapshotUtil()
        processor_exec_list = []
        processor_exec_output_dict = {}
        request_group_num = f"R-{str(uuid.uuid4())[24:]}"
        processor_list = model.input_config_data.get('processor_list', [])
        processor_list_count = len(processor_list)
        for idx, processor_input_config_data in enumerate(processor_list):
            processor_num = f"{idx+1:03d}"
            sub_processor_list = processor_input_config_data.get(
                'processor_list')
            if sub_processor_list:
                concurrent_result_list = []
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    futures = []
                    for idxY, processor_input_config_dataY in enumerate(sub_processor_list):
                        sub_processor_num = f"{processor_num}.{idxY+1:03d}"
                        future = executor.submit(self.__prepare_and_run_processor,
                                                 processor_input_config_dataY, sub_processor_num,
                                                 request_group_num, processor_list_count,
                                                 processor_exec_output_dict, context_data,
                                                 processor_exec_list)
                        futures.append(future)
                    for future in futures:
                        result = future.result()
                        if result[0] == self.__PROCESSOR_DISABLED:
                            continue
                        concurrent_result_list.append(result)
                        # if result and len(result) == 2:
                        #     processor_response_data_list, stop_orchestrator = result
                if not concurrent_result_list:
                    continue
                sub_processor_nums = [
                    x for x in processor_exec_output_dict if f"{processor_num}." in x]
                controller_res_file_path_list = [processor_exec_output_dict.get(x, {}).get(
                    Constants.SYS_CONTROLLER_RES_FILE_PATH) for x in sub_processor_nums]
                controller_response_data, processor_response_data_list = \
                    snapshot_util.consolidate_controller_response_data(
                        controller_res_file_path_list)
                controller_res_file_path = snapshot_util.save_controller_response_data(
                    controller_response_data)
                for sub_processor_num in sub_processor_nums:
                    del processor_exec_output_dict[sub_processor_num]
                processor_exec_output_dict[processor_num] = {
                    Constants.SYS_CONTROLLER_RES_FILE_PATH: controller_res_file_path
                }
                # TODO: M Write logic to merge the results of sub-processors
                # E.g. R-c7d6f3d00afa-003.001_dpp_controller_response.json AND
                # R-c7d6f3d00afa-003.002_dpp_controller_response.json
                # That means 003.001 document_data, context_data, message_data with
                # 003.002 document_data, context_data, message_data
            else:
                result = self.__prepare_and_run_processor(
                    processor_input_config_data, processor_num, request_group_num,
                    processor_list_count, processor_exec_output_dict, context_data,
                    processor_exec_list)
                if result and len(result) == 2:
                    processor_response_data_list, stop_orchestrator = result
                if stop_orchestrator:
                    # self.__logger.debug(message)
                    # print(message)
                    break
        self.__processor_exec_list = processor_exec_list
        self.__processor_exec_output_dict = processor_exec_output_dict
        # return processor_exec_list, processor_exec_output_dict
        return processor_response_data_list

    def get_run_batch_summary(self) -> list:
        """Get run summary post run_batch execution"""
        return self.__processor_exec_list, self.__processor_exec_output_dict

    # ---------- Private Methods ---------
    def __prepare_and_run_processor(self, processor_input_config_data: dict,
                                    processor_num, request_group_num, processor_list_count,
                                    processor_exec_output_dict, context_data,
                                    processor_exec_list):

        model = self.__model
        processor_name = processor_input_config_data.get(
            'processor_name')

        request_id = f"{request_group_num}-{processor_num}"
        message_info = f"Processor #{processor_num} of {processor_list_count}| {request_id} | {processor_name}"
        if not processor_input_config_data.get('enabled'):
            self._logger.info(message_info + " | Skipped (disabled)")
            return self.__PROCESSOR_DISABLED, None  # continue
        self._logger.info(message_info + " | Started")
        start_time = time.time()

        # Get processor specifig input config variables which are same as overall input config variables
        input_variable_dict = model.input_config_data.get(
            'variables', {}).copy()
        # Fetch output of previous processor and update input_variable_dict
        prev_processor_num = self.__get_previous_processor_num(
            processor_num, processor_exec_output_dict)
        prev_processor_output_dict = processor_exec_output_dict.get(
            prev_processor_num, {})
        input_variable_dict.update(prev_processor_output_dict)

        # Prepare config data which is a subset of entire "processor_input_config" data
        # containing only the required config data specified in "processor_input_config_name_list"
        filtered_config_data = {}
        for processor_input_config_name in processor_input_config_data.get(
                'processor_input_config_name_list', []):
            filtered_config_data[processor_input_config_name] = model.input_config_data.get(
                'processor_input_config').get(processor_input_config_name)
        # Update to main entity
        processor_input_config_data['processor_input_config'] = filtered_config_data

        # Generate controller request data
        controller_request_data = self.__create_controller_request_data(
            processor_input_config_data, request_id, input_variable_dict, context_data)

        # Get processor specific deployment config data
        processor_deployment_config_data = None
        if model.deployment_config_data:
            item = model.deployment_config_data['processors'].get(
                processor_name)
            alias_of = item.get("alias_of")
            item = model.deployment_config_data['processors'].get(
                alias_of) if alias_of else item
            processor_deployment_config_data = item.copy()

        controller_response_data, output_variable_dict = self.__run_processor(
            controller_request_data, processor_input_config_data,
            processor_deployment_config_data, input_variable_dict)

        processor_response_data_list: List[ProcessorResponseData] = SnapshotUtil(
        ).create_processor_response_data_list(controller_response_data)

        self.__update_processor_name(
            processor_name, processor_response_data_list)

        stop_orchestrator = False
        tracked_message_list = self.__get_tracked_message_list(
            processor_response_data_list)

        processor_exec_output_dict[processor_num] = output_variable_dict
        processor_exec_list.append(processor_name)
        elapsed_time = round((time.time() - start_time), 4)
        message_elapsed_time = f"Execution time: {elapsed_time} secs"
        if tracked_message_list:
            stop_orchestrator = True
            itemised_message = ""
            for document_id, message_list in tracked_message_list:
                itemised_message += f"\ndocument_id: {document_id} => " + "\n".join([x.json(indent=4)
                                                                                    for x in message_list])
            message_err = message_info + \
                f" | Failed | {message_elapsed_time}"
            # message_err += " | Error: " + "\n".join([x.json(indent=4)
            #                                          for x in tracked_message_list])
            message_err += " | Error: " + itemised_message
            self._logger.error(message_err)
            print(message_err)
        else:
            self._logger.info(
                message_info + " | Completed | " + message_elapsed_time)
        return processor_response_data_list, stop_orchestrator

    def __run_processor(self, controller_request_data: ControllerRequestData,
                        processor_input_config_data: dict, processor_deployment_config_data: dict,
                        input_variable_dict: dict):
        model = self.__model
        controller_request_file_path = self.__create_controller_request_file(
            controller_request_data)
        input_variable_dict[Constants.SYS_CONTROLLER_REQ_FILE_PATH] = controller_request_file_path
        processor_deployment_config_data = self.__update_processor_deployment_config(
            processor_deployment_config_data, input_variable_dict)
        orchestrator_config_data = model.input_config_data.get(
            'orchestrator', {})
        output_variable_dict = self.execute_processor(
            processor_input_config_data, processor_deployment_config_data,
            orchestrator_config_data)
        controller_response_data = self.__read_controller_response_data(
            output_variable_dict)
        return controller_response_data, output_variable_dict

    def __create_controller_request_data(self, processor_dict, request_id,
                                         input_variable_dict, context_data) -> ControllerRequestData:
        model = self.__model
        SNAPSHOT_FOLDER_PATH = Constants.ORCHESTRATOR_SNAPSHOT_PATH
        self._fs_handler.create_folders(SNAPSHOT_FOLDER_PATH)
        controller_request_data = ControllerRequestData(
            dpp_version=Constants.DPP_VERSION,
            request_id=request_id,
            description="Auto-generated by DPP orchestrator",
            input_config_file_path=model.input_config_file_path,
            processor_filter=ProcessorFilterData(
                includes=[processor_dict['processor_name']]),
            context=context_data,
            snapshot_dir_root_path=SNAPSHOT_FOLDER_PATH
        )

        controller_response_data = self.__read_controller_response_data(
            input_variable_dict)
        if controller_response_data:
            controller_request_data.records = controller_response_data.records

        return controller_request_data

    def __read_controller_response_data(self, variables_dict) -> ControllerResponseData:
        dpp_controller_res_file_path = variables_dict.get(
            Constants.SYS_CONTROLLER_RES_FILE_PATH, None)
        controller_response_data: ControllerResponseData = SnapshotUtil().read_controller_response_data(
            dpp_controller_res_file_path)
        return controller_response_data

    def __create_controller_request_file(self, controller_request_data: ControllerRequestData):
        temp_folder_path = Constants.ORCHESTRATOR_ROOT_PATH
        request_id = controller_request_data.request_id
        self._fs_handler.create_folders(temp_folder_path)
        json_file_path = f"{temp_folder_path}/{request_id}{Constants.CONTROLLER_REQUEST_FILE_NAME_SUFFIX}"
        self._logger.info("Processor input config file path - %s",
                          json_file_path)
        # Due to TypeError: Object of type ProcessorFilterData is not JSON serializable
        controller_request_data = json.loads(
            DppJSONEncoder().encode(controller_request_data))
        data_as_json_str = json.dumps(controller_request_data, indent=4)
        self._fs_handler.write_file(
            json_file_path, data_as_json_str, encoding='utf-8')
        # rel_path = json_file_path.replace(data_root_path, "")
        # return rel_path
        return json_file_path

    def __get_tracked_message_list(self,
                                   processor_response_data_list: List[ProcessorResponseData]) -> list:
        TRACKED_MESSAGE_CODES = [
            MessageCodeEnum.SERVER_ERR_UNHANDLED_EXCEPTION,
            MessageCodeEnum.INFO_NO_RECORDS_FOUND]
        tracked_message_list = []

        for tracked_message_code in TRACKED_MESSAGE_CODES:
            for processor_response_data in processor_response_data_list:
                messages = ProcessorHelper.get_messages(
                    processor_response_data, tracked_message_code)
                if messages:
                    tracked_message_list.append(
                        [processor_response_data.document_data.document_id, messages])

        return tracked_message_list

    def __update_processor_name(self, processor_name: str,
                                processor_response_data_list: List[ProcessorResponseData]) -> None:
        for processor_response_data in processor_response_data_list:
            message_data = processor_response_data.message_data
            if message_data:
                for message_item_data in message_data.messages:
                    message_item_data.processor_name = processor_name

    def __update_processor_deployment_config(self, processor_deployment_config_data,
                                             input_variable_dict) -> dict:
        __processor_deployment_config_data = processor_deployment_config_data.copy()
        updated_arg_dict = {}
        for k, v in __processor_deployment_config_data.get('args', {}).items():
            if '${' in v:
                f_v = v.replace('${', '').replace('}', '')
                v = input_variable_dict.get(f_v.upper() if f_v else f_v)
            updated_arg_dict[k] = v
        __processor_deployment_config_data['args'] = updated_arg_dict

        updated_arg_dict = {}
        for k, v in __processor_deployment_config_data.get('env', {}).items():
            if '${' in v:
                f_v = v.replace('${', '').replace('}', '')
                v = input_variable_dict.get(f_v.upper() if f_v else f_v)
            updated_arg_dict[k] = v
        __processor_deployment_config_data['env'] = updated_arg_dict

        # Add storage related env variables
        storage_config_data: infy_fs_utils.data.StorageConfigData = \
            self._get_fs_handler().get_storage_config_data()
        std_env_var = {
            Constants.SYS_ENV_VAR_DPP_STORAGE_ROOT_URI: storage_config_data.storage_root_uri,
            Constants.SYS_ENV_VAR_DPP_STORAGE_SERVER_URL: storage_config_data.storage_server_url,
            Constants.SYS_ENV_VAR_DPP_STORAGE_ACCESS_KEY: storage_config_data.storage_access_key,
            Constants.SYS_ENV_VAR_DPP_STORAGE_SECRET_KEY: storage_config_data.storage_secret_key
        }
        __processor_deployment_config_data['env'].update(std_env_var)

        return __processor_deployment_config_data

    def __get_previous_processor_num(self, processor_num: str, processor_exec_output_dict: dict) -> str:
        processor_exec_list = list(processor_exec_output_dict.keys())
        if not processor_exec_list:
            return None
        # processor_exec_list.append(processor_num)
        # is_sub_processor_flow = "." in processor_num
        processor_exec_list.reverse()
        processor_exec_map = {}
        for item in processor_exec_list:
            main, _, sub = item.partition('.')
            if main not in processor_exec_map:
                processor_exec_map[main] = []
            if sub:
                processor_exec_map[main].append(sub)

        is_sub_processor_flow = "." in processor_num
        if is_sub_processor_flow:
            for item in processor_exec_map:
                main, _, sub = item.partition('.')
                if not sub:
                    return main
        else:
            for main_num, sub_nums in processor_exec_map.items():
                if not sub_nums:
                    return main_num
                keys = [f"{main_num}.{x}" for x in sub_nums]
                return keys

        # processor_exec_list = processor_exec_list.reverse()
        # match_start_idx = None
        # for idx, item in enumerate(processor_exec_list):
        #     if processor_num == item:
        #         match_start_idx = idx + 1
        #         break

        # for i in range(match_start_idx, len(processor_exec_list)):
        #     print(i)

        # return processor_exec_list[match_start_idx]

        # is_sub_processor_flow = "." in processor_num
        # if is_sub_processor_flow:
        #     _processor_num = processor_num.split('.')[0]  # E.g. 003.001 => 003
        #     for i in range(int(_processor_num)-1, 0, -1):
        #         if f"{i:03d}" in processor_exec_output_dict:
        #             return f"{i:03d}"
        # else:
        #     for i in range(int(processor_num)-1, 0, -1):
        #         if f"{i:03d}" in processor_exec_output_dict:
        #             return f"{i:03d}"
        # return None

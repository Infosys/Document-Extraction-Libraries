# ===============================================================================================================#
# Copyright 2022 Infosys Ltd.                                                                                   #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#


import os
import json
import logging
import subprocess
import time
import uuid
import infy_fs_utils
from ..data import (ControllerRequestData,
                    ControllerResponseData, ProcessorFilterData)
from ..common.dpp_json_encoder import DppJSONEncoder
from ..common import Constants
from ..interface.i_orchestrator_cli import IOrchestratorCli


class OrchestratorCliBasic(IOrchestratorCli):
    """Orchestrator class for CLI execution"""

    __fs_handler: infy_fs_utils.interface.IFileSystemHandler = None
    __logger: logging.Logger = None

    class Model():
        """Model class (MVC model)"""
        input_config_file_path: None
        deployment_config_file_path: None
        input_config_data: None
        deployment_config_data: None

    def __init__(self, input_config_file_path: str, deployment_config_file_path: str):
        self.__fs_handler = infy_fs_utils.manager.FileSystemManager(
        ).get_fs_handler(Constants.FSH_DPP)
        if infy_fs_utils.manager.FileSystemLoggingManager().has_fs_logging_handler(Constants.FSLH_DPP):
            self.__logger = infy_fs_utils.manager.FileSystemLoggingManager(
            ).get_fs_logging_handler(Constants.FSLH_DPP).get_logger()
        else:
            self.__logger = logging.getLogger(__name__)

        model = self.Model()
        model.input_config_file_path = input_config_file_path
        model.deployment_config_file_path = deployment_config_file_path

        model.input_config_data = json.loads(self.__fs_handler.read_file(
            input_config_file_path))
        model.deployment_config_data = json.loads(self.__fs_handler.read_file(
            deployment_config_file_path))

        validation_messages = self.__validate_dpp_deployment_config(
            model.deployment_config_data)
        validation_messages += self.__validate_dpp_input_config(model.input_config_data,
                                                                model.deployment_config_data)
        if validation_messages:
            message = "Validation of DPP config file(s) failed. " + \
                ".".join(validation_messages)
            self.__logger.error(message)
            raise Exception(message)
        self.__model = model

    # ---------- Public Methods ---------

    def run_batch(self, context_data: dict = None):
        processor_exec_list = []
        processor_exec_output_dict = {}
        request_group_num = f"R-{str(uuid.uuid4())[24:]}"
        for idx, processor_dict in enumerate(self.__model.input_config_data.get('processor_list', [])):
            if processor_dict.get('enabled'):
                start_time = time.time()
                processor_name = processor_dict.get('processor_name')
                self.__logger.info(
                    "[Running] - Processor Name - %s", processor_name)
                prev_processor_output_dict = processor_exec_output_dict.get(
                    processor_exec_list[-1], {}) if processor_exec_list else {}
                processor_exec_list.append(processor_name)
                proc_deployment_data = self.__model.deployment_config_data['processors'].get(
                    processor_name)
                processor_num = "{:03d}".format(idx+1)
                request_id = f"{request_group_num}-{processor_num}"
                self.__update_proc_args(
                    processor_dict, self.__model.input_config_data, proc_deployment_data,
                    prev_processor_output_dict, request_id, context_data)
                output_variable_dict = self.__execute_processor(
                    proc_deployment_data)
                processor_exec_output_dict[processor_name] = output_variable_dict
                elapsed_time = round((time.time() - start_time)/60, 4)
                self.__logger.info(
                    "[End] - Processor Name - %s execution elapse time is %s mins", processor_name, elapsed_time)
        return processor_exec_list, processor_exec_output_dict

    # ---------- Private Methods ---------
    def __execute_processor(self, processor_dict):
        def _dict_to_cli_args(proc_args):
            args_list = []
            for k, v in proc_args.items():
                args_list.append(f'--{k} "{v}"')
            return ' '.join(args_list)

        def _get_env(env_var_dict):
            new_env = os.environ.copy()
            for key, val in env_var_dict.items():
                new_env[key] = val if val else ""
            return new_env
        new_output_variables_dict = {}
        try:
            run_command = f"cd {processor_dict['venv_script_dir']} "
            run_command += f"&& {processor_dict['venv_activate_cmd']} "
            run_command += f"&& cd {processor_dict['cli_controller_dir']} "
            run_command += f"&& python {processor_dict['cli_controller_file']} "
            run_command += _dict_to_cli_args(processor_dict['args'])
            self.__logger.info("[run cmd] - %s", run_command)
            new_env = _get_env(processor_dict.get('env', {}))
            sub_process = subprocess.Popen(run_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                           env=new_env, universal_newlines=True, shell=True)
            stdout, stderr = sub_process.communicate()
            if stderr:
                self.__logger.error(stderr)
            if "status=success" not in stdout:
                raise Exception(stderr)
            output_variables_dict = processor_dict['output']['variables']

            if output_variables_dict:
                for output_variable, processor_output_var in output_variables_dict.items():
                    # before, keyword, after
                    _, _, after_keyword = stdout.partition(
                        processor_output_var)
                    processor_out = after_keyword.replace(
                        '=', '').split('\n')[0].strip()
                    new_output_variables_dict[output_variable] = processor_out

        except Exception as ex:
            raise Exception(ex) from ex
        return new_output_variables_dict

    def __update_proc_args(self, processor_dict, proc_input_config_file_data,
                           proc_deployment_data, prev_processor_output_dict, request_id, context_data):
        def _write_to_temp_file(data, request_id):
            temp_folder_path = '/data/temp/dpp_orchestrator_cli_basic'
            self.__fs_handler.create_folders(temp_folder_path)
            json_file_path = f"{temp_folder_path}/{request_id}_dpp_controller_request.json"
            self.__logger.info("Processor input config file path - %s",
                               json_file_path)
            data_as_json_str = json.dumps(data, indent=4)
            self.__fs_handler.write_file(
                json_file_path, data_as_json_str, encoding='utf-8')
            # rel_path = json_file_path.replace(data_root_path, "")
            # return rel_path
            return json_file_path

        def _get_processor_input_config(processor_list, input_config_dict):
            found_proc = {}
            for x in processor_list:
                val = input_config_dict.get(x)
                if val:
                    found_proc[x] = val
            return found_proc

        proc_variables = proc_input_config_file_data.get('variables', {})
        # updating variable with previous processor output variable result
        proc_variables.update(prev_processor_output_dict)
        SNAPSHOT_FOLDER_PATH = '/data/temp/dpp_orchestrator_cli_basic/snapshots'
        self.__fs_handler.create_folders(SNAPSHOT_FOLDER_PATH)
        controller_request_data = ControllerRequestData(
            request_id=request_id,
            description="Auto-generated by DPP orchestrator",
            input_config_file_path=self.__model.input_config_file_path,
            processor_filter=ProcessorFilterData(
                includes=[processor_dict['processor_name']]),
            context=context_data,
            snapshot_dir_root_path=SNAPSHOT_FOLDER_PATH
        )
        dpp_controller_res_file_path = proc_variables.get(
            'DPP_CONTROLLER_RES_FILE_PATH', None)
        controller_response_data: ControllerResponseData = None
        if dpp_controller_res_file_path:
            data = json.loads(self.__fs_handler.read_file(
                dpp_controller_res_file_path))
            controller_response_data = ControllerResponseData(**data)
            controller_request_data.records = controller_response_data.records

        # Due to TypeError: Object of type ProcessorFilterData is not JSON serializable
        controller_request_data = json.loads(
            DppJSONEncoder().encode(controller_request_data))
        controller_request_file_path = _write_to_temp_file(
            dict(controller_request_data), request_id)
        proc_variables['DPP_CONTROLLER_REQ_FILE_PATH'] = controller_request_file_path

        updated_arg_dict = {}
        for k, v in proc_deployment_data.get('args', {}).items():
            if '${' in v:
                f_v = v.replace('${', '').replace('}', '')
                v = proc_variables.get(f_v.upper() if f_v else f_v)
            updated_arg_dict[k] = v
        proc_deployment_data['args'] = updated_arg_dict

        updated_arg_dict = {}
        for k, v in proc_deployment_data.get('env', {}).items():
            if '${' in v:
                f_v = v.replace('${', '').replace('}', '')
                v = proc_variables.get(f_v.upper() if f_v else f_v)
            updated_arg_dict[k] = v
        proc_deployment_data['env'] = updated_arg_dict

    def __validate_dpp_deployment_config(self, config_data):
        validation_messages = []
        VALIDATE_DEPLOYMENT_CONFIG_PATH_LIST = [
            'processor_home_dir', 'cli_controller_dir', 'venv_script_dir']
        key_missing_dict, invalid_path_dict = {}, {}
        for key, value in config_data.get('processors', {}).items():
            if not value.get('enabled'):
                continue
            for x in VALIDATE_DEPLOYMENT_CONFIG_PATH_LIST:
                if not value.get(x):
                    self.__add_or_update_dict(key_missing_dict, key, x)
                elif not os.path.exists(value.get(x)):
                    self.__add_or_update_dict(invalid_path_dict, key, x)
        if key_missing_dict:
            message = f"INVALID DEPLOYMENT CONFIG FILE: key is missing -> {key_missing_dict}"
            self.__logger.error(message)
            validation_messages.append(message)
        if invalid_path_dict:
            message = f"INVALID DEPLOYMENT CONFIG FILE: path is not valid -> {invalid_path_dict}"
            self.__logger.error(message)
            validation_messages.append(message)
        return validation_messages

    def __validate_dpp_input_config(self, input_config_data, deployment_config_data) -> []:
        validation_messages = []
        enabled_processor_list = [k for k, v in deployment_config_data.get(
            'processors', {}).items() if v.get('enabled')]
        not_enabled_processors_list = []
        for x in input_config_data.get('processor_list', []):
            if not x.get('enabled'):
                continue
            if x.get('processor_name') not in enabled_processor_list:
                not_enabled_processors_list.append(x.get('processor_name'))
        if not_enabled_processors_list:
            message = "INVALID INPUT CONFIG FILE: "
            message += f"processor(s) are not enabled in deployment config -> {not_enabled_processors_list}"
            self.__logger.error(message)
            validation_messages.append(message)
        return validation_messages

    def __add_or_update_dict(self, d, k, v):
        if k in d:
            d[k].append(v)
        else:
            d[k] = [v]
        return d

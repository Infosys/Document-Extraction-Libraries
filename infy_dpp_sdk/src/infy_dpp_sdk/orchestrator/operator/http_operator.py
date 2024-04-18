# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#


import os
import json
import logging
import requests
import infy_fs_utils
from ...data import (ControllerResponseData)
from ...common.dpp_json_encoder import DppJSONEncoder
from ...common import Constants


class HTTPOperator():
    """Operator for HTTP"""

    def __init__(self) -> None:
        self.__fs_handler = infy_fs_utils.manager.FileSystemManager(
        ).get_fs_handler(Constants.FSH_DPP)
        if infy_fs_utils.manager.FileSystemLoggingManager().has_fs_logging_handler(Constants.FSLH_DPP):
            self.__logger = infy_fs_utils.manager.FileSystemLoggingManager(
            ).get_fs_logging_handler(Constants.FSLH_DPP).get_logger()
        else:
            self.__logger = logging.getLogger(__name__)

    def execute_processor(self, processor_deployment_config_data: dict):
        """Execute a processor"""
        def __dict_to_cli_args(proc_args):
            args_list = []
            for k, v in proc_args.items():
                args_list.append(f'--{k} "{v}"')
            return ' '.join(args_list)

        def __get_env(env_var_dict):
            new_env = os.environ.copy()
            for key, val in env_var_dict.items():
                new_env[key] = val if val else ""
            return new_env

        new_output_variables_dict = {}
        try:
            api_url = processor_deployment_config_data['http_controller_base_url'] + \
                processor_deployment_config_data['http_controller_path']

            args = processor_deployment_config_data.get('args', {})
            env = processor_deployment_config_data.get('env', {})

            dpp_headers = {k.replace("_", "-"): v for k,
                           v in env.items()}
            dpp_controller_req_file_path = args.get('request_file_path', None)

            data = json.loads(self.__fs_handler.read_file(
                dpp_controller_req_file_path))
            # controller_request_data = ControllerResponseData(**data)

            # data_as_json_str = json.dumps(controller_request_data, indent=4)
            controller_response_data: ControllerResponseData = None
            response = requests.post(
                api_url, json=data, headers=dpp_headers,
                verify=False, timeout=180)
            if response.ok:
                controller_response_data = ControllerResponseData(
                    **response.json())

            dpp_controller_res_file_path = self.__create_controller_response_file(
                controller_response_data)

            output_variables_dict = processor_deployment_config_data['output']['variables']

            if output_variables_dict:
                for output_variable, _ in output_variables_dict.items():
                    new_output_variables_dict[output_variable] = dpp_controller_res_file_path

            # new_output_variables_dict['SYS_CONTROLLER_RES_FILE_PATH'] = controller_response_data

            # return controller_response_data, {}

            # run_command = f"cd {processor_deployment_config_data['venv_script_dir']} "
            # run_command += f"&& {processor_deployment_config_data['venv_activate_cmd']} "
            # run_command += f"&& cd {processor_deployment_config_data['cli_controller_dir']} "
            # run_command += f"&& python {processor_deployment_config_data['cli_controller_file']} "
            # run_command += __dict_to_cli_args(
            #     processor_deployment_config_data['args'])
            # self.__logger.info("[run cmd] - %s", run_command)
            # new_env = __get_env(
            #     processor_deployment_config_data.get('env', {}))
            # sub_process = subprocess.Popen(run_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            #                                env=new_env, universal_newlines=True, shell=True)
            # stdout, stderr = sub_process.communicate()
            # if stderr:
            #     self.__logger.error(stderr)
            # if "status=success" not in stdout:
            #     raise Exception(stderr)
            # output_variables_dict = processor_deployment_config_data['output']['variables']

            # if output_variables_dict:
            #     for output_variable, processor_output_var in output_variables_dict.items():
            #         # before, keyword, after
            #         _, _, after_keyword = stdout.partition(
            #             processor_output_var)
            #         processor_out = after_keyword.replace(
            #             '=', '').split('\n')[0].strip()
            #         new_output_variables_dict[output_variable] = processor_out

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

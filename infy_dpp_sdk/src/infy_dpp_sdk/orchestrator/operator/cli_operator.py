# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#


import os
import subprocess
import logging
import infy_fs_utils
from ...common import Constants


class CLIOperator():
    """Operator for CLI"""

    def __init__(self) -> None:
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
            run_command = f"cd {processor_deployment_config_data['venv_script_dir']} "
            run_command += f"&& {processor_deployment_config_data['venv_activate_cmd']} "
            run_command += f"&& cd {processor_deployment_config_data['cli_controller_dir']} "
            run_command += f"&& python {processor_deployment_config_data['cli_controller_file']} "
            run_command += __dict_to_cli_args(
                processor_deployment_config_data['args'])
            self.__logger.info("[run cmd] - %s", run_command)
            new_env = __get_env(
                processor_deployment_config_data.get('env', {}))
            sub_process = subprocess.Popen(run_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                           env=new_env, universal_newlines=True, shell=True)
            stdout, stderr = sub_process.communicate()
            if stderr:
                self.__logger.error(stderr)
            if "status=success" not in stdout:
                raise Exception(stderr)
            output_variables_dict = processor_deployment_config_data['output']['variables']

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

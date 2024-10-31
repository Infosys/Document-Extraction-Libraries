# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import os
import infy_dpp_sdk
import infy_fs_utils
# import logging
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
# NOTE: This application should not be run directly. Instead, run the following test module:
# libraries\infy_dpp_sdk\tests\test_orchestrator_cli_external.py


class App():
    LOG_LEVELS = {
        "NOTSET": 0,
        "DEBUG": 10,
        "INFO": 20,
        "WARN": 30,
        "ERROR": 40,
        "CRITICAL": 50
    }

    def __init__(self) -> None:
        pass

    def do_processing(self):
        # NOTE: The environment variables will be passed by the DPP orchestrator
        # It's pre-requisite for running any DPP pipeline

        # Uncomment for unit testing locally
        # for k, v in os.environ.items():
        #     print(k, v)
        log_level_int = 40
        log_level_str = os.environ.get('LOG_LEVEL', '').upper()
        if log_level_str in self.LOG_LEVELS:
            log_level_int = self.LOG_LEVELS[log_level_str]
        storage_config_data = infy_fs_utils.data.StorageConfigData(
            **{
                "storage_root_uri": os.environ.get('DPP_STORAGE_ROOT_URI'),
                "storage_server_url": os.environ.get('DPP_STORAGE_SERVER_URL'),
                "storage_access_key": os.environ.get('DPP_STORAGE_ACCESS_KEY'),
                "storage_secret_key": os.environ.get('DPP_STORAGE_SECRET_KEY'),
            })
        file_sys_handler = infy_fs_utils.provider.FileSystemHandler(
            storage_config_data)
        if not infy_fs_utils.manager.FileSystemManager().has_fs_handler(infy_dpp_sdk.common.Constants.FSH_DPP):
            infy_fs_utils.manager.FileSystemManager().add_fs_handler(
                file_sys_handler,
                infy_dpp_sdk.common.Constants.FSH_DPP)

        # Modify as required to control the overall logging level
        # logging.basicConfig(level=logging.ERROR)
        # Configure client properties
        try:
            # Get the current working directory
            cwd = Path.cwd()
            # Check if the system is Windows
            if os.name == 'nt':
                # Get the drive from the current working directory
                root_dir = cwd.drive + '\\tmp\\dpp_processor_container'
                if not os.path.exists(root_dir):
                    os.makedirs(root_dir)
            else:
                # root dir for docker container
                # Get the root directory
                root_dir = cwd.root
            print("root_dir:", root_dir)
            # For VM9 testing uncomment below line
            # root_dir = '/tmp/dpp_processor_container' #os.environ.get('CONTAINER_ROOT_PATH')
            client_config_data = infy_dpp_sdk.ClientConfigData(
                **{
                    "container_data": {
                        # os.environ.get('CONTAINER_ROOT_PATH'),
                        "container_root_path": root_dir+"/temp/infy_dpp_processor/CONTAINER"
                    }
                })
            infy_dpp_sdk.ClientConfigManager().load(client_config_data)
        except Exception as e:
            print(f"Error: {e}")
        logging_config_data = infy_fs_utils.data.LoggingConfigData(
            **{
                # "logger_group_name": "my_group_1",
                "logging_level": log_level_int,
                "logging_format": "",
                "logging_timestamp_format": "",
                "log_file_data": {
                    "log_file_dir_path": "/logs",
                    "log_file_name_prefix": os.environ.get('LOG_FILE_NAME'),
                    # "log_file_name_prefix":os.environ.get('LOG_FILE_NAME'),
                    # TODO:time stamp having date  in suffix/ keep env varaible
                    "log_file_name_suffix": "",
                    "log_file_extension": ".log"

                }})
        if not infy_fs_utils.manager.FileSystemLoggingManager().has_fs_logging_handler(
                infy_dpp_sdk.common.Constants.FSLH_DPP):
            infy_fs_utils.manager.FileSystemLoggingManager().add_fs_logging_handler(
                infy_fs_utils.provider.FileSystemLoggingHandler(
                    logging_config_data, file_sys_handler),
                infy_dpp_sdk.common.Constants.FSLH_DPP)

        controller_cli = infy_dpp_sdk.controller.ControllerCLI()
        controller_request_data: infy_dpp_sdk.data.ControllerRequestData = controller_cli.receive_request(
            internal_orchestrator=False)
        controller_response_data: infy_dpp_sdk.data.ControllerResponseData = controller_cli.do_execute_batch(
            controller_request_data)
        response_file_path = controller_cli.send_response(
            controller_response_data)
        # ---START---#
        try:
            #     # Get the current working directory
            #     cwd = Path.cwd()
            #     # Check if the system is Windows
            #     if os.name == 'nt':
            #         # Get the drive from the current working directory
            #         root_dir = cwd.drive + '\\'
            #     else:
            #         # Get the root directory
            #         root_dir = cwd.root
            #         print("root_dir", root_dir)

            # For VM9 testing uncomment below line
            # root_dir = os.environ.get('CONTAINER_ROOT_PATH')
            node_output_file_path = f'{root_dir}/processor_output.txt'
            with open(node_output_file_path, 'w', encoding='utf8') as file:
                file.write(response_file_path)
        except Exception as e:
            print(f"Error: {e}")
        # ---END---#
        return response_file_path


if __name__ == '__main__':
    status = 1  # Not successful
    response_file_path = App().do_processing()
    if response_file_path:
        status = 0  # Successful
    exit(status)

# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import os
import infy_dpp_sdk
import infy_fs_utils

# NOTE: This application should not be run directly. Instead, run the following test module:
# libraries\infy_dpp_sdk\tests\test_orchestrator_cli.py


class App():
    def __init__(self) -> None:
        pass

    def do_processing(self):
        # NOTE: The environment variables will be passed by the DPP orchestrator
        # It's pre-requisite for running any DPP pipeline

        # Uncomment for unit testing locally
        # for k, v in os.environ.items():
        #     print(k, v)

        storage_config_data = infy_fs_utils.data.StorageConfigData(
            **{
                "storage_root_uri": os.environ.get('DPP_STORAGE_ROOT_URI'),
                "storage_server_url": os.environ.get('DPP_STORAGE_SERVER_URL'),
                "storage_access_key": os.environ.get('DPP_STORAGE_ACCESS_KEY'),
                "storage_secret_key": os.environ.get('DPP_STORAGE_SECRET_KEY'),
            })

        if not infy_fs_utils.manager.FileSystemManager().has_fs_handler(infy_dpp_sdk.common.Constants.FSH_DPP):
            infy_fs_utils.manager.FileSystemManager().add_fs_handler(
                infy_fs_utils.provider.FileSystemHandler(storage_config_data),
                infy_dpp_sdk.common.Constants.FSH_DPP)

        controller_cli = infy_dpp_sdk.controller.ControllerCLI()
        controller_request_data: infy_dpp_sdk.data.ControllerRequestData = controller_cli.receive_request()
        controller_response_data: infy_dpp_sdk.data.ControllerResponseData = controller_cli.do_execute_batch(
            controller_request_data)
        response_file_path = controller_cli.send_response(
            controller_response_data)
        return response_file_path


if __name__ == '__main__':
    status = 1  # Not successful
    response_file_path = App().do_processing()
    if response_file_path:
        status = 0  # Successful
    exit(status)

# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import os
import json
import sys
import pytest
import infy_fs_utils
import infy_dpp_sdk

STORAGE_ROOT_PATH = f"C:/temp/unittest/infy_dpp_sdk/{__name__}/STORAGE"
REQUEST_FILE_PATH = "/data/work/R-f2594a38b532-dpp_controller_request.json"
REQUEST_FILE_PATH_2 = "/data/work/R-54a9450fe33b-dpp_controller_request.json"


@pytest.fixture(scope='module', autouse=True)
def pre_test(create_root_folders, copy_files_to_root_folder):
    """Test pre-run method"""
    # Create data folders
    create_root_folders([STORAGE_ROOT_PATH])
    # Copy files to pick up folder
    SAMPLE_ROOT_PATH = "./data/sample"
    FILES_TO_COPY = [
        ['company1.txt', f"{SAMPLE_ROOT_PATH}/input",
            f"{STORAGE_ROOT_PATH}/data/input"],
        ['company2.txt', f"{SAMPLE_ROOT_PATH}/input",
            f"{STORAGE_ROOT_PATH}/data/input"],
        ['dpp_pipeline1_input_config.json', f"{SAMPLE_ROOT_PATH}/config",
            f"{STORAGE_ROOT_PATH}/data/config"],
        ['dpp_pipeline2_input_config.json', f"{SAMPLE_ROOT_PATH}/config",
            f"{STORAGE_ROOT_PATH}/data/config"],
        ['R-f2594a38b532-dpp_controller_request.json', f"{SAMPLE_ROOT_PATH}/work",
            f"{STORAGE_ROOT_PATH}/data/work"],
        ['R-54a9450fe33b-dpp_controller_request.json', f"{SAMPLE_ROOT_PATH}/work",
            f"{STORAGE_ROOT_PATH}/data/work"],
    ]
    copy_files_to_root_folder(FILES_TO_COPY)

    storage_config_data = infy_fs_utils.data.StorageConfigData(
        **{
            "storage_root_uri": f"file://{STORAGE_ROOT_PATH}",
            "storage_server_url": "",
            "storage_access_key": "",
            "storage_secret_key": ""
        })
    file_sys_handler = infy_fs_utils.provider.FileSystemHandler(
        storage_config_data)
    infy_fs_utils.manager.FileSystemManager().set_root_handler_name(
        infy_dpp_sdk.common.Constants.FSH_DPP)
    infy_fs_utils.manager.FileSystemManager().add_fs_handler(file_sys_handler)

    logging_config_data = infy_fs_utils.data.LoggingConfigData(
        **{
            # "logger_group_name": "my_group_1",
            "logging_level": 10,
            "logging_format": "",
            "logging_timestamp_format": "",
            "log_file_data": {
                "log_file_dir_path": "/logs",
                "log_file_name_prefix": "infy_dpp_sdk",
                # "log_file_name_suffix": "1",
                "log_file_extension": ".log"

            }})
    file_sys_logging_handler = infy_fs_utils.provider.FileSystemLoggingHandler(
        logging_config_data, file_sys_handler)
    infy_fs_utils.manager.FileSystemLoggingManager(
    ).set_root_handler_name(infy_dpp_sdk.common.Constants.FSLH_DPP)
    infy_fs_utils.manager.FileSystemLoggingManager(
    ).add_fs_logging_handler(file_sys_logging_handler)

    yield  # Run all test methods
    # Post run cleanup
    # Delete file system handler so that other test modules don't get duplicate key error
    infy_fs_utils.manager.FileSystemManager().delete_fs_handler()
    infy_fs_utils.manager.FileSystemLoggingManager().delete_fs_logging_handler()


def test_controller_1():
    """Test method to check normal scenario"""
    # Create command line arguments
    sys.argv = ['<leave empty>', '--request_file_path', REQUEST_FILE_PATH]
    controller_cli = infy_dpp_sdk.controller.ControllerCLI()
    controller_request_data: infy_dpp_sdk.data.ControllerRequestData = controller_cli.receive_request()
    controller_response_data: infy_dpp_sdk.data.ControllerResponseData = controller_cli.do_execute_batch(
        controller_request_data)
    response_file_path = controller_cli.send_response(controller_response_data)

    assert os.path.exists(f"{STORAGE_ROOT_PATH}{response_file_path}")


def test_controller_2():
    """Test method to check scenario where initial context data is provided by client"""
    # Create command line arguments
    sys.argv = ['<leave empty>', '--request_file_path', REQUEST_FILE_PATH_2]
    controller_cli = infy_dpp_sdk.controller.ControllerCLI()
    controller_request_data: infy_dpp_sdk.data.ControllerRequestData = controller_cli.receive_request()
    controller_response_data: infy_dpp_sdk.data.ControllerResponseData = controller_cli.do_execute_batch(
        controller_request_data)

    def __test_context_data():
        # Verify that context data provided in dpp_controller_request file is reflected in context data
        # It should be the first key in context data
        context_data_file_path_1 = controller_response_data.snapshot_dir_root_path + "/" + \
            controller_response_data.records[1].snapshot.context_data_file_path
        context_data_file_path_1 = f"{STORAGE_ROOT_PATH}{context_data_file_path_1}"
        context_data = __get_json_data(context_data_file_path_1)
        assert list(context_data.keys())[0] == 'Preprocessor'

    __test_context_data()

    response_file_path = controller_cli.send_response(controller_response_data)

    assert os.path.exists(f"{STORAGE_ROOT_PATH}{response_file_path}")


# ############# PRIVATE FUNCTIONS ############# #

def __get_json_data(file_path):
    """Get json data from file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

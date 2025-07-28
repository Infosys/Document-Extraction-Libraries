# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#


import sys
import os
import pytest
from app_dpp_container import App

STORAGE_ROOT_PATH = f"C:/temp/unittest/my_dummy_processor_app/{__name__}/STORAGE"
INPUT_CONFIG_FILE_PATH = '/data/config/dpp_pipeline2_input_config.json'
REQUEST_FILE_PATH = "/data/temp/work/dpp_orchestrator/R-123456789012-001_dpp_controller_request.json"


@pytest.fixture(scope='module', autouse=True)
def pre_test(create_root_folders, copy_files_to_root_folder):
    """Test pre-run method"""
    # Create data folders
    create_root_folders([STORAGE_ROOT_PATH])
    # Copy files to pick up folder
    SAMPLE_ROOT_PATH = "./data/sample"
    FILES_TO_COPY = [
        [os.path.basename(INPUT_CONFIG_FILE_PATH), f"{SAMPLE_ROOT_PATH}/config",
            f"{STORAGE_ROOT_PATH}/data/config"],
        [os.path.basename(REQUEST_FILE_PATH), f"{SAMPLE_ROOT_PATH}",
            f"{STORAGE_ROOT_PATH}/data/temp/work/dpp_orchestrator"]
    ]
    copy_files_to_root_folder(FILES_TO_COPY)


def test_app_dpp_container_partial_pipeline():
    """Test case for app_dpp_container to execute first processor of pipeline"""

    # NOTE: To generate the test data, run the following test module:
    # libraries\infy_dpp_sdk\tests\test_orchestrator_cli_basic.py

    os.environ['DPP_STORAGE_ROOT_URI'] = f"file://{STORAGE_ROOT_PATH}"

    cli_args = ['--request_file_path', REQUEST_FILE_PATH]
    sys.argv.extend(cli_args)

    response_file_path = App().do_processing()
    assert response_file_path is not None

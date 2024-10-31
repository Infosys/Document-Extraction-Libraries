# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#
import pytest
import json
import infy_fs_utils
import infy_dpp_sdk

STORAGE_ROOT_PATH = f"C:/temp/unittest/infy_dpp_ai/{__name__}/STORAGE"
CONTAINER_ROOT_PATH = f"C:/temp/unittest/infy_dpp_ai/{__name__}/CONTAINER"


@pytest.fixture(scope='module', autouse=True)
def pre_test(create_root_folders, copy_files_to_root_folder):
    """Initialization method"""
    # Create data folders
    create_root_folders([STORAGE_ROOT_PATH, CONTAINER_ROOT_PATH])
    # Copy files to pick up folder
    SAMPLE_ROOT_PATH = "./data/sample"
    FILES_TO_COPY = [
        ['centralised_indexer_input_config.json', f"{SAMPLE_ROOT_PATH}/data/config",
            f"{STORAGE_ROOT_PATH}/data/config"],
        ['processor_response_data.json', f"{SAMPLE_ROOT_PATH}/data/work/D-5a449ddc-2b56-4766-b346-1f9f1e6cd31f/page-14-17.pdf_files",
            f"{STORAGE_ROOT_PATH}/data/work/D-5a449ddc-2b56-4766-b346-1f9f1e6cd31f/page-14-17.pdf_files"],
        ['*txt', f"{SAMPLE_ROOT_PATH}/data/vectordb/chunked/5a449ddc-2b56-4766-b346-1f9f1e6cd31f/chunks",
            f"{STORAGE_ROOT_PATH}/data/vectordb/chunked/5a449ddc-2b56-4766-b346-1f9f1e6cd31f/chunks"],
        ['*json', f"{SAMPLE_ROOT_PATH}/data/vectordb/chunked/5a449ddc-2b56-4766-b346-1f9f1e6cd31f/chunks",
            f"{STORAGE_ROOT_PATH}/data/vectordb/chunked/5a449ddc-2b56-4766-b346-1f9f1e6cd31f/chunks"],
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
    infy_fs_utils.manager.FileSystemManager().add_fs_handler(
        file_sys_handler,
        infy_dpp_sdk.common.Constants.FSH_DPP)

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
    infy_fs_utils.manager.FileSystemLoggingManager().add_fs_logging_handler(
        infy_fs_utils.provider.FileSystemLoggingHandler(
            logging_config_data, file_sys_handler),
        infy_dpp_sdk.common.Constants.FSLH_DPP)

    # Configure client properties
    client_config_data = infy_dpp_sdk.ClientConfigData(
        **{
            "container_data": {
                "container_root_path": f"{CONTAINER_ROOT_PATH}",
            }
        })
    infy_dpp_sdk.ClientConfigManager().load(client_config_data)

    yield  # Run all test methods
    # Post run cleanup
    # Delete file system handler so that other test modules don't get duplicate key error
    infy_fs_utils.manager.FileSystemManager().delete_fs_handler(
        infy_dpp_sdk.common.Constants.FSH_DPP)
    infy_fs_utils.manager.FileSystemLoggingManager().delete_fs_logging_handler(
        infy_dpp_sdk.common.Constants.FSLH_DPP)


def test_dpp_centralised_index_creation():
    """
        Test case for dpp_ai
    """
    PROCESSOR_INPUT_CONFIG_PATH = '/data/config/centralised_indexer_input_config.json'
    file_sys_handler = infy_fs_utils.manager.FileSystemManager(
    ).get_fs_handler(infy_dpp_sdk.common.Constants.FSH_DPP)
    processor_response_data = json.loads(file_sys_handler.read_file
                                         ("/data/work/D-5a449ddc-2b56-4766-b346-1f9f1e6cd31f/page-14-17.pdf_files/processor_response_data.json"))
    dpp_orchestrator = infy_dpp_sdk.orchestrator.OrchestratorNativeBasic(
        input_config_file_path=PROCESSOR_INPUT_CONFIG_PATH)
    response_data_list = dpp_orchestrator.run_batch(
        [infy_dpp_sdk.data.DocumentData(
            **processor_response_data.get('document_data'))],
        [processor_response_data.get('context_data')])

    assert response_data_list[0].context_data.get('db_indexer') is not None

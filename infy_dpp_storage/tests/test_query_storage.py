# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#
import pytest
import json
import infy_dpp_sdk
import infy_fs_utils

STORAGE_ROOT_PATH = f"C:/temp/unittest/infy_dpp_storage/{__name__}/STORAGE"
CONTAINER_ROOT_PATH = f"C:/temp/unittest/infy_dpp_storage/{__name__}/CONTAINER"
PROCESSOR_INPUT_CONFIG_PATH =f"/data/config/dpp_pipeline_storage_input_config.json"

@pytest.fixture(scope='module', autouse=True)
def pre_test(create_root_folders, copy_files_to_root_folder):
    """Initialization method"""
    create_root_folders([STORAGE_ROOT_PATH, CONTAINER_ROOT_PATH])
    SAMPLE_ROOT_PATH = "./data/sample"
    FILES_TO_COPY = [
        ['sample_data.txt', f"{SAMPLE_ROOT_PATH}/input",
            f"{STORAGE_ROOT_PATH}/data/input"],
        ['dpp_pipeline_storage_input_config.json', f"{SAMPLE_ROOT_PATH}/config",
            f"{STORAGE_ROOT_PATH}/data/config"],
        ['books_schema.json', f"{SAMPLE_ROOT_PATH}/config/schema",
        f"{STORAGE_ROOT_PATH}/data/config/schema"],
        ['document_data.json', f"{SAMPLE_ROOT_PATH}/work/D-bf978e1a-75a1-42f3-9d94-a2f6cbad2d97/sample_data.txt_files",
        f"{STORAGE_ROOT_PATH}/data/work/D-bf978e1a-75a1-42f3-9d94-a2f6cbad2d97/sample_data.txt_files"],
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
        file_sys_handler,infy_dpp_sdk.common.Constants.FSH_DPP)   
    
    
    logging_config_data = infy_fs_utils.data.LoggingConfigData(
        **{
            "logging_level": 10,
            "logging_format": "",
            "logging_timestamp_format": "",
            "log_file_data": {
                "log_file_dir_path": "/logs",
                "log_file_name_prefix": "infy_dpp_sdk",                
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

def test_query_storage():
    """
        Test case for query creation and execution
    """
    file_sys_handler = infy_fs_utils.manager.FileSystemManager().get_fs_handler(infy_dpp_sdk.common.Constants.FSH_DPP)
    document_data_json =json.loads(file_sys_handler.read_file
                                   ("/data/work/D-bf978e1a-75a1-42f3-9d94-a2f6cbad2d97/sample_data.txt_files/document_data.json"))
    # --------- Run the pipeline ------------    
    dpp_orchestrator = infy_dpp_sdk.orchestrator.OrchestratorNativeBasic(
        input_config_file_path=PROCESSOR_INPUT_CONFIG_PATH)    
    response_data_list = dpp_orchestrator.run_batch(
        [infy_dpp_sdk.data.DocumentData(**document_data_json.get('document_data'))],
        [document_data_json.get('context_data')])   
    # --------- Save the response data to temp file ------------#
    for response_data in response_data_list:
        output_file_path="/data/work/D-bf978e1a-75a1-42f3-9d94-a2f6cbad2d97/sample_data.txt_files/processor_response_data.json"
        file_sys_handler.write_file(output_file_path, json.dumps(response_data.dict(),indent=4))
        assert response_data.context_data.get('db_query_executor') is not None



# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                   #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#
import pytest
import json
import infy_dpp_sdk
import infy_dpp_ai
import infy_fs_utils
STORAGE_ROOT_PATH = f"C:/temp/unittest/infy_dpp_ai/{__name__}/STORAGE"
CONTAINER_ROOT_PATH = f"C:/temp/unittest/infy_dpp_ai/{__name__}/CONTAINER"
PROCESSOR_INPUT_CONFIG_PATH =f"/data/config/inference_batch_input_config_data.json"



@pytest.fixture(scope='module', autouse=True)
def pre_test(create_root_folders, copy_files_to_root_folder):
    """Initialization method"""
    create_root_folders([STORAGE_ROOT_PATH, CONTAINER_ROOT_PATH])
    SAMPLE_ROOT_PATH = "./data/sample"
    FILES_TO_COPY = [
        ['document_data.json', f"C:/Temp/unittest/infy_dpp_ai/tests.test_data_encoder/STORAGE/data/work/D-037c85b3-d45b-47db-abb0-b7aadf813b4e/page-14-17.pdf_files",
            f"{STORAGE_ROOT_PATH}/data/work/D-037c85b3-d45b-47db-abb0-b7aadf813b4e/page-14-17.pdf_files"],
        ['inference_batch_input_config_data.json', f"{SAMPLE_ROOT_PATH}/data/config",
            f"{STORAGE_ROOT_PATH}/data/config"],
        ['extractor_attribute_prompt_2.txt',f"{SAMPLE_ROOT_PATH}/data/config/prompt_templates",
            f"{STORAGE_ROOT_PATH}/data/config/prompt_templates"],
        ['*.txt',f"{SAMPLE_ROOT_PATH}/vectordb/chunked",
            f"{STORAGE_ROOT_PATH}/vectordb/chunked"],
        ['*.json',f"{SAMPLE_ROOT_PATH}/vectordb/chunked",
            f"{STORAGE_ROOT_PATH}/vectordb/chunked"],
        ['*.pkl',f"C:/Temp/unittest/infy_dpp_ai/tests.test_data_encoder/STORAGE/vectordb/encoded", f"{STORAGE_ROOT_PATH}/vectordb/encoded"],
        ['*.faiss',f"C:/Temp/unittest/infy_dpp_ai/tests.test_data_encoder/STORAGE/vectordb/encoded", f"{STORAGE_ROOT_PATH}/vectordb/encoded"],
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

def test_reader_pipeline_1():
    """
        Test case for segmentation_pipeline
    """
    file_sys_handler = infy_fs_utils.manager.FileSystemManager().get_fs_handler(infy_dpp_sdk.common.Constants.FSH_DPP)
    document_data_json =json.loads(file_sys_handler.read_file
                                   ("/data/work/D-037c85b3-d45b-47db-abb0-b7aadf813b4e/page-14-17.pdf_files/document_data.json"))
    # --------- Run the pipeline ------------    
    dpp_orchestrator = infy_dpp_sdk.orchestrator.OrchestratorNativeBasic(
        input_config_file_path=PROCESSOR_INPUT_CONFIG_PATH)    
    response_data_list = dpp_orchestrator.run_batch(
        [infy_dpp_sdk.data.DocumentData(**document_data_json.get('document_data'))],
        [document_data_json.get('context_data')])   
    # --------- Save the response data to temp file ------------#
    for response_data in response_data_list:
        output_file_path="/data/work/D-037c85b3-d45b-47db-abb0-b7aadf813b4e/page-14-17.pdf_files/processor_response_data.json"
        file_sys_handler.write_file(output_file_path, json.dumps(response_data.dict(),indent=4))
        assert response_data.context_data.get('query_retriever').get('queries')  is not None



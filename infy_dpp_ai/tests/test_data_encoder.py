# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                   #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#
import pytest
import infy_dpp_sdk
import infy_dpp_ai
import infy_fs_utils


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
        ['document_data.json', f"{SAMPLE_ROOT_PATH}/data/work/D-037c85b3-d45b-47db-abb0-b7aadf813b4e/page-14-17.pdf_files",
            f"{STORAGE_ROOT_PATH}/data/work/D-037c85b3-d45b-47db-abb0-b7aadf813b4e/page-14-17.pdf_files"],
        ['pipeline_input_config_data.json', f"{SAMPLE_ROOT_PATH}/data/config",
            f"{STORAGE_ROOT_PATH}/data/config"],        
        ['*.txt',f"{SAMPLE_ROOT_PATH}/vectordb/chunked",
            f"{STORAGE_ROOT_PATH}/vectordb/chunked"],
        ['*.json',f"{SAMPLE_ROOT_PATH}/vectordb/chunked",
            f"{STORAGE_ROOT_PATH}/vectordb/chunked"]
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
 

def test_dpp_ai_pipeline_1():
    """
        Test case for segmentation_pipeline
    """
    document_data_json = infy_dpp_ai.common.FileUtil.load_json(
        f"{STORAGE_ROOT_PATH}/data/work/D-037c85b3-d45b-47db-abb0-b7aadf813b4e/page-14-17.pdf_files/document_data.json")

    # --------- Run the pipeline ------------
    dpp_orchestrator = infy_dpp_sdk.orchestrator.OrchestratorNativeBasic(
        input_config_file_path=f"/data/config/pipeline_input_config_data.json")    
    response_data_list = dpp_orchestrator.run_batch(
        [infy_dpp_sdk.data.DocumentData(**document_data_json.get('document_data'))],
        [document_data_json.get('context_data')])   
    # --------- Save the response data to temp file ------------
    for idx,response_data in enumerate(response_data_list):
        output_file_path=f"{STORAGE_ROOT_PATH}/data/work/D-037c85b3-d45b-47db-abb0-b7aadf813b4e/page-14-17.pdf_files/document_data.json"
        infy_dpp_ai.common.FileUtil.save_to_json(output_file_path,response_data.dict())
        assert response_data.context_data.get('data_encoder') is not None

def test_dpp_ai_pipeline_2():
    """
        Test case for data encoding 2 file in same vector db if "db_name" key is in faiss configuration
    """
    for i in (1,2):
        document_data_json = infy_dpp_ai.common.FileUtil.load_json(
            f"{STORAGE_ROOT_PATH}/data/work/D-037c85b3-d45b-47db-abb0-b7aadf813b4e/page-14-17.pdf_files/document_data.json")
        # --------- Run the pipeline ------------
        dpp_orchestrator = infy_dpp_sdk.orchestrator.OrchestratorNativeBasic(
            input_config_file_path=f"/data/config/pipeline_input_config_data.json")    
        response_data_list = dpp_orchestrator.run_batch(
            [infy_dpp_sdk.data.DocumentData(**document_data_json.get('document_data'))],
            [document_data_json.get('context_data')])   
    # --------- Save the response data to temp file ------------
    for idx,response_data in enumerate(response_data_list):
        output_file_path=f"{STORAGE_ROOT_PATH}/data/work/D-037c85b3-d45b-47db-abb0-b7aadf813b4e/page-14-17.pdf_files/document_data.json"
        infy_dpp_ai.common.FileUtil.save_to_json(output_file_path,response_data.dict())
        assert response_data.context_data.get('data_encoder') is not None

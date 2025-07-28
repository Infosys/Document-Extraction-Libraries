# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#
import json
import pytest
import infy_dpp_sdk
import infy_fs_utils

STORAGE_ROOT_PATH = f"C:/temp/unittest/infy_dpp_storage/{__name__}/STORAGE"
CONTAINER_ROOT_PATH = f"C:/temp/unittest/infy_dpp_storage/{__name__}/CONTAINER"


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
        ['dpp_pipeline_inference_input_config.json', f"{SAMPLE_ROOT_PATH}/config",
            f"{STORAGE_ROOT_PATH}/data/config"],
        ['books_schema.json', f"{SAMPLE_ROOT_PATH}/config/schema",
         f"{STORAGE_ROOT_PATH}/data/config/schema"],
        ['*.txt', f"{SAMPLE_ROOT_PATH}/config/prompt_templates",
         f"{STORAGE_ROOT_PATH}/data/config/prompt_templates"],
        ['*.*', f"{SAMPLE_ROOT_PATH}/vectordb/encoded",
            f"{STORAGE_ROOT_PATH}/data/vectordb/encoded"],
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
    infy_fs_utils.manager.FileSystemManager().delete_fs_handler()
    infy_fs_utils.manager.FileSystemLoggingManager().delete_fs_logging_handler()


def test_dpp_storage_with_inference_call():
    """
        Test case for dpp_storage with inference call
    """
    inference_response_data_list = __inference_call()
    PROCESSOR_INPUT_CONFIG_PATH = '/data/config/dpp_pipeline_storage_input_config.json'
    response_data = infy_dpp_sdk.data.ProcessorResponseData(
        document_data=inference_response_data_list[0].document_data,
        context_data=inference_response_data_list[0].context_data)
    document_data_json = json.loads(response_data.model_dump_json(indent=4))
    dpp_orchestrator = infy_dpp_sdk.orchestrator.OrchestratorNativeBasic(
        input_config_file_path=PROCESSOR_INPUT_CONFIG_PATH)
    response_data_list = dpp_orchestrator.run_batch(
        [infy_dpp_sdk.data.DocumentData(
            **document_data_json.get('document_data'))],
        [document_data_json.get('context_data')])

    assert response_data_list[0].context_data.get(
        'db_query_generator') is not None
    assert response_data_list[0].context_data.get(
        'db_query_executor') is not None


def __inference_call():

    PROCESSOR_INPUT_CONFIG_PATH = '/data/config/dpp_pipeline_inference_input_config.json'
    # ---- Create response data -----
    metadata = infy_dpp_sdk.data.MetaData(
        standard_data=infy_dpp_sdk.data.StandardData(
            filepath=infy_dpp_sdk.data.ValueData()))
    document_data = infy_dpp_sdk.data.DocumentData(metadata=metadata)
    context_data = {}
    response_data = infy_dpp_sdk.data.ProcessorResponseData(
        document_data=document_data, context_data=context_data)
    document_data_json = json.loads(response_data.model_dump_json(indent=4))
    # --------- Run the pipeline ------------
    dpp_orchestrator = infy_dpp_sdk.orchestrator.OrchestratorNativeBasic(
        input_config_file_path=PROCESSOR_INPUT_CONFIG_PATH)
    response_data_list = dpp_orchestrator.run_batch(
        [infy_dpp_sdk.data.DocumentData(
            **document_data_json.get('document_data'))],
        [document_data_json.get('context_data')])

    return response_data_list

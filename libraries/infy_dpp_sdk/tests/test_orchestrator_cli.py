# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import os
import pytest
import infy_fs_utils
import infy_dpp_sdk

STORAGE_ROOT_PATH = f"C:/temp/unittest/infy_dpp_sdk/{__name__}/STORAGE"
CONTAINER_ROOT_PATH = f"C:/temp/unittest/infy_dpp_sdk/{__name__}/CONTAINER"
SERIAL_FLOW_INPUT_CONFIG_FILE_PATH = '/data/config/dpp_pipeline2_input_config.json'
PARALLEL_FLOW_INPUT_CONFIG_FILE_PATH = '/data/config/dpp_pipeline2p_input_config.json'
DEPLOYMENT_CONFIG_FILE_PATH = '/data/config/dpp_deployment_config.json'


@pytest.fixture(scope='module', autouse=True)
def pre_test(create_root_folders, copy_files_to_root_folder):
    """Test pre-run method"""
    # Create data folders
    create_root_folders([STORAGE_ROOT_PATH, CONTAINER_ROOT_PATH])
    # Copy files to pick up folder
    # Deployment config file is owned by a separate application
    SAMPLE_ROOT_PATH = os.path.abspath("./my_dummy_processor_app")
    FILES_TO_COPY = [
        ['dpp_deployment_config.json', f"{SAMPLE_ROOT_PATH}/config",
            f"{CONTAINER_ROOT_PATH}/data/config"]
    ]
    copy_files_to_root_folder(FILES_TO_COPY)
    SAMPLE_ROOT_PATH = "./data/sample"
    FILES_TO_COPY = [
        ['company1.txt', f"{SAMPLE_ROOT_PATH}/input",
            f"{STORAGE_ROOT_PATH}/data/input"],
        ['company2.txt', f"{SAMPLE_ROOT_PATH}/input",
            f"{STORAGE_ROOT_PATH}/data/input"],
        [os.path.basename(SERIAL_FLOW_INPUT_CONFIG_FILE_PATH), f"{SAMPLE_ROOT_PATH}/config",
            f"{STORAGE_ROOT_PATH}/data/config"],
        [os.path.basename(PARALLEL_FLOW_INPUT_CONFIG_FILE_PATH), f"{SAMPLE_ROOT_PATH}/config",
            f"{STORAGE_ROOT_PATH}/data/config"]
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


def test_pipeline_serial_1():
    """Test method for normal scenario"""
    abs_deployment_config_file_path = f"{CONTAINER_ROOT_PATH}{DEPLOYMENT_CONFIG_FILE_PATH}"
    dpp_orchestrator = infy_dpp_sdk.orchestrator.OrchestratorCLI(
        input_config_file_path=SERIAL_FLOW_INPUT_CONFIG_FILE_PATH,
        deployment_config_file_path=abs_deployment_config_file_path)

    processor_response_data_list = dpp_orchestrator.run_batch()
    processor_exec_list, processor_exec_output_dict = dpp_orchestrator.get_run_batch_summary()

    # Verify processor_response_data_list
    assert len(processor_response_data_list) == 2
    document_id_list = [x.dict()['document_data']['document_id']
                        for x in processor_response_data_list]
    assert len(set(document_id_list)) == 2
    message_data_list = [x.dict()['message_data']
                         for x in processor_response_data_list]
    assert len(message_data_list) == 2
    for message_data in message_data_list:
        assert len(message_data['messages']) == 1
        assert message_data['messages'][0]['message_type'] == infy_dpp_sdk.data.MessageTypeEnum.INFO
        assert message_data['messages'][0]['message_code'] == infy_dpp_sdk.data.MessageCodeEnum.INFO_SUCCESS

    # Verify run batch summary
    assert len(processor_exec_list) == 4
    for processor_name, var_dict in processor_exec_output_dict.items():
        print(processor_name)
        assert os.path.exists(f"{STORAGE_ROOT_PATH}" +
                              var_dict['SYS_CONTROLLER_RES_FILE_PATH'])


def test_pipeline_serial_2():
    """Test method for scenario where initial context data is provided by client"""
    abs_deployment_config_file_path = f"{CONTAINER_ROOT_PATH}{DEPLOYMENT_CONFIG_FILE_PATH}"
    dpp_orchestrator = infy_dpp_sdk.orchestrator.OrchestratorCLI(
        input_config_file_path=SERIAL_FLOW_INPUT_CONFIG_FILE_PATH,
        deployment_config_file_path=abs_deployment_config_file_path)

    context_data = {'Preprocessor': {'a': 1, 'b': 2}}
    processor_response_data_list = dpp_orchestrator.run_batch(context_data)
    processor_exec_list, processor_exec_output_dict = dpp_orchestrator.get_run_batch_summary()

    # Verify processor_response_data_list
    assert len(processor_response_data_list) == 2
    document_id_list = [x.dict()['document_data']['document_id']
                        for x in processor_response_data_list]
    assert len(set(document_id_list)) == 2
    message_data_list = [x.dict()['message_data']
                         for x in processor_response_data_list]
    assert len(message_data_list) == 2
    for message_data in message_data_list:
        assert len(message_data['messages']) == 1
        assert message_data['messages'][0]['message_type'] == infy_dpp_sdk.data.MessageTypeEnum.INFO
        assert message_data['messages'][0]['message_code'] == infy_dpp_sdk.data.MessageCodeEnum.INFO_SUCCESS

    # Verify run batch summary
    assert len(processor_exec_list) == 4
    for processor_name, var_dict in processor_exec_output_dict.items():
        print(processor_name)
        assert os.path.exists(f"{STORAGE_ROOT_PATH}" +
                              var_dict['SYS_CONTROLLER_RES_FILE_PATH'])


def test_pipeline_parallel_1():
    """Test method for normal scenario"""
    abs_deployment_config_file_path = f"{CONTAINER_ROOT_PATH}{DEPLOYMENT_CONFIG_FILE_PATH}"
    dpp_orchestrator = infy_dpp_sdk.orchestrator.OrchestratorCLI(
        input_config_file_path=PARALLEL_FLOW_INPUT_CONFIG_FILE_PATH,
        deployment_config_file_path=abs_deployment_config_file_path)

    processor_response_data_list = dpp_orchestrator.run_batch()
    processor_exec_list, processor_exec_output_dict = dpp_orchestrator.get_run_batch_summary()

    # Verify processor_response_data_list
    assert len(processor_response_data_list) == 2
    document_id_list = [x.dict()['document_data']['document_id']
                        for x in processor_response_data_list]
    assert len(set(document_id_list)) == 2
    message_data_list = [x.dict()['message_data']
                         for x in processor_response_data_list]
    assert len(message_data_list) == 2
    for message_data in message_data_list:
        assert len(message_data['messages']) == 1
        assert message_data['messages'][0]['message_type'] == infy_dpp_sdk.data.MessageTypeEnum.INFO
        assert message_data['messages'][0]['message_code'] == infy_dpp_sdk.data.MessageCodeEnum.INFO_SUCCESS

    # Verify run batch summary
    assert len(processor_exec_list) == 5
    for processor_name, var_dict in processor_exec_output_dict.items():
        print(processor_name)
        assert os.path.exists(f"{STORAGE_ROOT_PATH}" +
                              var_dict['SYS_CONTROLLER_RES_FILE_PATH'])

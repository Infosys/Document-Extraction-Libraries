# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import os
import time
import pytest
import infy_fs_utils
import infy_dpp_sdk

STORAGE_ROOT_PATH_CLOUD = f"mmsrepo/docwb/unittest/infy_dpp_sdk/{__name__}"
CONTAINER_ROOT_PATH = f"C:/temp/unittest/infy_dpp_sdk/{__name__}/CONTAINER"
INPUT_CONFIG_FILE_PATH = '/data/config/dpp_pipeline2_cloud_input_config.json'
DEPLOYMENT_CONFIG_FILE_PATH = '/data/config/dpp_deployment_config.json'


@pytest.fixture(scope='module', autouse=True)
def pre_test(create_root_folders, copy_files_to_root_folder):
    """Test pre-run method"""
    # Create data folders
    create_root_folders([CONTAINER_ROOT_PATH])

    def archive_root_path():
        # Archive existing root path folder in cloud
        storage_root_path_cloud_parent = os.path.dirname(
            STORAGE_ROOT_PATH_CLOUD)
        storage_config_data = infy_fs_utils.data.StorageConfigData(
            **{
                "storage_root_uri": f"s3://{storage_root_path_cloud_parent}",
                "storage_server_url": os.environ['INFY_STORAGE_SERVER_URL'],
                "storage_access_key": os.environ['INFY_STORAGE_ACCESS_KEY'],
                "storage_secret_key": os.environ['INFY_STORAGE_SECRET_KEY'],
            })
        infy_fs_utils.manager.FileSystemManager().add_fs_handler(
            infy_fs_utils.provider.FileSystemHandler(storage_config_data), 'my_key_archival')

        file_sys_handler = infy_fs_utils.manager.FileSystemManager(
        ).get_fs_handler('my_key_archival')
        source_folder_name = os.path.basename(STORAGE_ROOT_PATH_CLOUD)
        if file_sys_handler.exists(source_folder_name):
            archival_folder_name = f'{source_folder_name}_{time.strftime("%Y%m%d_%H%M%S")}'
            file_sys_handler.move_folder(
                source_folder_name, archival_folder_name)

        file_sys_handler.create_folders(source_folder_name)

    def copy_data_files(file_sys_handler):
        # Deployment config file is owned by a separate application
        SAMPLE_ROOT_PATH = os.path.abspath("./my_dummy_processor_app")
        FILES_TO_COPY = [
            ['dpp_deployment_config.json', f"{SAMPLE_ROOT_PATH}/config",
                f"{CONTAINER_ROOT_PATH}/data/config"]
        ]
        copy_files_to_root_folder(FILES_TO_COPY)

        SAMPLE_ROOT_PATH = os.path.abspath("./data/sample")
        FILES_TO_COPY = [
            ['company1.txt', f"{SAMPLE_ROOT_PATH}/input", "/data/input"],
            ['company2.txt', f"{SAMPLE_ROOT_PATH}/input", "/data/input"],
            [os.path.basename(INPUT_CONFIG_FILE_PATH), f"{SAMPLE_ROOT_PATH}/config",
                "/data/config"]
        ]
        for file_to_copy in FILES_TO_COPY:
            file_sys_handler.put_file(file_to_copy[1] + "/" + file_to_copy[0],
                                      file_to_copy[2] + "/" + file_to_copy[0])

    archive_root_path()

    storage_config_data = infy_fs_utils.data.StorageConfigData(
        **{
            "storage_root_uri": f"s3://{STORAGE_ROOT_PATH_CLOUD}",
            "storage_server_url": os.environ['INFY_STORAGE_SERVER_URL'],
            "storage_access_key": os.environ['INFY_STORAGE_ACCESS_KEY'],
            "storage_secret_key": os.environ['INFY_STORAGE_SECRET_KEY'],
        })

    file_sys_handler = infy_fs_utils.provider.FileSystemHandler(
        storage_config_data)
    infy_fs_utils.manager.FileSystemManager().add_fs_handler(
        file_sys_handler,
        infy_dpp_sdk.common.Constants.FSH_DPP)

    # Copy files to pick up folder
    copy_data_files(file_sys_handler)

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

    yield  # Run all test methods
    # Post run cleanup
    # Delete file system handler so that other test modules don't get duplicate key error
    infy_fs_utils.manager.FileSystemManager().delete_fs_handler(
        infy_dpp_sdk.common.Constants.FSH_DPP)
    infy_fs_utils.manager.FileSystemLoggingManager().delete_fs_logging_handler(
        infy_dpp_sdk.common.Constants.FSLH_DPP)


@pytest.mark.skip(reason="Please uncomment only for testing with cloud storage")
def test_pipeline_scenario_1():
    """Test method for normal scenario"""
    abs_deployment_config_file_path = f"{CONTAINER_ROOT_PATH}{DEPLOYMENT_CONFIG_FILE_PATH}"
    dpp_orchestrator = infy_dpp_sdk.orchestrator.OrchestratorCLI(
        input_config_file_path=INPUT_CONFIG_FILE_PATH,
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
        print("SYS_CONTROLLER_RES_FILE_PATH",
              var_dict['SYS_CONTROLLER_RES_FILE_PATH'])

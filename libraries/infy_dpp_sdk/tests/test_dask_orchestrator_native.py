# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import os
import pytest
import infy_fs_utils
import infy_dpp_sdk


STORAGE_ROOT_PATH = f"C:/temp/unittest/infy_dpp_sdk/{__name__}/STORAGE"
DASK_FLOW_INPUT_CONFIG_FILE_PATH = '/data/config/dpp_dask_pipeline_input_config.json'


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
        [os.path.basename(DASK_FLOW_INPUT_CONFIG_FILE_PATH), f"{SAMPLE_ROOT_PATH}/config",
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


def test_pipeline_dask():
    """DPP Dask Pipeline| NOTE: Before running this with dask copy use_cases folder to infy_dpp_sdk folder"""
    dpp_orchestrator = infy_dpp_sdk.orchestrator.OrchestratorNative(
        input_config_file_path=DASK_FLOW_INPUT_CONFIG_FILE_PATH)
    processor_response_data_list = dpp_orchestrator.run_batch()

    assert len(processor_response_data_list) == 2
    document_id_list = [x.dict()['document_data']['document_id']
                        for x in processor_response_data_list]
    assert len(set(document_id_list)) == 2

    # Validate business data
    business_attribute_data_list = [x.dict()['document_data']['business_attribute_data']
                                    for x in processor_response_data_list]
    company_names, company_countries = [], []
    for business_attribute_data in business_attribute_data_list:
        print(business_attribute_data)
        company_names.extend(
            [x['text'] for x in business_attribute_data if x['name'] == 'Company Name'])
        company_countries.extend(
            [x['text'] for x in business_attribute_data if x['name'] == 'Country'])

    assert set(company_names) == {'Infosys', 'Microsoft'}
    assert set(company_countries) == {'Indian', 'American'}

    message_data_list = [x.dict()['message_data']
                         for x in processor_response_data_list]

    assert len(message_data_list) == 2
    for message_data in message_data_list:
        assert len(message_data['messages']) == 1
        assert message_data['messages'][0]['message_type'] == infy_dpp_sdk.data.MessageTypeEnum.INFO
        assert message_data['messages'][0]['message_code'] == infy_dpp_sdk.data.MessageCodeEnum.INFO_SUCCESS

    processor_exec_list, processor_exec_output_dict = dpp_orchestrator.get_run_batch_summary()
    assert processor_exec_list == [
        'document_downloader', 'content_extractor',
        'attribute_extractor', 'document_uploader']
    assert [x for x in processor_exec_output_dict] == [
        '001', '002', '003', '004']

    print(processor_response_data_list)

    # Run the orchestrator again to check for no records found handling
    dpp_orchestrator = infy_dpp_sdk.orchestrator.OrchestratorNative(
        input_config_file_path=DASK_FLOW_INPUT_CONFIG_FILE_PATH)
    processor_response_data_list = dpp_orchestrator.run_batch()
    assert len(processor_response_data_list) >= 1
    document_id_list = [x.dict()['document_data']['document_id']
                        for x in processor_response_data_list]
    assert len(set(document_id_list)) >= 1
    message_data_list = [x.dict()['message_data']
                         for x in processor_response_data_list]
    assert len(message_data_list) >= 1
    for message_data in message_data_list:
        assert len(message_data['messages']) == 1
        assert message_data['messages'][0]['message_type'] == infy_dpp_sdk.data.MessageTypeEnum.INFO

    print(processor_response_data_list)

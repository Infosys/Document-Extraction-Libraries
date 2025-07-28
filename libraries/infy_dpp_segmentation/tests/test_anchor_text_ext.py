# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#
import pytest
import infy_fs_utils
import infy_dpp_sdk

STORAGE_ROOT_PATH = f"C:/temp/unittest/infy_dpp_segmentation/{__name__}/STORAGE"
CONTAINER_ROOT_PATH = f"C:/temp/unittest/infy_dpp_segmentation/{__name__}/CONTAINER"


@pytest.fixture(scope='module', autouse=True)
def pre_test(create_root_folders, copy_files_to_root_folder):
    """Initialization method"""
    # Create data folders
    create_root_folders([STORAGE_ROOT_PATH, CONTAINER_ROOT_PATH])
    # Copy files to pick up folder
    SAMPLE_ROOT_PATH = "./data/sample"
    FILES_TO_COPY = [
        ['invoice1.jpg', f"{SAMPLE_ROOT_PATH}/input",
            f"{STORAGE_ROOT_PATH}/data/input"],
        ['pipeline_input_config_anchor_text.json', f"{SAMPLE_ROOT_PATH}/config",
            f"{STORAGE_ROOT_PATH}/data/config"],
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


def test_anchor_text_extraction():
    """
        Test case for dpp_segmentation
    """
    PROCESSOR_INPUT_CONFIG_PATH = '/data/config/pipeline_input_config_anchor_text.json'
    dpp_orchestrator = infy_dpp_sdk.orchestrator.OrchestratorNativeBasic(
        input_config_file_path=PROCESSOR_INPUT_CONFIG_PATH)
    response_data_list = dpp_orchestrator.run_batch()

    message_data = response_data_list[0].message_data
    if message_data:
        for message in message_data:
            print(message)
        assert False

    assert len(response_data_list[0].context_data) >= 4
    assert response_data_list[0].context_data.get('content_extractor').get(
        'content_extractor_image').get('image_ocr').get('image_ocr_file_path') is not None
    assert response_data_list[0].context_data.get('content_extractor').get(
        'content_extractor_image').get('image_ocr').get('image_file_path') is not None
    assert response_data_list[0].context_data.get('rd_based_attribute_extractor').get(
        'raw_attributes')[0].get('values')[0]['text_obj_list']['text'] == 'SDCKL00562710'
    assert response_data_list[0].context_data.get('request_closer') is not None

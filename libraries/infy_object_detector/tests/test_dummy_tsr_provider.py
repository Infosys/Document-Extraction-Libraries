"""Test module for Dummy TSR Provider"""
# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import json
import pytest
import infy_fs_utils.data
from infy_object_detector.common.constants import Constants
from infy_object_detector.schema.table_data import BaseTableRequestData
from .sample.dummy_tsr_provider import DummyTsrProviderConfigData, DummyTsrProvider

STORAGE_ROOT_PATH = f"C:/temp/unittest/infy_object_detector/{__name__}/STORAGE"
CONTAINER_ROOT_PATH = f"C:/temp/unittest/infy_object_detector/{__name__}/CONTAINER"


@pytest.fixture(scope='module', autouse=True)
def setup(create_root_folders, copy_files_to_root_folder) -> dict:
    """Initialization method"""
    create_root_folders([STORAGE_ROOT_PATH, CONTAINER_ROOT_PATH])
    SAMPLE_ROOT_PATH = "./data/sample"
    FILES_TO_COPY = [
        ['*.json', f"{SAMPLE_ROOT_PATH}/input",
            f"{STORAGE_ROOT_PATH}/data/input"],
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
        Constants.FSH_OBJECT_DETECTOR)
    infy_fs_utils.manager.FileSystemManager().add_fs_handler(file_sys_handler)

    logging_config_data = infy_fs_utils.data.LoggingConfigData(
        **{
            # "logger_group_name": "my_group_1",
            "logging_level": 10,
            "logging_format": "",
            "logging_timestamp_format": "",
            "log_file_data": {
                "log_file_dir_path": "/logs",
                "log_file_name_prefix": "infy_object_detector",
                # "log_file_name_suffix": "1",
                "log_file_extension": ".log"

            }})
    file_sys_logging_handler = infy_fs_utils.provider.FileSystemLoggingHandler(
        logging_config_data, file_sys_handler)
    infy_fs_utils.manager.FileSystemLoggingManager(
    ).set_root_handler_name(Constants.FSLH_OBJECT_DETECTOR)
    infy_fs_utils.manager.FileSystemLoggingManager(
    ).add_fs_logging_handler(file_sys_logging_handler)

    yield
    infy_fs_utils.manager.FileSystemManager().delete_fs_handler()
    infy_fs_utils.manager.FileSystemLoggingManager().delete_fs_logging_handler()


def test_dummy_provider():
    """test method for dummy provider"""
    dummy_tsr_provider_config_data = DummyTsrProviderConfigData(
        **{
            "model_path": "",
            "model_name": ""
        })
    provider = DummyTsrProvider(dummy_tsr_provider_config_data, )
    table_request_data = BaseTableRequestData(
        image_file_path='./data/input/image.jpg')
    response = provider.extract_table_data(table_request_data)
    assert response is not None and response.table_data is not None
    __pretty_print(response.dict())
    # Print schema
    print(response.schema_json(indent=4))


def __pretty_print(dictionary):
    p = json.dumps(dictionary, indent=4)
    print(p.replace('\"', '\''))

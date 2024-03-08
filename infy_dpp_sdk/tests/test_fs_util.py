# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                   #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import os
import pytest
import infy_fs_utils

# Create inside temp folder for the purpose of unit testing
STORAGE_ROOT_PATH = f"C:/temp/unittest/infy_dpp_sdk/{__name__}/STORAGE"


@pytest.fixture(scope='module', autouse=True)
def pre_test(create_root_folders):
    """Initialization method"""
    # Create data folders
    create_root_folders([STORAGE_ROOT_PATH])
    # Configure storage properties
    storage_config_data = infy_fs_utils.data.StorageConfigData(
        **{
            "storage_root_uri": f"file://{STORAGE_ROOT_PATH}",
            "storage_server_url": "",
            "storage_access_key": "",
            "storage_secret_key": ""
        })

    infy_fs_utils.manager.FileSystemManager().add_fs_handler(
        infy_fs_utils.provider.FileSystemHandler(storage_config_data), 'my_key_1')
    yield  # Run all test methods
    # Post run cleanup
    # Delete file system handler so that other test modules don't get duplicate key error
    infy_fs_utils.manager.FileSystemManager().delete_fs_handler('my_key_1')


def test_properties():
    """Test method"""
    fs_handler = infy_fs_utils.manager.FileSystemManager(
    ).get_fs_handler('my_key_1')
    assert fs_handler.get_scheme() == 'file'
    assert fs_handler.get_storage_root_uri(
    ) == f"file://{STORAGE_ROOT_PATH}"
    assert type(fs_handler.get_instance()).__name__ == "LocalFileSystem"


def test_create_folders():
    """Test method"""
    fs_handler = infy_fs_utils.manager.FileSystemManager(
    ).get_fs_handler('my_key_1')
    fs_handler.create_folders('/a/b/c')
    assert os.path.exists(f'{STORAGE_ROOT_PATH}/a/b/c')

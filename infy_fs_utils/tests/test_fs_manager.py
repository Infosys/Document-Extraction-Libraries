# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                   #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import pytest
import infy_fs_utils


# Create inside temp folder for the purpose of unit testing
STORAGE_ROOT_PATH = f"C:/temp/unittest/infy_fs_utils/{__name__}/STORAGE"


@pytest.fixture(scope='module', autouse=True)
def pre_test(create_root_folders):
    """Initialization method"""
    # Empty the storage folder
    create_root_folders([STORAGE_ROOT_PATH])
    # Create storage config data
    storage_config_data = infy_fs_utils.data.StorageConfigData(
        **{
            "storage_root_uri": f"file://{STORAGE_ROOT_PATH}",
            "storage_server_url": "",
            "storage_access_key": "",
            "storage_secret_key": ""
        })
    infy_fs_utils.manager.FileSystemManager().add_fs_handler(
        infy_fs_utils.provider.FileSystemHandler(storage_config_data), 'my_key_100')


def test_duplicate_keys_error():
    """Test method"""
    try:
        infy_fs_utils.manager.FileSystemManager().add_fs_handler(
            infy_fs_utils.provider.FileSystemHandler(infy_fs_utils.data.StorageConfigData()), 'my_key_100')
    except Exception as e:
        assert e.args[0] == "Duplicate key=my_key_100 found. Please provide unique keys."

# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                   #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import os
import pytest
import infy_fs_utils


@pytest.fixture(scope='module', autouse=True)
def pre_test():
    """Initialization method"""
    # Create storage config data
    storage_config_data = infy_fs_utils.data.StorageConfigData(
        **{
            "storage_root_uri": "s3://mmsrepo/docwb/infy_fs_utils/unittest",
            "storage_server_url": "http://10.66.217.23:9000",
            "storage_access_key": "AKaHEgQ4II0S7BjT6DjAUDA4BX",
            "storage_secret_key": os.environ['INFY_STORAGE_SECRET_KEY'],
        })
    infy_fs_utils.manager.FileSystemManager().add_fs_handler(
        infy_fs_utils.provider.FileSystemHandler(storage_config_data), 'my_key_2')


def test_properties():
    """Test method"""
    file_sys_handler = infy_fs_utils.manager.FileSystemManager(
    ).get_fs_handler('my_key_2')
    assert file_sys_handler.get_scheme() == 's3'
    assert file_sys_handler.get_storage_root_uri(
    ) == "s3://mmsrepo/docwb/infy_fs_utils/unittest"
    assert type(file_sys_handler.get_instance()).__name__ == "S3FileSystem"


def test_create_folders():
    """Test method"""
    file_sys_handler = infy_fs_utils.manager.FileSystemManager(
    ).get_fs_handler('my_key_2')
    file_sys_handler.create_folders('/a/b/c')
    assert file_sys_handler.list_files('/a/b/c') == []


def test_list_files():
    """Test method"""
    file_sys_handler = infy_fs_utils.manager.FileSystemManager(
    ).get_fs_handler('my_key_2')
    if not file_sys_handler.exists('/a/b/l'):
        file_sys_handler.create_folders('/a/b/l')
        assert file_sys_handler.list_files('/a/b/l') == []
    # Write file with extension .txt and .csv respectively
    file_sys_handler.write_file('/a/b/l/my_file_1.txt', 'Greetings!')
    file_sys_handler.write_file('/a/b/l/my_file_1.csv', '1,2,3')
    # Get list of all files w/o and w/ filter respectively
    my_list = file_sys_handler.list_files('/a/b/l')
    assert my_list == ['/a/b/l/my_file_1.csv', '/a/b/l/my_file_1.txt']
    my_list = file_sys_handler.list_files('/a/b/l', '*.txt')
    assert my_list == ['/a/b/l/my_file_1.txt']


def test_read_write_file():
    """Test method"""
    file_sys_handler = infy_fs_utils.manager.FileSystemManager(
    ).get_fs_handler('my_key_2')
    if not file_sys_handler.exists('/a/b/rw'):
        file_sys_handler.create_folders('/a/b/rw')
        assert file_sys_handler.list_files('/a/b/rw') == []
    # Create and write to file
    file_sys_handler.write_file('/a/b/rw/my_file_1.txt', 'Greetings!')
    assert file_sys_handler.list_files(
        '/a/b/rw') == ['/a/b/rw/my_file_1.txt']
    # Read file
    file_content = file_sys_handler.read_file('/a/b/rw/my_file_1.txt')
    assert file_content == 'Greetings!'
    # Do cleanup
    file_sys_handler.delete_file('/a/b/rw/my_file_1.txt')


def test_delete_file():
    """Test method"""
    file_sys_handler = infy_fs_utils.manager.FileSystemManager(
    ).get_fs_handler('my_key_2')
    # Create folders
    if not file_sys_handler.exists('/a/b/d'):
        file_sys_handler.create_folders('/a/b/d')
        assert file_sys_handler.list_files('/a/b/d') == []
    # Create and write to file
    file_sys_handler.write_file(
        '/a/b/d/my_file_1.txt', 'Unit testing for deleting a file')
    assert file_sys_handler.list_files('/a/b/d') == ['/a/b/d/my_file_1.txt']
    # Delete file
    file_sys_handler.delete_file('/a/b/d/my_file_1.txt')
    assert file_sys_handler.list_files('/a/b/d') == []

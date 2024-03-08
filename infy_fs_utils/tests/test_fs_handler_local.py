# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                   #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#
import os
import hashlib
import pytest
import infy_fs_utils


# Create inside temp folder for the purpose of unit testing
STORAGE_ROOT_PATH = f"C:/temp/unittest/infy_fs_utils/{__name__}/STORAGE"


@pytest.fixture(scope='module', autouse=True)
def pre_test(create_root_folders):
    """Initialization method"""
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
        infy_fs_utils.provider.FileSystemHandler(storage_config_data), 'my_key_1')


def test_properties():
    """Test method"""
    file_sys_handler = infy_fs_utils.manager.FileSystemManager(
    ).get_fs_handler('my_key_1')
    assert file_sys_handler.get_scheme() == 'file'
    assert file_sys_handler.get_storage_root_uri(
    ) == f"file://{STORAGE_ROOT_PATH}"
    assert type(file_sys_handler.get_instance()).__name__ == "LocalFileSystem"


def test_create_folders():
    """Test method"""
    file_sys_handler = infy_fs_utils.manager.FileSystemManager(
    ).get_fs_handler('my_key_1')
    file_sys_handler.create_folders('/a/b/c')
    assert os.path.exists(f'{STORAGE_ROOT_PATH}/a/b/c')


def test_read_write_file():
    """Test method"""
    file_sys_handler = infy_fs_utils.manager.FileSystemManager(
    ).get_fs_handler('my_key_1')
    file_sys_handler.create_folders('/a/b/c')
    assert os.path.exists(f'{STORAGE_ROOT_PATH}/a/b/c')
    # Create and write to file
    file_sys_handler.write_file('/a/b/my_file_1.txt', 'Greetings!')
    assert os.path.exists(f'{STORAGE_ROOT_PATH}/a/b/my_file_1.txt')
    # Read file
    file_content = file_sys_handler.read_file('/a/b/my_file_1.txt')
    assert file_content == 'Greetings!'


def test_delete_file():
    """Test method"""
    file_sys_handler = infy_fs_utils.manager.FileSystemManager(
    ).get_fs_handler('my_key_1')
    # Create folders
    file_sys_handler.create_folders('/a/b/d')
    # Create and write to file
    file_sys_handler.write_file(
        '/a/b/d/my_file_1.txt', 'Unit testing for deleting a file')
    assert os.path.exists(f'{STORAGE_ROOT_PATH}/a/b/d/my_file_1.txt')
    # Delete file
    file_sys_handler.delete_file('/a/b/d/my_file_1.txt')
    assert not os.path.exists(f'{STORAGE_ROOT_PATH}/a/b/d/my_file_1.txt')

def test_file_hash():
    """Test method"""
    file_sys_handler = infy_fs_utils.manager.FileSystemManager(
    ).get_fs_handler('my_key_1')
    file_sys_handler.create_folders('/a/b/c')
    assert os.path.exists(f'{STORAGE_ROOT_PATH}/a/b/c')
    # Create and write to file
    file_sys_handler.write_file('/a/b/my_file_1.txt', 'Greetings!')
    assert os.path.exists(f'{STORAGE_ROOT_PATH}/a/b/my_file_1.txt')
    # Read file
    file_content = file_sys_handler.read_file('/a/b/my_file_1.txt')
    assert file_content == 'Greetings!'
    # Get hash
    hash_lib = hashlib.sha1()
    hash_lib.update(file_content.encode())
    file_hash_value=hash_lib.hexdigest()
    print(file_hash_value)
    assert file_hash_value=='36b940cf8a8d37916f5d6160a03a558c4d526e01'

    
def test_create_dirs_if_absent():  
    """Test method"""
    file_sys_handler = infy_fs_utils.manager.FileSystemManager(
    ).get_fs_handler('my_key_1')      
    if not file_sys_handler.exists('/a/b/c/d'):
        file_sys_handler.create_folders('/a/b/c/d')
    assert os.path.exists(f'{STORAGE_ROOT_PATH}/a/b/c/d')

# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import os
import time
import tempfile
import datetime
import hashlib
import pytest
import infy_fs_utils


# Create inside temp folder for the purpose of unit testing
STORAGE_ROOT_PATH_LOCAL = f"C:/temp/unittest/infy_fs_utils/{__name__}/STORAGE"
STORAGE_ROOT_PATH_CLOUD = f"mmsrepo/docwb/unittest/infy_fs_utils/{__name__}"
FS_HANDLER_KEYS = ['my_key_1', 'my_key_2']


@pytest.fixture(scope='module', autouse=True)
def pre_test(create_root_folders):
    """Initialization method"""
    # Create root folders in local
    create_root_folders([STORAGE_ROOT_PATH_LOCAL])
    # Archive existing root path folder in cloud
    storage_root_path_cloud_parent = os.path.dirname(STORAGE_ROOT_PATH_CLOUD)
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
        file_sys_handler.move_folder(source_folder_name, archival_folder_name)

    file_sys_handler.create_folders(source_folder_name)

    # Create storage config data
    storage_config_data = infy_fs_utils.data.StorageConfigData(
        **{
            "storage_root_uri": f"file://{STORAGE_ROOT_PATH_LOCAL}",
            "storage_server_url": "",
            "storage_access_key": "",
            "storage_secret_key": ""
        })

    infy_fs_utils.manager.FileSystemManager().add_fs_handler(
        infy_fs_utils.provider.FileSystemHandler(storage_config_data), 'my_key_1')

    storage_config_data = infy_fs_utils.data.StorageConfigData(
        **{
            "storage_root_uri": f"s3://{STORAGE_ROOT_PATH_CLOUD}",
            "storage_server_url": os.environ['INFY_STORAGE_SERVER_URL'],
            "storage_access_key": os.environ['INFY_STORAGE_ACCESS_KEY'],
            "storage_secret_key": os.environ['INFY_STORAGE_SECRET_KEY'],
        })
    infy_fs_utils.manager.FileSystemManager().add_fs_handler(
        infy_fs_utils.provider.FileSystemHandler(storage_config_data), 'my_key_2')


def test_properties():
    """Test method"""
    for fs_key in FS_HANDLER_KEYS:
        file_sys_handler = infy_fs_utils.manager.FileSystemManager(
        ).get_fs_handler(fs_key)
        if fs_key == 'my_key_1':
            assert file_sys_handler.get_scheme() == 'file'
            assert file_sys_handler.get_storage_root_uri(
            ) == f"file://{STORAGE_ROOT_PATH_LOCAL}"
            assert type(file_sys_handler.get_instance()
                        ).__name__ == "LocalFileSystem"
        elif fs_key == 'my_key_2':
            assert file_sys_handler.get_scheme() == 's3'
            assert file_sys_handler.get_storage_root_uri(
            ) == f"s3://{STORAGE_ROOT_PATH_CLOUD}"
            assert type(file_sys_handler.get_instance()
                        ).__name__ == "S3FileSystem"


def test_create_move_folders():
    """Test method"""
    for fs_key in FS_HANDLER_KEYS:
        file_sys_handler = infy_fs_utils.manager.FileSystemManager(
        ).get_fs_handler(fs_key)
        file_sys_handler.create_folders('/a/b/c')
        assert file_sys_handler.exists('/a/b/c')
        file_list = file_sys_handler.list_files('/a/b/c')
        assert len(file_list) == 0  # Should not include empty file
        file_sys_handler.move_folder('/a/b/c', '/a/b/m')
        assert file_sys_handler.exists('/a/b/m')


def test_get_folder():
    """Test method"""
    for fs_key in FS_HANDLER_KEYS:
        file_sys_handler = infy_fs_utils.manager.FileSystemManager(
        ).get_fs_handler(fs_key)
        file_sys_handler.create_folders('/a/b/c')
        assert file_sys_handler.exists('/a/b/c')
        download_root_path = f'{tempfile.gettempdir()}/downloads_{fs_key}_{time.strftime("%Y%m%d_%H%M%S")}'
        download_path = f"{download_root_path}/one/c"
        file_sys_handler.get_folder('/a/b/c', download_path)
        assert os.path.exists(download_path)
        assert not os.path.exists(f"{download_path}/empty.fsh")

        if fs_key == 'my_key_2':  # Cloud storage
            download_path = f"{download_root_path}/two/c"
            file_sys_handler.get_folder(
                '/a/b/c', download_path, empty_file_name=None)
            assert os.path.exists(download_path)
            assert os.path.exists(f"{download_path}/empty.fsh")


def test_read_write_delete_file():
    """Test method"""
    for fs_key in FS_HANDLER_KEYS:
        file_sys_handler = infy_fs_utils.manager.FileSystemManager(
        ).get_fs_handler(fs_key)
        # 1. Write to file
        FILE_PATH = '/a/b/my_file_1.txt'
        FILE_CONTENT = f'Greetings! Today is {str(datetime.datetime.now())}'
        file_sys_handler.write_file(FILE_PATH, FILE_CONTENT)
        assert file_sys_handler.exists(FILE_PATH)
        # 2. Read from file
        file_content = file_sys_handler.read_file(FILE_PATH)
        assert file_content == FILE_CONTENT
        # 3. Delete file
        file_sys_handler.delete_file(FILE_PATH)
        assert not file_sys_handler.exists(FILE_PATH)


def test_overwrite_file():
    """Test method"""
    for fs_key in FS_HANDLER_KEYS:
        file_sys_handler = infy_fs_utils.manager.FileSystemManager(
        ).get_fs_handler(fs_key)

        FILE_PATH = '/a/b/o/my_file_1.txt'
        # 1. Write to file and verify content by reading it
        FILE_CONTENT_1 = f'Greetings! Today is {str(datetime.datetime.now())}'
        file_sys_handler.write_file(FILE_PATH, FILE_CONTENT_1)
        file_content = file_sys_handler.read_file(FILE_PATH)
        assert file_content == FILE_CONTENT_1

        # 2. Ovewrite with different content and verify by reading it
        FILE_CONTENT_2 = f'Good morning! Today is {str(datetime.datetime.now())}'
        file_sys_handler.write_file(FILE_PATH, FILE_CONTENT_2)
        file_content = file_sys_handler.read_file(FILE_PATH)
        assert file_content == FILE_CONTENT_2

        # 3. Delete file
        file_sys_handler.delete_file(FILE_PATH)
        assert not file_sys_handler.exists(FILE_PATH)


def test_list_files():
    """Test method"""
    for fs_key in FS_HANDLER_KEYS:
        file_sys_handler = infy_fs_utils.manager.FileSystemManager(
        ).get_fs_handler(fs_key)

        # Write file with extension .txt and .csv respectively
        file_sys_handler.write_file('/a/b/l/my_file_1.txt', 'Greetings!')
        file_sys_handler.write_file('/a/b/l/my_file_1.csv', '1,2,3')
        # Get list of all files w/o and w/ filter respectively
        my_list = file_sys_handler.list_files('/a/b/l')
        assert my_list == ['/a/b/l/my_file_1.csv', '/a/b/l/my_file_1.txt']
        my_list = file_sys_handler.list_files('/a/b/l', '*.txt')
        assert my_list == ['/a/b/l/my_file_1.txt']


def test_file_hash():
    """Test method"""
    for fs_key in FS_HANDLER_KEYS:
        file_sys_handler = infy_fs_utils.manager.FileSystemManager(
        ).get_fs_handler(fs_key)

        # 1. Write to file
        FILE_PATH = '/a/b/my_file_1.txt'
        FILE_CONTENT = 'Greetings!'
        file_sys_handler.write_file(FILE_PATH, FILE_CONTENT)

        # 2. Read from file
        file_content = file_sys_handler.read_file(FILE_PATH)
        assert file_content == FILE_CONTENT

        # 3. Get hash
        hash_lib = hashlib.sha1()
        hash_lib.update(file_content.encode())
        file_hash_value = hash_lib.hexdigest()
        print(file_hash_value)
        assert file_hash_value == '36b940cf8a8d37916f5d6160a03a558c4d526e01'

        # 4. Delete file
        file_sys_handler.delete_file(FILE_PATH)
        assert not file_sys_handler.exists(FILE_PATH)


def test_upload_download_file():
    """Test method"""
    for fs_key in FS_HANDLER_KEYS:
        file_sys_handler = infy_fs_utils.manager.FileSystemManager(
        ).get_fs_handler(fs_key)

        # Generate test data file in local filesystem
        FILE_CONTENT = f'Greetings! Today is {str(datetime.datetime.now())}'
        data_file_path = f"{tempfile.gettempdir()}/Greetings.txt"
        with open(data_file_path, "w", encoding='utf-8') as file:
            file.write(FILE_CONTENT)

        UPLOAD_TO_FILE_PATH = '/hello/world/Greetings1.txt'
        file_sys_handler.put_file(data_file_path, UPLOAD_TO_FILE_PATH)
        assert file_sys_handler.exists(UPLOAD_TO_FILE_PATH)

        DOWNLOAD_TO_FILE_PATH = f"{tempfile.gettempdir()}/Greetings2.txt"

        file_sys_handler.get_file(
            UPLOAD_TO_FILE_PATH, DOWNLOAD_TO_FILE_PATH)
        assert os.path.exists(DOWNLOAD_TO_FILE_PATH)
        with open(DOWNLOAD_TO_FILE_PATH, "r", encoding='utf-8') as file:
            file_content = file.read()
        assert file_content == FILE_CONTENT


def test_upload_folder():
    """Test method"""
    file_sys_handler = infy_fs_utils.manager.FileSystemManager(
    ).get_fs_handler('my_key_2')

    # Generate test data file in local filesystem

    LOCAL_FOLDER_ROOT_PATH = f"{tempfile.gettempdir()}/folder1"
    local_file_path_list = [f"{LOCAL_FOLDER_ROOT_PATH}/greetings_100.txt",
                            f"{LOCAL_FOLDER_ROOT_PATH}/greetings_200.txt",
                            f"{LOCAL_FOLDER_ROOT_PATH}/folder2/greetings_300.txt"]
    for data_file_path in local_file_path_list:
        os.makedirs(os.path.dirname(data_file_path), exist_ok=True)
        with open(data_file_path, "w", encoding='utf-8') as file:
            file_content = f'Greetings! Today is {str(datetime.datetime.now())}'
            file.write(file_content)

    CLOUD_FOLDER_ROOT_PATH = '/hello2/documents'
    file_sys_handler.put_folder(LOCAL_FOLDER_ROOT_PATH, CLOUD_FOLDER_ROOT_PATH)
    uploaded_files = file_sys_handler.list_files(CLOUD_FOLDER_ROOT_PATH)

    local_file_name_list = [os.path.relpath(
        x, LOCAL_FOLDER_ROOT_PATH) for x in local_file_path_list]
    uploaded_file_name_list = [os.path.relpath(
        x, CLOUD_FOLDER_ROOT_PATH) for x in uploaded_files]

    assert uploaded_file_name_list == local_file_name_list

# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import os
import time
import datetime
import concurrent.futures
import pytest
import infy_fs_utils


# Create inside temp folder for the purpose of unit testing
STORAGE_ROOT_PATH_LOCAL = f"C:/temp/unittest/infy_fs_utils/{__name__}/STORAGE"
STORAGE_ROOT_PATH_CLOUD = f"mmsrepo/docwb/unittest/infy_fs_utils/{__name__}"
FS_HANDLER_KEYS = ['my_key_m_1', 'my_key_m_2']


@pytest.fixture(scope='module', autouse=True)
def pre_test(create_root_folders):
    """Initialization method"""
    # Create root folders in local
    create_root_folders([STORAGE_ROOT_PATH_LOCAL])
    # Archive existing root path folder in cloud
    # storage_root_path_cloud_parent = os.path.dirname(STORAGE_ROOT_PATH_CLOUD)
    # storage_config_data = infy_fs_utils.data.StorageConfigData(
    #     **{
    #         "storage_root_uri": f"s3://{storage_root_path_cloud_parent}",
    #         "storage_server_url": os.environ['INFY_STORAGE_SERVER_URL'],
    #         "storage_access_key": os.environ['INFY_STORAGE_ACCESS_KEY'],
    #         "storage_secret_key": os.environ['INFY_STORAGE_SECRET_KEY'],
    #     })
    # infy_fs_utils.manager.FileSystemManager().add_fs_handler(
    #     infy_fs_utils.provider.FileSystemHandler(storage_config_data), 'my_key_m_archival')

    # file_sys_handler = infy_fs_utils.manager.FileSystemManager(
    # ).get_fs_handler('my_key_m_archival')
    # source_folder_name = os.path.basename(STORAGE_ROOT_PATH_CLOUD)
    # if file_sys_handler.exists(source_folder_name):
    #     archival_folder_name = f'{source_folder_name}_{time.strftime("%Y%m%d_%H%M%S")}'
    #     file_sys_handler.move_folder(source_folder_name, archival_folder_name)

    # file_sys_handler.create_folders(source_folder_name)

    # Create storage config data
    storage_config_data = infy_fs_utils.data.StorageConfigData(
        **{
            "storage_root_uri": f"file://{STORAGE_ROOT_PATH_LOCAL}",
            "storage_server_url": "",
            "storage_access_key": "",
            "storage_secret_key": ""
        })

    infy_fs_utils.manager.FileSystemManager().add_fs_handler(
        infy_fs_utils.provider.FileSystemHandler(storage_config_data), 'my_key_m_1')

    storage_config_data = infy_fs_utils.data.StorageConfigData(
        **{
            "storage_root_uri": f"s3://{STORAGE_ROOT_PATH_CLOUD}",
            "storage_server_url": os.environ['INFY_STORAGE_SERVER_URL'],
            "storage_access_key": os.environ['INFY_STORAGE_ACCESS_KEY'],
            "storage_secret_key": os.environ['INFY_STORAGE_SECRET_KEY'],
        })
    infy_fs_utils.manager.FileSystemManager().add_fs_handler(
        infy_fs_utils.provider.FileSystemHandler(storage_config_data), 'my_key_m_2')


def test_read_write_delete_file():
    """Test method"""
    def code_block(fs_key, idx):
        file_sys_handler = infy_fs_utils.manager.FileSystemManager(
        ).get_fs_handler(fs_key)
        # 1. Write to file
        FILE_PATH = f'/a/b/{idx}/my_file_1.txt'
        FILE_CONTENT = f'Greetings! Today is {str(datetime.datetime.now())}'
        file_sys_handler.write_file(FILE_PATH, FILE_CONTENT)
        assert file_sys_handler.exists(FILE_PATH)
        # 2. Read from file
        file_content = file_sys_handler.read_file(FILE_PATH)
        assert file_content == FILE_CONTENT
        # 3. Delete file
        file_sys_handler.delete_file(FILE_PATH)
        assert not file_sys_handler.exists(FILE_PATH)
    for fs_key in FS_HANDLER_KEYS:
        start = time.time()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            for idx in range(10):
                future = executor.submit(code_block, fs_key, idx)
                futures.append(future)
            for future in futures:
                result = future.result()
                print(result)
        end = time.time()
        print("Time diff:", end-start)

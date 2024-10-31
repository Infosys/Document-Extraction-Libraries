# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#
"""Testing module"""

import os
import json
import shutil
import pytest
import infy_fs_utils
import infy_gen_ai_sdk
import infy_gen_ai_sdk.sparsedb
from typing import List

# Create inside temp folder for the purpose of unit testing
STORAGE_ROOT_PATH = f"C:/temp/unittest/infy_gen_ai_sdk/{__name__}/STORAGE"
CONTAINER_ROOT_PATH = f"C:/temp/unittest/infy_gen_ai_sdk/{__name__}/CONTAINER"


@pytest.fixture(scope='module', autouse=True)
def pre_test(create_root_folders, copy_files_to_root_folder):
    """Initialization method"""
    create_root_folders([STORAGE_ROOT_PATH, CONTAINER_ROOT_PATH])
    # Copy files to pick up folder
    SAMPLE_ROOT_PATH = "./data/sample"
    FILES_TO_COPY = [
        ['company_google.txt', f"{SAMPLE_ROOT_PATH}/input",
            f"{STORAGE_ROOT_PATH}/data/input"],
        ['company_ibm.txt', f"{SAMPLE_ROOT_PATH}/input",
            f"{STORAGE_ROOT_PATH}/data/input"],
        ['company_nvidia.txt', f"{SAMPLE_ROOT_PATH}/input",
            f"{STORAGE_ROOT_PATH}/data/input"],
        ['*.*', f"{SAMPLE_ROOT_PATH}/db",
            f"{STORAGE_ROOT_PATH}/data/db"],
    ]
    copy_files_to_root_folder(FILES_TO_COPY)

    # Create storage config data
    storage_config_data = infy_fs_utils.data.StorageConfigData(
        **{
            "storage_root_uri": f"file://{STORAGE_ROOT_PATH}",
            "storage_server_url": "",
            "storage_access_key": "",
            "storage_secret_key": ""
        })

    infy_fs_utils.manager.FileSystemManager().add_fs_handler(
        infy_fs_utils.provider.FileSystemHandler(storage_config_data),
        infy_gen_ai_sdk.common.Constants.FSH_GEN_AI_SDK)

    # Configure client properties
    client_config_data = infy_gen_ai_sdk.ClientConfigData(
        **{
            "container_data": {
                "container_root_path": f"{CONTAINER_ROOT_PATH}",
            }
        })
    infy_gen_ai_sdk.ClientConfigManager().load(client_config_data)
    print(infy_gen_ai_sdk.ClientConfigManager().get().dict())

    yield  # Run all test methods
    # Post run cleanup
    # Delete file system handler so that other test modules don't get duplicate key error
    infy_fs_utils.manager.FileSystemManager().delete_fs_handler(
        infy_gen_ai_sdk.common.Constants.FSH_GEN_AI_SDK)


def test_sparsedb_bm25s_save_records():
    """Test method"""

    # Set NLTK_DATA_DIR
    os.environ["NLTK_DATA_DIR"] = 'C:/MyProgramFiles/AI/nltk_data'

    # Step 1 - Choose sparse db provider
    sparse_db_provider_config_data = infy_gen_ai_sdk.sparsedb.provider.bm25s.SparseDbProviderConfigData(
        **{
            'db_folder_path': '/data/db/sparseindex/bm25s/documents',
            'db_index_name': 'save_records',
            'db_index_secret_key': '1234'
        })
    sparse_db_provider = infy_gen_ai_sdk.sparsedb.provider.bm25s.Bm25sSparseDbProvider(
        sparse_db_provider_config_data)

    # Step 2 - Add record(s) to vector db
    # Record 1 of 3
    sparse_record_config_dict = infy_gen_ai_sdk.sparsedb.provider.bm25s.SparseDbRecordConfigData(
        **{
            'content_file_path': '/data/input/company_google.txt',
            'metadata': {
                'company': 'google'
            }
        })
    sparse_db_provider.save_record(sparse_record_config_dict)

    # Record 2 of 3
    sparse_record_config_dict = infy_gen_ai_sdk.sparsedb.provider.bm25s.SparseDbRecordConfigData(
        **{
            'content_file_path': '/data/input/company_ibm.txt',
            'metadata': {
                'company': 'ibm'
            }
        })
    sparse_db_provider.save_record(sparse_record_config_dict)

    # Record 3 of 3
    sparse_record_config_dict = infy_gen_ai_sdk.sparsedb.provider.bm25s.SparseDbRecordConfigData(
        **{
            'content_file_path': '/data/input/company_nvidia.txt',
            'metadata': {
                'company': 'nvidia'
            }
        })
    sparse_db_provider.save_record(sparse_record_config_dict)


def test_sparsedb_bm25s_get_records():
    """Test method"""

    # Set NLTK_DATA_DIR
    os.environ["NLTK_DATA_DIR"] = 'C:/MyProgramFiles/AI/nltk_data'

    # Step 1 - Choose sparse db provider
    sparse_db_provider_config_data = infy_gen_ai_sdk.sparsedb.provider.bm25s.SparseDbProviderConfigData(
        **{
            'db_folder_path': '/data/db/sparseindex/bm25s/documents',
            'db_index_name': 'documents',
            'db_index_secret_key': '1234'
        })
    sparse_db_provider = infy_gen_ai_sdk.sparsedb.provider.bm25s.Bm25sSparseDbProvider(
        sparse_db_provider_config_data)

    records: List[infy_gen_ai_sdk.sparsedb.provider.bm25s.SparseDbRecordData] = sparse_db_provider.get_records()
    assert len(records) >= 1
    for record in records:
        print("content =", record.content)
        print("metadata =", record.metadata)


def test_sparsedb_bm25s_get_matches():
    """Test method"""

    # Set NLTK_DATA_DIR
    os.environ["NLTK_DATA_DIR"] = 'C:/MyProgramFiles/AI/nltk_data'

    # Step 1 - Choose sparse db provider
    sparse_db_provider_config_data = infy_gen_ai_sdk.sparsedb.provider.bm25s.SparseDbProviderConfigData(
        **{
            'db_folder_path': '/data/db/sparseindex/bm25s/documents',
            'db_index_name': 'documents',
            'db_index_secret_key': '1234'
        })
    sparse_db_provider = infy_gen_ai_sdk.sparsedb.provider.bm25s.Bm25sSparseDbProvider(
        sparse_db_provider_config_data)

    # Step 2 - Run query to get best matches
    query_params_data = infy_gen_ai_sdk.sparsedb.provider.bm25s.SparseDbQueryParamsData(
        **{
            'query': "Which companies are multinational?",
            'top_k': 4,
            'pre_filter_fetch_k': 10,
            'filter_metadata': {
            }
        })
    records: List[infy_gen_ai_sdk.sparsedb.provider.bm25s.SparseDbMatchesRecordData] = sparse_db_provider.get_matches(
        query_params_data)
    assert len(records) >= 1
    for record in records:
        print("db_folder_path =", record.db_folder_path)
        print("content =", record.content)
        print("metadata =", record.metadata)
        print("score =", record.score)


def test_sparsedb_bm25s_delete_records():
    """Test method"""

    # Set NLTK_DATA_DIR
    os.environ["NLTK_DATA_DIR"] = 'C:/MyProgramFiles/AI/nltk_data'

    # Step 1 - Choose sparse db provider
    sparse_db_provider_config_data = infy_gen_ai_sdk.sparsedb.provider.bm25s.SparseDbProviderConfigData(
        **{
            'db_folder_path': '/data/db/sparseindex/bm25s/documents',
            'db_index_name': 'documents',
            'db_index_secret_key': '1234'
        })
    sparse_db_provider = infy_gen_ai_sdk.sparsedb.provider.bm25s.Bm25sSparseDbProvider(
        sparse_db_provider_config_data)

    sparse_db_provider.delete_records()

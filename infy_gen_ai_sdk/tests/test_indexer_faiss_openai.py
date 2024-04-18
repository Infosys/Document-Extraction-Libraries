# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                   #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

"""Testing module"""

import time
import os
import shutil
import pytest
import infy_fs_utils
import infy_gen_ai_sdk

# Create inside temp folder for the purpose of unit testing
STORAGE_ROOT_PATH = f"C:/temp/unittest/infy_gen_ai_sdk/{__name__}/STORAGE"
CONTAINER_ROOT_PATH = f"C:/temp/unittest/infy_gen_ai_sdk/{__name__}/CONTAINER"
EXPECTED_DATA = {
    "VECTOR_DB": {
        "FILE_PATH": STORAGE_ROOT_PATH +
        '/vectordb/openai/companies/companies.faiss'
    }
}


@pytest.fixture(scope='module', autouse=True)
def pre_test(create_root_folders, copy_files_to_root_folder):
    """Initialization method"""
    # Archive old data
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

    # Delete existing files
    db_folder_path = os.path.dirname(EXPECTED_DATA['VECTOR_DB']['FILE_PATH'])
    if os.path.exists(db_folder_path):
        shutil.rmtree(db_folder_path)

    yield  # Run all test methods
    # Post run cleanup
    # Delete file system handler so that other test modules don't get duplicate key error
    infy_fs_utils.manager.FileSystemManager().delete_fs_handler(
        infy_gen_ai_sdk.common.Constants.FSH_GEN_AI_SDK)


def test_1():
    """Test method"""
    # Step 1 - Choose embedding provider
    embedding_provider_config_data = infy_gen_ai_sdk.embedding.provider.OpenAIEmbeddingProviderConfigData(
        **{
            "api_type": "azure",
            "api_url": "",
            "api_key": os.environ['INFY_OPENAI_SECRET_KEY'],
            "model_name": "text-embedding-ada-002",
            "deployment_name": "text-embedding-ada-002",
            "api_version": "2022-12-01",
            "chunk_size": 1000
        })
    embedding_provider = infy_gen_ai_sdk.embedding.provider.OpenAIEmbeddingProvider(
        embedding_provider_config_data)

    # Step 2 - Choose vector db provider
    vector_db_provider_config_data = infy_gen_ai_sdk.vectordb.provider.faiss.VectorDbProviderConfigData(
        **{
            'db_folder_path': '/vectordb/openai/companies',
            'db_index_name': 'companies'
        })
    vector_db_provider = infy_gen_ai_sdk.vectordb.provider.faiss.FaissVectorDbProvider(
        vector_db_provider_config_data, embedding_provider)

    # Step 3 - Add record(s) to vector db
    # Record 1 of 3
    db_record_data = infy_gen_ai_sdk.vectordb.provider.faiss.InsertVectorDbRecordData(
        **{
            'content_file_path': '/data/input/company_google.txt',
            'metadata': {
                'company': 'google'
            }
        })
    vector_db_provider.save_record(db_record_data)

    # Record 2 of 3
    db_record_data = infy_gen_ai_sdk.vectordb.provider.faiss.InsertVectorDbRecordData(
        **{
            'content_file_path': '/data/input/company_ibm.txt',
            'metadata': {
                'company': 'ibm'
            }
        })
    vector_db_provider.save_record(db_record_data)

    # Record 3 of 3
    db_record_data = infy_gen_ai_sdk.vectordb.provider.faiss.InsertVectorDbRecordData(
        **{
            'content_file_path': '/data/input/company_nvidia.txt',
            'metadata': {
                'company': 'nvidia'
            }
        })
    vector_db_provider.save_record(db_record_data)

    assert os.path.exists(EXPECTED_DATA['VECTOR_DB']['FILE_PATH'])

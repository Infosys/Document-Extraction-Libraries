# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                   #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

"""Testing module"""

import time
import os
import shutil
from typing import List
import pytest
import infy_fs_utils
import infy_gen_ai_sdk

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
        ['companies.faiss', f"{SAMPLE_ROOT_PATH}/vectordb/openai-text-davinci-003/companies",
            f"{STORAGE_ROOT_PATH}/vectordb/openai-text-davinci-003/companies"],
        ['companies.pkl', f"{SAMPLE_ROOT_PATH}/vectordb/openai-text-davinci-003/companies",
            f"{STORAGE_ROOT_PATH}/vectordb/openai-text-davinci-003/companies"]
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


def test_1():
    """Test method"""
    # Step 1 - Choose embedding provider
    embedding_provider_config_data = infy_gen_ai_sdk.embedding.provider.OpenAIEmbeddingProviderConfigData(
        **{
            "api_type": "azure",
            "api_url": "https://openai-ppcazure017.openai.azure.com/",
            "api_key": os.environ['INFY_OPENAI_SECRET_KEY'],
            "api_version": "2022-12-01",
            "chunk_size": 1000
        })
    embedding_provider = infy_gen_ai_sdk.embedding.provider.OpenAIEmbeddingProvider(
        embedding_provider_config_data)

    # Step 2 - Choose vector db provider
    vector_db_provider_config_data = infy_gen_ai_sdk.vectordb.provider.faiss.VectorDbProviderConfigData(
        **{
            'db_folder_path': '/vectordb/openai-text-davinci-003/companies',
            'db_index_name': 'companies'
        })
    vector_db_provider = infy_gen_ai_sdk.vectordb.provider.faiss.FaissVectorDbProvider(
        vector_db_provider_config_data, embedding_provider)

    # Step 3 - Run query to get best matches
    query_params_data = infy_gen_ai_sdk.vectordb.provider.faiss.VectorDbQueryParamsData(
        **{
            'query': "What is the amount?",
            'top_k': 5,
            'pre_filter_fetch_k': 10,
            'filter_metadata': {
            }
        })
    records: List[infy_gen_ai_sdk.vectordb.provider.faiss.MatchingVectorDbRecordData] = vector_db_provider.get_matches(
        query_params_data)
    assert len(records) == 3
    assert [x.metadata['company']
            for x in records] == ['google', 'ibm', 'nvidia']
    print(records)

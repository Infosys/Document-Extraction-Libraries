# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

"""Testing module"""

import time
import os
import glob
from typing import List
import pytest
import infy_fs_utils
import infy_gen_ai_sdk
from tests.internal import test_pt_01_indexer_faiss_openai_doc_chunk_level

# Create inside temp folder for the purpose of unit testing
STORAGE_ROOT_PATH = f"C:/temp/unittest/infy_gen_ai_sdk/{__name__}/STORAGE"
CONTAINER_ROOT_PATH = f"C:/temp/unittest/infy_gen_ai_sdk/{__name__}/CONTAINER"


@pytest.fixture(scope='module', autouse=True)
def pre_test(create_root_folders, copy_files_to_root_folder):
    """Initialization method"""
    # Archive old data
    create_root_folders([STORAGE_ROOT_PATH, CONTAINER_ROOT_PATH])
    # Copy files to pick up folder
    SAMPLE_ROOT_PATH = test_pt_01_indexer_faiss_openai_doc_chunk_level.STORAGE_ROOT_PATH
    FILES_TO_COPY = [
        ['*.*', f"{SAMPLE_ROOT_PATH}/vectordb",
            f"{STORAGE_ROOT_PATH}/vectordb"],
    ]
    _ = copy_files_to_root_folder(FILES_TO_COPY)

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


@pytest.mark.skip(reason="Please uncomment only for performance testing due to batch openai calls")
def test_1():
    """Test method"""
    # Step 1 - Choose embedding provider
    embedding_provider_config_data = infy_gen_ai_sdk.embedding.provider.OpenAIEmbeddingProviderConfigData(
        **{
            "api_type": "azure",
            "api_url": os.environ['AZURE_OPENAI_SERVER_BASE_URL'],
            "api_key": os.environ['AZURE_OPENAI_SECRET_KEY'],
            "api_version": "2022-12-01",
            "chunk_size": 1000
        })
    embedding_provider = infy_gen_ai_sdk.embedding.provider.OpenAIEmbeddingProvider(
        embedding_provider_config_data)
    total_time, counter = 0, 0
    for x in range(1, 21):
        # Step 2 - Choose vector db provider
        start_time = time.time()
        records_count = 0
        faiss_file_path = STORAGE_ROOT_PATH + \
            '/vectordb/openai-text-davinci-003/sow_pt_doc_chunk_level_db/' + \
            str(x)+'_*/'
        faiss_dirs = glob.glob(faiss_file_path)
        if not faiss_dirs:
            continue
        for faiss_dir in faiss_dirs:
            vector_db_provider_config_data = infy_gen_ai_sdk.vectordb.provider.faiss.VectorDbProviderConfigData(
                **{
                    'db_folder_path': '/vectordb/openai-text-davinci-003/sow_pt_doc_chunk_level_db/'+os.path.basename(os.path.dirname(faiss_dir)),
                    'db_index_name': 'sow_pt_db'
                })
            vector_db_provider = infy_gen_ai_sdk.vectordb.provider.faiss.FaissVectorDbProvider(
                vector_db_provider_config_data, embedding_provider)

            # Step 3 - Run query to get best matches
            query_params_data = infy_gen_ai_sdk.vectordb.provider.faiss.VectorDbQueryParamsData(
                **{
                    'query': "what is the project name?",
                    'top_k': 100,
                    'pre_filter_fetch_k': 100,
                    'filter_metadata': {
                    }
                })
            records: List[infy_gen_ai_sdk.vectordb.provider.faiss.MatchingVectorDbRecordData] = vector_db_provider.get_matches(
                query_params_data)
            records_count += len(records)
            # rec_metadata= [x.metadata for x in records]
            # print(rec_metadata)
        assert records_count > 1
        end_time_in_mins = round((time.time() - start_time)/60, 4)
        total_time += end_time_in_mins
        counter += 1
        print(
            f"[End] - Document - {x}; record matched {records_count} execution elapse time is {end_time_in_mins} mins")
    print(f"Avg. time in mins {total_time/counter}")

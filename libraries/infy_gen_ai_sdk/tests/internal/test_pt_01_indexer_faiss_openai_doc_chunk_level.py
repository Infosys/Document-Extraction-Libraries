# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

"""Testing module"""

import os
import glob
import pytest
import infy_fs_utils
import infy_gen_ai_sdk

# Create inside temp folder for the purpose of unit testing
STORAGE_ROOT_PATH = f"C:/temp/unittest/infy_gen_ai_sdk/{__name__}/STORAGE"
CONTAINER_ROOT_PATH = f"C:/temp/unittest/infy_gen_ai_sdk/{__name__}/CONTAINER"
EXPECTED_DATA = {
    "VECTOR_DB": {
        "ROOT_PATH": STORAGE_ROOT_PATH + '/vectordb/openai-text-davinci-003/sow_pt_doc_chunk_level_db',
        "DB_COUNT": None,
    }
}


@pytest.fixture(scope='module', autouse=True)
def pre_test(create_root_folders, copy_files_to_root_folder):
    """Initialization method"""
    # Archive old data
    create_root_folders([STORAGE_ROOT_PATH, CONTAINER_ROOT_PATH])
    # Copy files to pick up folder
    INFY_SP_ROOT_PATH = os.getenv('INFY_SP_ROOT_PATH')
    SAMPLE_ROOT_PATH = fr"{INFY_SP_ROOT_PATH}/workbenchlibraries - Documents/SHARED_DATA"
    SAMPLE_ROOT_PATH += "/unit_test_data/infy_gen_ai_sdk/data/sample"
    FILES_TO_COPY = [
        ['*.txt', f"{SAMPLE_ROOT_PATH}/chunks",
            f"{STORAGE_ROOT_PATH}/data/chunks"],

    ]
    copied_files = copy_files_to_root_folder(FILES_TO_COPY, 2)
    EXPECTED_DATA["VECTOR_DB"]["DB_COUNT"] = len(copied_files)

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

    for x in range(1, 21):
        # Step 3 - Add record(s) to vector db
        for document_file in glob.glob(STORAGE_ROOT_PATH+'/data/chunks/Doc-'+str(x)+'_*.txt'):
            print(document_file)
            file_name = os.path.basename(document_file)
            page_num = file_name.split('_')[1].split('.')[0]
            # Step 2 - Choose vector db provider
            vector_db_provider_config_data = infy_gen_ai_sdk.vectordb.provider.faiss.VectorDbProviderConfigData(
                **{
                    'db_folder_path': '/vectordb/openai-text-davinci-003/sow_pt_doc_chunk_level_db/'+str(x)+'_'+str(page_num),
                    'db_index_name': 'sow_pt_db'
                })
            vector_db_provider = infy_gen_ai_sdk.vectordb.provider.faiss.FaissVectorDbProvider(
                vector_db_provider_config_data, embedding_provider)

            db_record_data = infy_gen_ai_sdk.vectordb.provider.faiss.InsertVectorDbRecordData(
                **{
                    'content_file_path': "/data/chunks/"+file_name,
                    'metadata': {
                        'document_id': file_name.split('_')[0],
                        'page_num': page_num
                    }
                })
            vector_db_provider.save_record(db_record_data)
    assert len(glob.glob(EXPECTED_DATA["VECTOR_DB"]['ROOT_PATH'] +
               "/**/*.faiss")) == EXPECTED_DATA["VECTOR_DB"]["DB_COUNT"]

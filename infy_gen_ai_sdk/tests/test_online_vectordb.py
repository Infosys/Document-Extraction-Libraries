# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#
"""Testing module"""

import infy_gen_ai_sdk


def test_online_vectordb_save_records():
    """Test method to save records to vectordb"""

    vector_db_provider_config_data = infy_gen_ai_sdk.vectordb.provider.online.OnlineVectorDbProviderConfigData(
        **{
            'db_service_url': '',
            'model_name': 'all-MiniLM-L6-v2',
            'index_id': '',
            "collection_name": "document",
            "collection_secret_key": ""
        })

    vector_db_provider = infy_gen_ai_sdk.vectordb.provider.online.OnlineVectorDbProvider(
        vector_db_provider_config_data)

    request_body = infy_gen_ai_sdk.vectordb.provider.online.InsertVectorDbRecordData(
        **{
            "content": "This is a test record also called as dummy, this record is used for testing  purpose only. It is not a real record.",
            "metadata": {
                "doc_name": "test_doc",
                            "page_no": 1
            }
        })
    encoded_path_list = vector_db_provider.save_record(request_body)
    print("encoded_path_list:", encoded_path_list)


def test_online_vectordb_get_records():
    """Test method to get records from vectordb"""

    vector_db_provider_config_data = infy_gen_ai_sdk.vectordb.provider.online.OnlineVectorDbProviderConfigData(
        **{
            'db_service_url': '',
            'model_name': 'all-MiniLM-L6-v2',
            'index_id': '',
            "collection_name": "document",
            "collection_secret_key": ""
        })

    vector_db_provider = infy_gen_ai_sdk.vectordb.provider.online.OnlineVectorDbProvider(
        vector_db_provider_config_data)

    records = vector_db_provider.get_records()
    assert len(records) >= 1
    for record in records:
        print("id =", record.get('id'))
        print("content =", record.get('content'))
        print("metadata =", record.get('metadata'))


def test_online_vectordb_get_matches():
    """Test method to get matches from vectordb"""

    vector_db_provider_config_data = infy_gen_ai_sdk.vectordb.provider.online.OnlineVectorDbProviderConfigData(
        **{
            'db_service_url': '',
            'model_name': 'all-MiniLM-L6-v2',
            'index_id': '',
            "collection_name": "document",
            "collection_secret_key": ""
        })

    vector_db_provider = infy_gen_ai_sdk.vectordb.provider.online.OnlineVectorDbProvider(
        vector_db_provider_config_data)

    request_body = infy_gen_ai_sdk.vectordb.provider.online.VectorDbQueryParamsData(
        **{
            "query": "What is the record also called as?",
            "top_k": 1,
            "pre_filter_fetch_k": 10,
            "filter_metadata": {},
            "min_distance": 0,
            "max_distance": 2
        })

    records = vector_db_provider.get_matches(request_body)
    assert len(records) >= 1
    for record in records:
        print("id =", record.get('id'))
        print("content =", record.get('content'))
        print("metadata =", record.get('metadata'))


def test_online_vectordb_delete_records():
    """Test method to delete records from vectordb"""

    vector_db_provider_config_data = infy_gen_ai_sdk.vectordb.provider.online.OnlineVectorDbProviderConfigData(
        **{
            'db_service_url': '',
            'model_name': 'all-MiniLM-L6-v2',
            'index_id': '',
            "collection_name": "document",
            "collection_secret_key": ""
        })

    vector_db_provider = infy_gen_ai_sdk.vectordb.provider.online.OnlineVectorDbProvider(
        vector_db_provider_config_data)

    vector_db_provider.delete_records()

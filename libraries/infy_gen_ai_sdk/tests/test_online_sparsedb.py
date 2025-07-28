# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

"""Testing module"""

import os
import infy_gen_ai_sdk


def test_online_sparse_save_records():
    """Test method to save records to sparsedb"""

    sparse_db_provider_config_data = infy_gen_ai_sdk.sparsedb.provider.online.OnlineSparseDbProviderConfigData(
        **{
            'db_service_url': os.environ['INFY_DB_SERVICE_BASE_URL'],
            'method_name': 'bm25s',
            'index_id': 'test_index',
            "collection_name": "document",
            "collection_secret_key": ""
        })

    sparse_db_provider = infy_gen_ai_sdk.sparsedb.provider.online.OnlineSparseDbProvider(
        sparse_db_provider_config_data)

    request_body = infy_gen_ai_sdk.sparsedb.provider.online.InsertSparseDbRecordData(
        **{
            "content": "This is a test record also called as dummy, this record is used for testing  purpose only. It is not a real record.",
            "metadata": {}
        })
    encoded_path_list = sparse_db_provider.save_record(request_body)
    print("encoded_path_list:", encoded_path_list)


def test_online_sparseb_get_records():
    """Test method to get records from sparsedb"""

    sparse_db_provider_config_data = infy_gen_ai_sdk.sparsedb.provider.online.OnlineSparseDbProviderConfigData(
        **{
            'db_service_url': os.environ['INFY_DB_SERVICE_BASE_URL'],
            'method_name': 'bm25s',
            'index_id': 'test_index',
            "collection_name": "document",
            "collection_secret_key": ""
        })

    sparse_db_provider = infy_gen_ai_sdk.sparsedb.provider.online.OnlineSparseDbProvider(
        sparse_db_provider_config_data)

    records = sparse_db_provider.get_records()
    assert len(records) >= 1
    for record in records:
        print("content =", record.get('content'))
        print("metadata =", record.get('metadata'))


def test_online_sparsedb_get_matches():
    """Test method to get matches from sparsedb"""

    sparse_db_provider_config_data = infy_gen_ai_sdk.sparsedb.provider.online.OnlineSparseDbProviderConfigData(
        **{
            'db_service_url': os.environ['INFY_DB_SERVICE_BASE_URL'],
            'method_name': 'bm25s',
            'index_id': 'test_index',
            "collection_name": "document",
            "collection_secret_key": ""
        })

    sparse_db_provider = infy_gen_ai_sdk.sparsedb.provider.online.OnlineSparseDbProvider(
        sparse_db_provider_config_data)

    request_body = infy_gen_ai_sdk.sparsedb.provider.online.SparseDbQueryParamsData(
        **{
            "query": "What is the record also called as?",
            "top_k": 1,
            "pre_filter_fetch_k": 10,
            "filter_metadata": {},
            "min_distance": 0,
            "max_distance": 2
        })

    records = sparse_db_provider.get_matches(request_body)
    assert len(records) >= 1
    for record in records:
        print("content =", record.get('content'))
        print("metadata =", record.get('metadata'))


def test_online_sparsedb_delete_records():
    """Test method to delete records from sparsedb"""

    sparse_db_provider_config_data = infy_gen_ai_sdk.sparsedb.provider.online.OnlineSparseDbProviderConfigData(
        **{
            'db_service_url': os.environ['INFY_DB_SERVICE_BASE_URL'],
            'method_name': 'bm25s',
            'index_id': 'test_index',
            "collection_name": "document",
            "collection_secret_key": ""
        })

    sparse_db_provider = infy_gen_ai_sdk.sparsedb.provider.online.OnlineSparseDbProvider(
        sparse_db_provider_config_data)

    sparse_db_provider.delete_records()

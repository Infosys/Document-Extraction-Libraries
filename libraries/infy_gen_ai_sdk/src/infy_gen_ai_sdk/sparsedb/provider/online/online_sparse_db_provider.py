# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

"""Module for Online Sparse DB provider"""

import logging
import requests
import infy_fs_utils
from ....schema.sparse_db_data import OnlineSparseDbConfigData, BaseSparseDbRecordData, BaseSparseDbQueryParamsData, BaseSparseDbMacthesData
from ....sparsedb.interface.i_online_sparse_db_provider import IOnlineSparseDbProvider
from ....common import Constants


class OnlineSparseDbProviderConfigData(OnlineSparseDbConfigData):
    """Domain class"""
    db_service_url: str = None
    method_name: str = None
    index_id: str = None
    collection_name: str = None
    collection_secret_key: str = None


class InsertSparseDbRecordData(BaseSparseDbRecordData):
    """Domain class"""
    content: str = None
    metadata: dict = None


class SparseDbQueryParamsData(BaseSparseDbQueryParamsData):
    """Domain class"""
    query: str = None
    top_k: int = 1
    pre_filter_fetch_k: int = 10
    filter_metadata: dict = None
    min_distance: int = 0
    max_distance: int = 2


class SparseDbMatchesRecordData(BaseSparseDbMacthesData):
    """Domain class"""


class OnlineSparseDbProvider(IOnlineSparseDbProvider):
    """Online Sparse DB provider"""

    def __init__(self, online_sparse_config_data: OnlineSparseDbProviderConfigData) -> None:
        if infy_fs_utils.manager.FileSystemLoggingManager().has_fs_logging_handler():
            self.__logger = infy_fs_utils.manager.FileSystemLoggingManager(
            ).get_fs_logging_handler().get_logger()
        else:
            self.__logger = logging.getLogger(__name__)

        self.__config_data = online_sparse_config_data.dict()

    def get_matches(self, query_params_data: SparseDbQueryParamsData):
        try:
            db_service_url = self.__config_data.get(
                'db_service_url', '').rstrip('/') + '/api/v1/db/sparsedb/getmatches'
            method_name = self.__config_data.get('method_name', '')
            index_id = self.__config_data.get('index_id', '')
            collection_name = self.__config_data.get('collection_name', '')
            collection_secret_key = self.__config_data.get(
                'collection_secret_key', '')
            query_params_data = query_params_data.dict()

            query_dict = {'method_name': method_name, 'index_id': index_id, 'collection_name': collection_name,
                          'collection_secret_key': collection_secret_key, 'query_dict': query_params_data}

            response = requests.post(
                db_service_url, json=query_dict, timeout=120)
            if response.status_code != 200:
                raise Exception("Failed to connect to endpoint")
            elif response.status_code == 200:
                response_json = response.json()
                if response_json.get('responseCde') != 200:
                    raise Exception(
                        f"Failed to get matches: {response_json.get('responseMsg')}")
                elif response_json.get('responseCde') == 200:
                    record_list = response_json.get('response').get('records')
                    return record_list
        except Exception as e:
            self.__logger.exception(e)
            raise e

    def save_record(self, db_record_data: InsertSparseDbRecordData):
        try:
            db_service_url = self.__config_data.get(
                'db_service_url', '').rstrip('/') + '/api/v1/db/sparsedb/saverecords'
            method_name = self.__config_data.get('method_name', '')
            index_id = self.__config_data.get('index_id', '')
            collection_name = self.__config_data.get('collection_name', '')
            collection_secret_key = self.__config_data.get(
                'collection_secret_key', '')
            record_data_dict = db_record_data.dict()

            query_dict = {'method_name': method_name, 'index_id': index_id, 'collection_name': collection_name,
                          'collection_secret_key': collection_secret_key, 'record_data_dict': record_data_dict}

            response = requests.post(
                db_service_url, json=query_dict, timeout=120)
            if response.status_code != 200:
                raise Exception("Failed to connect to endpoint")
            elif response.status_code == 200:
                response_json = response.json()
                if response_json.get('responseCde') != 200:
                    raise Exception(
                        f"Failed to save record: {response_json.get('responseMsg')}")
                elif response_json.get('responseCde') == 200:
                    return response_json.get('response').get('encoded_path_list')
        except Exception as e:
            self.__logger.exception(e)
            raise e

    def get_records(self):
        try:
            db_service_url = self.__config_data.get(
                'db_service_url', '').rstrip('/') + '/api/v1/db/sparsedb/getrecords'
            method_name = self.__config_data.get('method_name', '')
            index_id = self.__config_data.get('index_id', '')
            collection_name = self.__config_data.get('collection_name', '')
            collection_secret_key = self.__config_data.get(
                'collection_secret_key', '')

            query_dict = {'method_name': method_name, 'index_id': index_id, 'collection_name': collection_name,
                          'collection_secret_key': collection_secret_key}

            response = requests.post(
                db_service_url, json=query_dict, timeout=120)
            if response.status_code != 200:
                raise Exception("Failed to connect to endpoint")
            elif response.status_code == 200:
                response_json = response.json()
                if response_json.get('responseCde') != 200:
                    raise Exception(
                        f"Failed to get records: {response_json.get('responseMsg')}")
                elif response_json.get('responseCde') == 200:
                    record_list = response_json.get('response').get('records')
                    return record_list
        except Exception as e:
            self.__logger.exception(e)
            raise e

    def delete_records(self):
        try:
            db_service_url = self.__config_data.get(
                'db_service_url', '').rstrip('/') + '/api/v1/db/sparsedb/deleterecords'
            method_name = self.__config_data.get('method_name', '')
            index_id = self.__config_data.get('index_id', '')
            collection_name = self.__config_data.get('collection_name', '')
            collection_secret_key = self.__config_data.get(
                'collection_secret_key', '')

            query_dict = {'method_name': method_name, 'index_id': index_id, 'collection_name': collection_name,
                          'collection_secret_key': collection_secret_key}

            response = requests.post(
                db_service_url, json=query_dict, timeout=120)
            if response.status_code != 200:
                raise Exception("Failed to connect to endpoint")
            elif response.status_code == 200:
                response_json = response.json()
                if response_json.get('responseCde') != 200:
                    raise Exception(
                        f"Failed to delete record: {response_json.get('responseMsg')}")
                elif response_json.get('responseCde') == 200:
                    pass
        except Exception as e:
            self.__logger.exception(e)
            raise e

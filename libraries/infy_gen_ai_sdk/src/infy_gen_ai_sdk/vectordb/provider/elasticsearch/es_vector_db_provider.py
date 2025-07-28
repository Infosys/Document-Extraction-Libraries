# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

"""Module for Elascticsearch vector DB provider"""

import os
import logging
from typing import List
import infy_fs_utils
from .es_service import ElasticSearchService
from ....common.app_config_manager import AppConfigManager
from ....common.file_util import FileUtil
from ....schema.config_data import BaseVectorDbProviderConfigData
from ....schema.embedding_data import EmbeddingData
from ....schema.vector_db_data import BaseVectorDbQueryParamsData, BaseVectorDbRecordData
from ....vectordb.interface.i_vector_db_provider import IVectorDbProvider
from ....embedding.interface.i_embedding_provider import IEmbeddingProvider
from ....common import Constants


class VectorDbProviderConfigData(BaseVectorDbProviderConfigData):
    """Domain class"""
    db_server_url: str
    authenticate: bool
    username: str
    password: str
    verify_certs: bool
    cert_fingerprint: str
    index_id: str


class InsertVectorDbRecordData(BaseVectorDbRecordData):
    """Domain class"""
    content_file_path: str = None
    metadata: dict = None


class MatchingVectorDbRecordData(BaseVectorDbRecordData):
    """Domain class"""
    db_folder_path: str = None
    score: float = None
    content: str = None
    metadata: dict = None


class VectorDbRecordData(BaseVectorDbRecordData):
    """Domain class"""


class VectorDbQueryParamsData(BaseVectorDbQueryParamsData):
    """Domain class"""


class ESVectorDbProvider(IVectorDbProvider):
    """ELASTICSEARCH vector DB provider"""

    __DB_TYPE = "ELASTICSEARCH"

    def __init__(self, config_data: VectorDbProviderConfigData, embedding_provider: IEmbeddingProvider) -> None:
        if infy_fs_utils.manager.FileSystemLoggingManager().has_fs_logging_handler():
            self.__logger = infy_fs_utils.manager.FileSystemLoggingManager(
            ).get_fs_logging_handler().get_logger()
        else:
            self.__logger = logging.getLogger(__name__)

        self.__app_config = AppConfigManager().get_app_config()
        self.__fs_handler = infy_fs_utils.manager.FileSystemManager(
        ).get_fs_handler()
        super().__init__(db_type=self.__DB_TYPE, embedding_provider=embedding_provider)
        # Convert pydantic to dict for flexibility
        self.__internal_config_data = dict(config_data)
        # Create container folders if not present
        app_container_folders = [self.__app_config["CONTAINER"]["APP_DIR_DATA_PATH"],
                                 self.__app_config["CONTAINER"]["APP_DIR_TEMP_PATH"]]
        for app_container_folder in app_container_folders:
            FileUtil.create_dirs_if_absent(app_container_folder)

    def get_matches(self, query_params_data: VectorDbQueryParamsData) -> List[MatchingVectorDbRecordData]:
        '''Get top_k matches from elasticsearch index'''
        try:
            scores_list = []
            sorted_scores_list = []
            config_data = self.__internal_config_data
            db_server_url = config_data['db_server_url']
            authenticate = config_data['authenticate']
            username = config_data['username']
            password = config_data['password']
            verify_certs = config_data['verify_certs']
            cert_fingerprint = config_data['cert_fingerprint']
            index_id = config_data['index_id']
            ca_certs_path = os.environ.get('CA_CERTS_PATH')

            query = query_params_data.query
            filter_metadata = query_params_data.filter_metadata
            top_k = query_params_data.top_k
            pre_filter_fetch_k = query_params_data.pre_filter_fetch_k

            es_service_obj = ElasticSearchService(
                db_server_url, authenticate, username, password, verify_certs, cert_fingerprint, ca_certs_path, index_id)

            embedding_data: EmbeddingData = self._embedding_provider.generate_embedding(
                query)
            embedding_list = (embedding_data.vector[0]).tolist()
            model_name = embedding_data.model_name

            # Check if index exists
            index_exists = es_service_obj.check_index_exists()
            # Get all recorda if index exists else throw error
            if index_exists:
                records = es_service_obj.get_matches(
                    model_name, embedding_list, filter_metadata, top_k, pre_filter_fetch_k)
            else:
                raise ValueError(
                    f"Index doesn't exist: {index_id}")
            for record in records:
                vector_db_record_data_dict = {
                    "db_folder_path": config_data['db_server_url'],
                    'content': record['_source']['content'],
                    'metadata': record['_source']['metadata'],
                    "score": record['_score']
                }
                scores_list.append(MatchingVectorDbRecordData(
                    **vector_db_record_data_dict))
            sorted_scores_list = sorted(scores_list, key=lambda d: d.score)
            self.__logger.debug("Sorted scores list size: %s",
                                len(sorted_scores_list))
            return sorted_scores_list

        except Exception as e:
            self.__logger.exception(e)
            raise e

    def save_record(self, db_record_data: InsertVectorDbRecordData):
        '''Save record to elasticsearch index'''
        try:
            encoded_path = ''
            config_data = self.__internal_config_data
            db_server_url = config_data['db_server_url']
            authenticate = config_data['authenticate']
            username = config_data['username']
            password = config_data['password']
            verify_certs = config_data['verify_certs']
            cert_fingerprint = config_data['cert_fingerprint']
            index_id = config_data['index_id']
            ca_certs_path = os.environ.get('CA_CERTS_PATH')

            content_file_path = db_record_data.content_file_path
            metadata = db_record_data.metadata
            metadata['source'] = content_file_path

            es_service_obj = ElasticSearchService(
                db_server_url, authenticate, username, password, verify_certs, cert_fingerprint, ca_certs_path, index_id)

            local_content_file_path = f'{self.__app_config["CONTAINER"]["APP_DIR_TEMP_PATH"]}/{FileUtil.get_uuid()}'
            with self.__fs_handler.get_file_object(content_file_path) as file:
                with open(local_content_file_path, "wb") as output:
                    output.write(file.read())
            with open(local_content_file_path, 'r', encoding='utf-8') as file:
                content = file.read()

            # Generate embedding, convert that to list and get model name
            embedding_data: EmbeddingData = self._embedding_provider.generate_embedding(
                content)
            embedding_list = (embedding_data.vector[0]).tolist()
            model_name = embedding_data.model_name

            # Check if index exists
            index_exists = es_service_obj.check_index_exists()
            # Add record if index exists else create new index and add record
            if index_exists:
                response = es_service_obj.add_record(
                    model_name, embedding_list, content, metadata)
            else:
                es_service_obj.create_new_index(
                    embedding_data.vector_dimension)
                response = es_service_obj.add_record(
                    model_name, embedding_list, content, metadata)

            # Log index location where data is indexed
            self.__logger.info(
                'Record added to index %s', response.meta.headers['Location'])

            encoded_path = response.meta.headers['Location'] if response.meta.headers['Location'] else ''
            return encoded_path

        except Exception as e:
            self.__logger.exception(e)
            raise e

    def get_records(self, count: int = -1) -> List[VectorDbRecordData]:
        '''Get all records from elasticsearch index'''
        try:
            record_list = []
            config_data = self.__internal_config_data
            db_server_url = config_data['db_server_url']
            authenticate = config_data['authenticate']
            username = config_data['username']
            password = config_data['password']
            verify_certs = config_data['verify_certs']
            cert_fingerprint = config_data['cert_fingerprint']
            index_id = config_data['index_id']
            ca_certs_path = os.environ.get('CA_CERTS_PATH')

            es_service_obj = ElasticSearchService(
                db_server_url, authenticate, username, password, verify_certs, cert_fingerprint, ca_certs_path, index_id)

            # Check if index exists
            index_exists = es_service_obj.check_index_exists()
            # Get all recorda if index exists else throw error
            if index_exists:
                records = es_service_obj.get_records()
            else:
                raise ValueError(
                    f"Index doesn't exist: {index_id}")

            processed_count = 0
            for record in records:
                vector_db_record_data_dict = {
                    'id': record['_id'],
                    'content': record['_source']['content'],
                    'metadata': record['_source']['metadata']
                }
                record_list.append(VectorDbRecordData(
                    **vector_db_record_data_dict))
                processed_count += 1
                if count > -1 and processed_count >= count:
                    break

            return record_list

        except Exception as e:
            self.__logger.exception(e)
            raise e

    def delete_records(self):
        '''Delete an elasticsearch index'''
        try:
            config_data = self.__internal_config_data
            db_server_url = config_data['db_server_url']
            authenticate = config_data['authenticate']
            username = config_data['username']
            password = config_data['password']
            verify_certs = config_data['verify_certs']
            cert_fingerprint = config_data['cert_fingerprint']
            index_id = config_data['index_id']
            ca_certs_path = os.environ.get('CA_CERTS_PATH')

            es_service_obj = ElasticSearchService(
                db_server_url, authenticate, username, password, verify_certs, cert_fingerprint, ca_certs_path, index_id)

            # Check if index exists
            index_exists = es_service_obj.check_index_exists()
            # Delete index if exists else throw error
            if index_exists:
                response = es_service_obj.delete_index()
                if response:
                    self.__logger.info(
                        'Elasticsearch index deleted successfully %s', {index_id})
                else:
                    self.__logger.info(
                        'Elasticsearch index deletion failed %s', {index_id})
            else:
                raise ValueError(
                    f"Index doesn't exist: {index_id}")
        except Exception as e:
            self.__logger.exception(e)
            raise e

    def get_custom_metadata(self):
        """Return custom metadata schema"""
        try:
            record_list = []
            config_data = self.__internal_config_data
            db_server_url = config_data['db_server_url']
            authenticate = config_data['authenticate']
            username = config_data['username']
            password = config_data['password']
            verify_certs = config_data['verify_certs']
            cert_fingerprint = config_data['cert_fingerprint']
            index_id = config_data['index_id']
            ca_certs_path = os.environ.get('CA_CERTS_PATH')

            es_service_obj = ElasticSearchService(
                db_server_url, authenticate, username, password, verify_certs, cert_fingerprint, ca_certs_path, index_id)

            # Check if index exists
            index_exists = es_service_obj.check_index_exists()
            # Get all recorda if index exists else throw error
            if index_exists:
                schema = es_service_obj.get_custom_metadata_schema()
            else:
                raise ValueError(
                    f"Index doesn't exist: {index_id}")

            return schema

        except Exception as e:
            self.__logger.exception(e)
            raise e

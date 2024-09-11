# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

"""Module for FAISS vector DB provider"""

import os
import logging
from typing import List
import infy_fs_utils
from .faiss_service import FaissService
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
    db_folder_path: str
    db_index_name: str


class InsertVectorDbRecordData(BaseVectorDbRecordData):
    """Domain class"""
    content_file_path: str = None


class MatchingVectorDbRecordData(BaseVectorDbRecordData):
    """Domain class"""
    db_folder_path: str = None
    score: float = None


class VectorDbRecordData(BaseVectorDbRecordData):
    """Domain class"""


class VectorDbQueryParamsData(BaseVectorDbQueryParamsData):
    """Domain class"""


class FaissVectorDbProvider(IVectorDbProvider):
    """FAISS vector DB provider"""

    __DB_TYPE = "FAISS"

    def __init__(self, config_data: VectorDbProviderConfigData, embedding_provider: IEmbeddingProvider) -> None:
        if infy_fs_utils.manager.FileSystemLoggingManager().has_fs_logging_handler(
                Constants.FSLH_GEN_AI_SDK):
            self.__logger = infy_fs_utils.manager.FileSystemLoggingManager(
            ).get_fs_logging_handler(Constants.FSLH_GEN_AI_SDK).get_logger()
        else:
            self.__logger = logging.getLogger(__name__)

        self.__app_config = AppConfigManager().get_app_config()
        self.__fs_handler = infy_fs_utils.manager.FileSystemManager(
        ).get_fs_handler(Constants.FSH_GEN_AI_SDK)
        super().__init__(db_type=self.__DB_TYPE, embedding_provider=embedding_provider)
        # Convert pydantic to dict for flexibility
        self.__config_data = dict(config_data)
        self.__internal_config_data = self.__localize_db(
            self.__config_data)
        # Create container folders if not present
        app_container_folders = [self.__app_config["CONTAINER"]["APP_DIR_DATA_PATH"],
                                 self.__app_config["CONTAINER"]["APP_DIR_TEMP_PATH"]]
        for app_container_folder in app_container_folders:
            FileUtil.create_dirs_if_absent(app_container_folder)

    def get_matches(self, query_params_data: VectorDbQueryParamsData) -> List[MatchingVectorDbRecordData]:
        try:
            config_data = self.__internal_config_data
            scores_list = []
            sorted_scores_list = []
            db_folder_path_for_load = config_data.get(
                'local_db_folder_path', config_data['db_folder_path'])
            if not os.path.exists(db_folder_path_for_load):
                raise ValueError(
                    f"File doesn't exist: {db_folder_path_for_load}")
            faiss_service_obj = FaissService(
                db_folder_path_for_load, config_data['db_index_name'])
            faiss_service_obj.load_local()

            query = query_params_data.query
            filter_metadata = query_params_data.filter_metadata
            top_k = query_params_data.top_k
            pre_filter_fetch_k = query_params_data.pre_filter_fetch_k

            embedding_data: EmbeddingData = self._embedding_provider.generate_embedding(
                query)

            records = faiss_service_obj.search_records(
                embedding_data.vector, top_k, filter_metadata, pre_filter_fetch_k)
            # print(f"Query: {query}")
            for record in records:
                # print(
                #     f"Distance: {record['distance']}, Document: {record['content']}")
                vector_db_record_data_dict = {"db_folder_path": config_data['db_folder_path'],
                                              'content': record['content'],
                                              'metadata': record['metadata'],
                                              "score": record['distance']}
                scores_list.append(MatchingVectorDbRecordData(
                    **vector_db_record_data_dict))
            sorted_scores_list = sorted(scores_list, key=lambda d: d.score)
            self.__logger.debug("Sorted scores list size: %s",
                                len(sorted_scores_list))
        except Exception as e:
            self.__logger.exception(e)
            raise e

        return sorted_scores_list

    def save_record(self, db_record_data: InsertVectorDbRecordData):
        try:
            config_data = self.__internal_config_data
            db_folder_path = config_data['db_folder_path']
            local_db_folder_path = config_data['local_db_folder_path']
            db_index_name = config_data['db_index_name']

            local_content_file_path = f'{self.__app_config["CONTAINER"]["APP_DIR_TEMP_PATH"]}/{FileUtil.get_uuid()}'

            content_file_path = db_record_data.content_file_path
            with self.__fs_handler.get_file_object(content_file_path) as file:
                with open(local_content_file_path, "wb") as output:
                    output.write(file.read())

            with open(local_content_file_path, 'r', encoding='utf-8') as file:
                content = file.read()

            embedding_data: EmbeddingData = self._embedding_provider.generate_embedding(
                content)
            faiss_service_obj = FaissService(
                local_db_folder_path, db_index_name)
            if os.path.exists(local_db_folder_path):
                faiss_service_obj.load_local()
            else:
                faiss_service_obj.create_new(embedding_data.vector_dimension)

            metadata = {
                'source': content_file_path
            }
            metadata.update(db_record_data.metadata)
            faiss_service_obj.add_record(
                embedding_data.vector, content, metadata)

            faiss_service_obj.save_local()
            total_no_of_records = faiss_service_obj.get_record_count()
            self.__logger.info(
                'Total # of records in DB: %s', total_no_of_records)

            # Upload vector db if storage is cloud file system
            if self.__fs_handler.get_scheme() != infy_fs_utils.interface.IFileSystemHandler.SCHEME_TYPE_FILE:
                self.__fs_handler.put_folder(
                    local_db_folder_path, db_folder_path)
                self.__logger.debug("Uploaded DB to %s", db_folder_path)

        except Exception as e:
            self.__logger.exception(e)
            raise e

    def get_records(self, count: int = -1) -> List[VectorDbRecordData]:
        try:
            config_data = self.__internal_config_data
            db_folder_path_for_load = config_data.get(
                'local_db_folder_path', config_data['db_folder_path'])
            if not os.path.exists(db_folder_path_for_load):
                raise ValueError(
                    f"File doesn't exist: {db_folder_path_for_load}")
            faiss_service_obj = FaissService(
                db_folder_path_for_load, config_data['db_index_name'])
            faiss_service_obj.load_local()
            records = faiss_service_obj.get_records(end=count)
            record_list = []
            processed_count = 0
            for record in records:
                vector_db_record_data_dict = {
                    'id': record['id'],
                    'content': record['content'],
                    'metadata': record['metadata']
                }
                record_list.append(VectorDbRecordData(
                    **vector_db_record_data_dict))
                processed_count += 1
                if count > -1 and processed_count >= count:
                    break
        except Exception as e:
            self.__logger.exception(e)
            raise e
        return record_list

    ######## Private Methods #############

    def __localize_db(self, config_data):
        """Creates a local version of cloud DB OR updates absolute path for local DB."""
        _config_data = config_data.copy()
        storage_uri = self.__fs_handler.get_storage_root_uri()
        db_folder_path = _config_data['db_folder_path']
        # Download to local if storage is cloud file system
        if self.__fs_handler.get_scheme() != infy_fs_utils.interface.IFileSystemHandler.SCHEME_TYPE_FILE:
            local_container_folder_path = f'{self.__app_config["CONTAINER"]["APP_DIR_TEMP_PATH"]}/{FileUtil.get_uuid()}'
            FileUtil.create_dirs_if_absent(local_container_folder_path)
            if self.__fs_handler.exists(db_folder_path):
                self.__fs_handler.get_folder(
                    db_folder_path, local_container_folder_path)
            local_db_folder_path = local_container_folder_path + '/' + \
                os.path.basename(db_folder_path)
            _config_data['local_db_folder_path'] = local_db_folder_path
            self.__logger.debug("Downloaded %s to %s",
                                db_folder_path, local_db_folder_path)
        else:  # Skip download, just update path if storage is local file system
            _config_data['local_db_folder_path'] = storage_uri.replace(
                self.__fs_handler.get_scheme() + '://', '') + db_folder_path

        return _config_data

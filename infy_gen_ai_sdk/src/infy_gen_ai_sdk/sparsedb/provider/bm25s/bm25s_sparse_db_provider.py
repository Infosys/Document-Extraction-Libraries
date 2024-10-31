# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#
"""Module for Bm25s Sparse DB provider"""

import os
import json
import logging
import shutil
from typing import Optional
import infy_fs_utils
import numpy as np
from .bm25s_service import Bm25sService
from ....common.app_config_manager import AppConfigManager
from ....common.file_util import FileUtil
from ....schema.sparse_db_data import BaseSparseDbConfigData, BaseSparseDbSaveRecordData, BaseSparseDbRecordData, BaseSparseDbQueryParamsData, BaseSparseDbMacthesData
from ...interface.i_sparse_db_provider import ISparseDbProvider
from ....common import Constants


class SparseDbProviderConfigData(BaseSparseDbConfigData):
    """Domain class"""
    db_folder_path: str = None
    db_index_name: str = None
    db_index_secret_key: Optional[str] = None

class SparseDbRecordConfigData(BaseSparseDbSaveRecordData):
    """Domain class"""
    content_file_path: str
    metadata: dict = None
    
class SparseDbRecordData(BaseSparseDbRecordData):
    """Domain class"""

class SparseDbQueryParamsData(BaseSparseDbQueryParamsData):
    """Domain class"""
    
class SparseDbMatchesRecordData(BaseSparseDbMacthesData):
    """Domain class"""

class Bm25sSparseDbProvider(ISparseDbProvider):
    """BM25S Sparse DB provider"""

    def __init__(self, config_data: SparseDbProviderConfigData, ) -> None:
        if infy_fs_utils.manager.FileSystemLoggingManager().has_fs_logging_handler(
                Constants.FSLH_GEN_AI_SDK):
            self.__logger = infy_fs_utils.manager.FileSystemLoggingManager(
            ).get_fs_logging_handler(Constants.FSLH_GEN_AI_SDK).get_logger()
        else:
            self.__logger = logging.getLogger(__name__)

        self.__app_config = AppConfigManager().get_app_config()
        self.__fs_handler = infy_fs_utils.manager.FileSystemManager(
        ).get_fs_handler(Constants.FSH_GEN_AI_SDK)
        # Convert pydantic to dict for flexibility
        self.__config_data = config_data.dict()
        # Create container folders if not present
        app_container_folders = [self.__app_config["CONTAINER"]["APP_DIR_DATA_PATH"],
                                 self.__app_config["CONTAINER"]["APP_DIR_TEMP_PATH"]]
        for app_container_folder in app_container_folders:
            FileUtil.create_dirs_if_absent(app_container_folder)

    def save_record(self, sparse_record_config_dict: SparseDbRecordConfigData):
        try:
            config_data = self.__config_data
            db_folder_path = config_data.get('db_folder_path', '')
            db_index_name = config_data.get('db_index_name','')
            db_index_secret_key = config_data.get('db_index_secret_key', None)
            sparse_record_config_dict = sparse_record_config_dict.dict()
            if os.environ.get("NLTK_DATA_DIR"):
                nltk_data_dir = os.environ.get("NLTK_DATA_DIR")
            else:
                raise ValueError("Please set NLTK_DATA_DIR path.")

            content_file_path = sparse_record_config_dict.get('content_file_path','')
            metadata = sparse_record_config_dict.get('metadata','')
            
            chunk_list = []
            chunk = self.__fs_handler.read_file(content_file_path)
            chunk_list.append(chunk)

            metadata_list = []
            metadata_list.append(metadata)
            
            corpus = []
            for chunk, metadata in zip(chunk_list, metadata_list):
                try:
                    metadata = json.loads(metadata)
                except (json.JSONDecodeError, TypeError):
                    pass
                item = {"text": chunk, "metadata": metadata}
                corpus.append(item)
            
            retriever={}
            local_db_folder_path = self.__fs_handler.get_abs_path(db_folder_path).replace('filefile://', '')
            bm25s_service_obj = Bm25sService(
                self.__fs_handler, db_folder_path, local_db_folder_path, db_index_name, db_index_secret_key)
            
            if os.path.exists(local_db_folder_path) and os.path.exists(f'{local_db_folder_path}/{db_index_name}/corpus.jsonl'):
                retriever = bm25s_service_obj.load_local()
                retriever = bm25s_service_obj.add_record(retriever,nltk_data_dir,chunk_list,corpus)
            else:
                retriever = bm25s_service_obj.create_new(nltk_data_dir,chunk_list, corpus)
                
            bm25s_service_obj.save_local(retriever)
            
            records = bm25s_service_obj.get_records(retriever)
            self.__logger.info(
                'Total # of records in DB: %s', len(records)) 
        
        except Exception as e:
            self.__logger.exception(e)
            raise e
        
    def get_records(self):
        try:
            config_data = self.__config_data
            db_folder_path = config_data.get('db_folder_path', '')
            db_index_name = config_data.get('db_index_name','')
            db_index_secret_key = config_data.get('db_index_secret_key', None)
            
            retriever={}
            local_db_folder_path = self.__fs_handler.get_abs_path(db_folder_path).replace('filefile://', '')
            local_db_index_path = f'{local_db_folder_path}/{db_index_name}'
            
            if os.path.exists(local_db_folder_path) and os.path.exists(local_db_index_path) and os.path.exists(f'{local_db_index_path}/corpus.jsonl'):
                bm25s_service_obj = Bm25sService(
                self.__fs_handler, db_folder_path, local_db_folder_path, db_index_name, db_index_secret_key)
                
                retriever = bm25s_service_obj.load_local()
                records = bm25s_service_obj.get_records(retriever)
                
                record_list = []
                for record in records:
                    sparse_db_record_data_dict = {
                        'content': record['content'],
                        'metadata': record['metadata']
                    }
                    record_list.append(SparseDbRecordData(
                        **sparse_db_record_data_dict))
                return record_list
            else:
                raise ValueError("Collection doesn't exist.")
            
        except Exception as e:
            self.__logger.exception(e)
            raise e

    def get_matches(self, query_params_data: SparseDbQueryParamsData):
        try:
            config_data = self.__config_data
            db_folder_path = config_data.get('db_folder_path', '')
            db_index_name = config_data.get('db_index_name','')
            db_index_secret_key = config_data.get('db_index_secret_key', None)
            query_params_data = query_params_data.dict()
            if os.environ.get("NLTK_DATA_DIR"):
                nltk_data_dir = os.environ.get("NLTK_DATA_DIR")
            else:
                raise ValueError("Please set NLTK_DATA_DIR path.")
            
            query = query_params_data.get('query', '')
            top_k = query_params_data.get('top_k', 1)
            filter_metadata = query_params_data.get('filter_metadata', {})
            pre_filter_fetch_k = query_params_data.get('pre_filter_fetch_k', top_k*top_k)
            local_db_folder_path = self.__fs_handler.get_abs_path(db_folder_path).replace('filefile://', '')
                        
            if os.path.exists(local_db_folder_path) and os.path.exists(f'{local_db_folder_path}/{db_index_name}/corpus.jsonl'):

                bm25s_service_obj = Bm25sService(
                    self.__fs_handler, db_folder_path, local_db_folder_path, db_index_name, db_index_secret_key)

                retriever = bm25s_service_obj.load_local()
                records = bm25s_service_obj.search_records(retriever, nltk_data_dir, query, top_k, pre_filter_fetch_k)         
                record_list = []
                if filter_metadata:
                    for i in range(len(records[0][0])):
                        record_metadata = records[0][0][i].get('metadata', {})
                        if all(record_metadata.get(key) == value for key, value in filter_metadata.items()): 
                            sparse_db_record_data_dict = {
                                "db_folder_path": config_data['db_folder_path'],
                                'content': records[0][0][i].get('text',''),
                                'metadata': records[0][0][i].get('metadata',{}),
                                'score': float(records[1][0][i]) if isinstance(records[1][0][i], np.float32) else records[1][0][i],
                            }
                            record_list.append(SparseDbMatchesRecordData(
                                **sparse_db_record_data_dict))
                else:
                    for i in range(len(records[0][0])):
                        record_metadata = records[0][0][i].get('metadata', {})
                        sparse_db_record_data_dict = {
                                "db_folder_path": config_data['db_folder_path'],
                                'content': records[0][0][i].get('text',''),
                                'metadata': records[0][0][i].get('metadata',{}),
                                'score': float(records[1][0][i]) if isinstance(records[1][0][i], np.float32) else records[1][0][i],
                            }
                        record_list.append(SparseDbMatchesRecordData(
                            **sparse_db_record_data_dict))
                        
                if len(record_list) > top_k:
                    record_list = record_list[:top_k]
                    
                return record_list
            else:
                raise ValueError(
                    "Collection does not exist.")           

        except Exception as e:
            self.__logger.exception(e)
            raise e

    def delete_records(self):
        try:
            config_data = self.__config_data
            db_folder_path = config_data.get('db_folder_path', '')
            db_index_name = config_data.get('db_index_name','')
            db_index_secret_key = config_data.get('db_index_secret_key', None)

            local_db_folder_path = self.__fs_handler.get_abs_path(db_folder_path).replace('filefile://', '')
            
            if os.path.exists(local_db_folder_path) and os.path.exists(f'{local_db_folder_path}/{db_index_name}/corpus.jsonl'):
                bm25s_service_obj = Bm25sService(
                    self.__fs_handler, db_folder_path, local_db_folder_path, db_index_name, db_index_secret_key)
                
                records_dict = bm25s_service_obj.delete_local()
                if records_dict:
                    folder_path = records_dict.get('folder_path', '')
                    secret_key_path = records_dict.get('secret_key_path', '')
                    if secret_key_path:
                        self.__fs_handler.delete_file(secret_key_path)
                    if folder_path:
                        shutil.rmtree(folder_path)
            else:
                raise ValueError(
                    "Collection does not exist.")           

        except Exception as e:
            self.__logger.exception(e)
            raise e          

  
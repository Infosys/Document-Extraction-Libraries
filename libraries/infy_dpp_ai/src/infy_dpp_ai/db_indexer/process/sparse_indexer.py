# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import os
import json
import infy_fs_utils
import infy_dpp_sdk
import infy_gen_ai_sdk


class SparseIndexer:
    """SparseIndexer class is used to index data to sparse database.
    """

    def __init__(self, sparse_storage, sparse_storage_config, chunk_data, document_id, index_id,  file_sys_handler, logger, app_config) -> None:
        self.sparse_storage = sparse_storage
        self.chunk_data = chunk_data
        self.document_id = document_id
        self.sparse_index_root_path = sparse_storage_config.get(
            "sparse_index_root_path", '')
        self.sparse_db_name = sparse_storage_config.get(
            "db_name", '')
        self.nltk_data_dir = sparse_storage_config.get(
            "nltk_data_dir", '')
        self.sparse_collections = sparse_storage_config.get(
            "collections", [])
        self.db_service_url = sparse_storage_config.get(
            "db_service_url", '')
        self.method_name = sparse_storage_config.get(
            "method_name", '')
        self.index_id = index_id

        self.__logger = logger
        self.__app_config = app_config
        self.__file_sys_handler = file_sys_handler

    def create_index(self):
        encoded_path_list = []
        encoded_path = ''
        if self.sparse_storage == 'bm25s':
            os.environ["NLTK_DATA_DIR"] = self.nltk_data_dir
            if self.sparse_db_name:
                server_faiss_write_path = f'{self.sparse_index_root_path}/{self.sparse_storage}/{self.sparse_db_name}'
            else:
                server_faiss_write_path = f'{self.sparse_index_root_path}/{self.sparse_storage}/{self.document_id}'
            # index-id
            if self.index_id:
                server_faiss_write_path = f'{server_faiss_write_path}/{self.index_id}'
            # index-id

            if self.sparse_collections:
                for collection in self.sparse_collections:
                    sparse_db_provider_config_data = infy_gen_ai_sdk.sparsedb.provider.bm25s.SparseDbProviderConfigData(
                        **{
                            'db_folder_path': server_faiss_write_path,
                            'db_index_name': collection.get('collection_name', self.sparse_db_name) or self.document_id,
                            'db_index_secret_key': collection.get('collection_secret_key', '')
                        })
                    sparse_db_provider = infy_gen_ai_sdk.sparsedb.provider.bm25s.Bm25sSparseDbProvider(
                        sparse_db_provider_config_data)

                    for _key, chunked_method in self.chunk_data.items():
                        for text_file_path in chunked_method.get('chunked_data_list'):
                            if f'{text_file_path}_metadata.json' in chunked_method.get('chunked_file_meta_data_list'):
                                metadata_file_path = f'{text_file_path}_metadata.json'
                                if metadata_file_path in chunked_method.get('chunked_file_meta_data_list', []):
                                    metadata = json.loads(
                                        self.__file_sys_handler.read_file(metadata_file_path))
                                else:
                                    metadata = {}

                                chunk_type = collection.get('chunk_type')
                                if chunk_type:
                                    if chunk_type == metadata.get('chunking_method'):
                                        # Add record(s) to sparse db
                                        db_record_data_dict = {
                                            'content_file_path': text_file_path,
                                            'metadata': metadata
                                        }
                                        db_record_data = infy_gen_ai_sdk.sparsedb.provider.bm25s.SparseDbRecordConfigData(
                                            **db_record_data_dict)
                                        sparse_db_provider.save_record(
                                            db_record_data)
                                elif chunk_type is None or chunk_type == '':
                                    # Add record(s) to sparse db
                                    db_record_data_dict = {
                                        'content_file_path': text_file_path,
                                        'metadata': metadata
                                    }
                                    db_record_data = infy_gen_ai_sdk.sparsedb.provider.bm25s.SparseDbRecordConfigData(
                                        **db_record_data_dict)
                                    sparse_db_provider.save_record(
                                        db_record_data)

                    encoded_path_list.append(server_faiss_write_path)
            elif not self.sparse_collections:
                sparse_db_provider_config_data = infy_gen_ai_sdk.sparsedb.provider.bm25s.SparseDbProviderConfigData(
                    **{
                        'db_folder_path': server_faiss_write_path,
                        'db_index_name': self.sparse_db_name if self.sparse_db_name else self.document_id,
                        'db_index_secret_key': ''
                    })
                sparse_db_provider = infy_gen_ai_sdk.sparsedb.provider.bm25s.Bm25sSparseDbProvider(
                    sparse_db_provider_config_data)

                for _key, chunked_method in self.chunk_data.items():
                    for text_file_path in chunked_method.get('chunked_data_list'):
                        if f'{text_file_path}_metadata.json' in chunked_method.get('chunked_file_meta_data_list'):
                            metadata_file_path = f'{text_file_path}_metadata.json'
                            if metadata_file_path in chunked_method.get('chunked_file_meta_data_list', []):
                                metadata = json.loads(
                                    self.__file_sys_handler.read_file(metadata_file_path))
                            else:
                                metadata = {}

                            # Add record(s) to vector db
                            db_record_data_dict = {
                                'content_file_path': text_file_path,
                                'metadata': metadata
                            }
                            db_record_data = infy_gen_ai_sdk.sparsedb.provider.bm25s.SparseDbRecordConfigData(
                                **db_record_data_dict)
                            sparse_db_provider.save_record(
                                db_record_data)

                encoded_path_list.append(server_faiss_write_path)
        elif self.sparse_storage == 'infy_db_service':
            if self.sparse_collections:
                for collection in self.sparse_collections:
                    sparse_db_provider_config_data = infy_gen_ai_sdk.sparsedb.provider.online.OnlineSparseDbProviderConfigData(
                        **{
                            'db_service_url': self.db_service_url,
                            'method_name': self.method_name,
                            'index_id': self.index_id,
                            "collection_name": collection.get('collection_name', self.sparse_db_name) or self.document_id,
                            "collection_secret_key": collection.get('collection_secret_key', '')
                        })
                    sparse_db_provider = infy_gen_ai_sdk.sparsedb.provider.online.OnlineSparseDbProvider(
                        sparse_db_provider_config_data)

                    for _key, chunked_method in self.chunk_data.items():
                        for text_file_path in chunked_method.get('chunked_data_list'):
                            if f'{text_file_path}_metadata.json' in chunked_method.get('chunked_file_meta_data_list'):
                                metadata_file_path = f'{text_file_path}_metadata.json'
                                if metadata_file_path in chunked_method.get('chunked_file_meta_data_list', []):
                                    metadata = json.loads(
                                        self.__file_sys_handler.read_file(metadata_file_path))
                                    content = self.__file_sys_handler.read_file(
                                        text_file_path)
                                else:
                                    metadata = {}

                                chunk_type = collection.get('chunk_type')
                                if chunk_type:
                                    if chunk_type == metadata.get('chunking_method'):
                                        # Add record(s) to sparse db
                                        db_record_data_dict = {
                                            'content': content,
                                            'metadata': metadata
                                        }
                                        db_record_data = infy_gen_ai_sdk.sparsedb.provider.online.InsertSparseDbRecordData(
                                            **db_record_data_dict)
                                        encoded_path = sparse_db_provider.save_record(
                                            db_record_data)
                                elif chunk_type is None or chunk_type == '':
                                    # Add record(s) to sparse db
                                    db_record_data_dict = {
                                        'content': content,
                                        'metadata': metadata
                                    }
                                    db_record_data = infy_gen_ai_sdk.sparsedb.provider.online.InsertSparseDbRecordData(
                                        **db_record_data_dict)
                                    encoded_path = sparse_db_provider.save_record(
                                        db_record_data)

                    encoded_path_list.append(encoded_path)
            elif not self.sparse_collections:
                raise ValueError(
                    "Sparse collections not provided for infy_db_service storage")
        else:
            raise ValueError(
                f"Sparse storage type: {self.sparse_storage} not supported.")
        return encoded_path_list

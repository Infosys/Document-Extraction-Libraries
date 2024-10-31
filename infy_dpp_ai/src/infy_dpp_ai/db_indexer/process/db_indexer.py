# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#
import time
import concurrent.futures
import infy_fs_utils
import infy_gen_ai_sdk
import infy_dpp_sdk
from infy_dpp_sdk.data import DocumentData, ProcessorResponseData
from infy_dpp_ai.db_indexer.process.sparse_indexer import SparseIndexer
from infy_dpp_ai.db_indexer.process.vector_indexer import VectorIndexer


PROCESSEOR_CONTEXT_DATA_NAME = "db_indexer"


class DbIndexer(infy_dpp_sdk.interface.IProcessor):
    def __init__(self):
        self.__logger = self.get_logger()
        self.__file_sys_handler: infy_fs_utils.interface.IFileSystemHandler = self.get_fs_handler()
        client_config_data_dict = infy_dpp_sdk.ClientConfigManager().get().dict()

        if not infy_fs_utils.manager.FileSystemManager().has_fs_handler(infy_gen_ai_sdk.common.Constants.FSH_GEN_AI_SDK):
            infy_fs_utils.manager.FileSystemManager().add_fs_handler(
                infy_fs_utils.provider.FileSystemHandler(
                    self.__file_sys_handler.get_storage_config_data()),
                infy_gen_ai_sdk.common.Constants.FSH_GEN_AI_SDK)
        client_config_data = infy_gen_ai_sdk.ClientConfigData(
            **client_config_data_dict)
        infy_gen_ai_sdk.ClientConfigManager().load(client_config_data)

    def do_execute(self, document_data: DocumentData, context_data: dict, config_data: dict) -> ProcessorResponseData:
        processor_response_data = infy_dpp_sdk.data.ProcessorResponseData()
        context_data = context_data if context_data else {}
        __processor_config_data = config_data.get('DbIndexer', {})

        # for parallel processing
        if not __processor_config_data:
            for key, val in config_data.items():
                __processor_config_data = val
                break
        else:
            context_data[PROCESSEOR_CONTEXT_DATA_NAME] = {}

        document_id = document_data.document_id
        chunk_data = context_data.get('chunk_generator')
        vector_index_path, vector_storage = None, None
        sparse_index_path, sparse_storage = None, None
        vector_index_obj, sparse_index_obj = None, None
        index_id = ''

        for key, value in __processor_config_data.items():
            if key == 'index' and value.get('enabled'):
                index_name = value.get('index_name', '')
                if index_name:
                    group_request_id = context_data.get(
                        'request_creator', {}).get('group_request_id', '').strip()
                    group_request_id = group_request_id.split(
                        'G')[1][:24] if group_request_id else ''
                    index_id = f"{index_name}{group_request_id}" if group_request_id else ''
                else:
                    index_id = value.get('index_id')
            if key == 'embedding':
                for e_key, e_val in value.items():
                    if e_val.get('enabled'):
                        get_llm = e_key
                        get_llm_config = e_val.get('configuration')
                        model_name = get_llm_config.get("model_name")
            if key == 'storage':
                for storage_key, storage_value in value.items():
                    if storage_key == 'vectordb':
                        for e_key, e_val in storage_value.items():
                            if e_key and e_val.get('enabled'):
                                vector_storage = e_key
                                vector_storage_config = e_val.get(
                                    'configuration', {})
                                distance_metric = vector_storage_config.get(
                                    "distance_metric")
                                if distance_metric is not None:
                                    for key, value in distance_metric.items():
                                        if value is True:
                                            distance_metric = key
                                            break
                                vector_index_obj = VectorIndexer(
                                    vector_storage, vector_storage_config, get_llm, get_llm_config,  model_name, chunk_data, document_id, index_id)
                                break

                    if storage_key == 'sparseindex':
                        sparse_index_path = None
                        sparse_storage = None
                        for e_key, e_val in storage_value.items():
                            if e_key and e_val.get('enabled'):
                                sparse_storage = e_key
                                sparse_storage_config = e_val.get(
                                    'configuration', {})
                                sparse_index_obj = SparseIndexer(
                                    sparse_storage, sparse_storage_config, chunk_data, document_id, index_id)
                                break

        # Parallel index creation
        start = time.time()
        self.__logger.debug("Index creation started: %s", start)
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            if vector_index_obj:
                futures.append(executor.submit(
                    lambda: ('vector', vector_index_obj.create_index())))
            if sparse_index_obj:
                futures.append(executor.submit(
                    lambda: ('sparse', sparse_index_obj.create_index())))

            for future in concurrent.futures.as_completed(futures):
                result_type, result_path = future.result()
                if result_path:
                    if result_type == 'vector':
                        vector_index_path = result_path
                    elif result_type == 'sparse':
                        sparse_index_path = result_path
        end = time.time()
        self.__logger.debug("Index creation finished: %s", end)

        if vector_index_path and vector_storage:
            if 'DbIndexer' in config_data:
                context_data[PROCESSEOR_CONTEXT_DATA_NAME]['vector_db'] = {
                    'encoded_path_list': vector_index_path,
                    'embedding_model': model_name,
                    'distance_metric': distance_metric or 'eucledian',
                    'index_id': index_id
                }
            else:
                context_data[PROCESSEOR_CONTEXT_DATA_NAME+'_vector'] = {}
                context_data[PROCESSEOR_CONTEXT_DATA_NAME+'_vector']['vector_db'] = {
                    'encoded_path_list': vector_index_path,
                    'embedding_model': model_name,
                    'distance_metric': distance_metric or 'eucledian',
                    'index_id': index_id
                }

        if sparse_index_path and sparse_storage:
            if 'DbIndexer' in config_data:
                context_data[PROCESSEOR_CONTEXT_DATA_NAME]['sparse_index'] = {
                    'sparse_index_path': sparse_index_path,
                    'sparse_storage': sparse_storage,
                    'index_id': index_id
                }
            else:
                context_data[PROCESSEOR_CONTEXT_DATA_NAME+'_sparse'] = {}
                context_data[PROCESSEOR_CONTEXT_DATA_NAME+'_sparse']['sparse_index'] = {
                    'sparse_index_path': sparse_index_path,
                    'sparse_storage': sparse_storage,
                    'index_id': index_id
                }

        # Populate response data
        processor_response_data.document_data = document_data
        processor_response_data.context_data = context_data

        return processor_response_data

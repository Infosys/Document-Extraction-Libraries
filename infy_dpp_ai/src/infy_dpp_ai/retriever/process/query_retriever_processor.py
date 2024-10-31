# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import time
import concurrent.futures
import infy_dpp_sdk
from infy_dpp_sdk.data import DocumentData, ProcessorResponseData
import infy_gen_ai_sdk
import infy_fs_utils

from infy_dpp_ai.retriever.process.query_vectordb import QueryVectordb
from infy_dpp_ai.retriever.process.query_sparseindex import QuerySparseIndex
from infy_dpp_ai.retriever.process.query_hybrid_rrf import QueryHybridRrf

PROCESSOR_CONTEXT_DATA_NAME = "query_retriever"


class QueryRetriever(infy_dpp_sdk.interface.IProcessor):
    def __init__(self):
        self.__file_sys_handler: infy_fs_utils.interface.IFileSystemHandler = self.get_fs_handler()
        self.__logger = self.get_logger()

        if not infy_fs_utils.manager.FileSystemManager().has_fs_handler(infy_gen_ai_sdk.common.Constants.FSH_GEN_AI_SDK):
            infy_fs_utils.manager.FileSystemManager().add_fs_handler(
                infy_fs_utils.provider.FileSystemHandler(
                    self.__file_sys_handler.get_storage_config_data()),
                infy_gen_ai_sdk.common.Constants.FSH_GEN_AI_SDK)
        client_config_data_dict = infy_dpp_sdk.ClientConfigManager().get().dict()
        client_config_data = infy_gen_ai_sdk.ClientConfigData(
            **client_config_data_dict)
        infy_gen_ai_sdk.ClientConfigManager().load(client_config_data)

        self.vectordb = QueryVectordb(self.__file_sys_handler, self.__logger)
        self.sparseindex = QuerySparseIndex(
            self.__file_sys_handler, self.__logger)

    def do_execute(self, document_data: DocumentData, context_data: dict, config_data: dict) -> ProcessorResponseData:
        processor_response_data = infy_dpp_sdk.data.ProcessorResponseData()
        processor_config_data = config_data.get('QueryRetriever', {})
        context_data = context_data if context_data else {}
        document_id = document_data.document_id
        results = []
        start = time.time()
        self.__logger.debug("Retrieval started: %s", start)
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            futures.append(executor.submit(self.vectordb.query_vectordb,
                                           PROCESSOR_CONTEXT_DATA_NAME, processor_response_data, processor_config_data, context_data, document_data, document_id))
            futures.append(executor.submit(self.sparseindex.query_sparsedb,
                                           PROCESSOR_CONTEXT_DATA_NAME, processor_response_data, processor_config_data, context_data, document_data, document_id))
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result is not None:
                    results.append(result)
        end = time.time()
        self.__logger.debug("Retrieval Finished: %s", end)

        queries_list = []
        for result in results:
            for item in result:
                existing_entry = next(
                    (entry for entry in queries_list if entry["attribute_key"] == item["attribute_key"] and entry["question"] == item["question"]), None)
                if existing_entry:
                    # If it exists, append only the top_k_matches
                    existing_entry["top_k_matches"].append(
                        item['top_k_matches'])
                    existing_entry.update({k: item[k] for k in ["embedding_model", "distance_metric"] if existing_entry[k] in [
                                          '', None] and item[k] not in ['', None]})
                else:
                    queries_list.append({
                        "attribute_key": item["attribute_key"],
                        "question": item['question'],
                        "embedding_model": item['embedding_model'],
                        "distance_metric": item['distance_metric'],
                        "top_k": item['top_k'],
                        "top_k_matches": [item['top_k_matches']]
                    })

        for key, value in processor_config_data.items():
            if key == 'hybrid_search':
                for hybrid_key, hybrid_value in value.items():
                    if hybrid_key == 'rrf':
                        if hybrid_value.get('enabled'):
                            rrf_obj = QueryHybridRrf()
                            queries_list = rrf_obj.query_rrf(
                                queries_list)

        context_data[PROCESSOR_CONTEXT_DATA_NAME] = {
            'queries': queries_list}

        # Populate response data
        processor_response_data.document_data = document_data
        processor_response_data.context_data = context_data

        return processor_response_data

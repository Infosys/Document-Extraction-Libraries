# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import os
import json
import time
import uuid
from datetime import datetime, timezone
import fastapi
import infy_fs_utils
import infy_dpp_sdk
from schema.test_req_res_data import (
    QnARequestData, QnAResponseData, QueryResponseData)
from schema.base_req_res_data import (ResponseCode, ResponseMessage)
from .b_controller import BController
from common.app_config_manager import AppConfigManager


class TestController(BController):
    """Perform search on a database using a database"""

    __CONTROLLER_PATH = "/test"

    def __init__(self, context_root_path: str = ''):
        super().__init__(context_root_path=context_root_path,
                         controller_path=self.__CONTROLLER_PATH)
        self.get_router().add_api_route(
            "/search", self.Test_document, methods=["POST"], summary="Perform search on a database",
            tags=["test"],
            response_model=QnAResponseData)

    def Test_document(self, QnA_request_data: QnARequestData,
                      request: fastapi.Request
                      ):
        app_config = AppConfigManager().get_app_config()
        file_sys_handler = infy_fs_utils.manager.FileSystemManager(
        ).get_fs_handler()
        start_time = time.time()
        date = datetime.now(timezone.utc)
        date_time_stamp = date.strftime("%Y-%m-%d %I:%M:%S %p")

        input_data = QnA_request_data.dict()
        working_file_path_list = ['documents']
        datasource = input_data.get("retrieval", {}).get("datasource", {})
        config_file_path = app_config['STORAGE']["dpp_input_config_file_path"]
        if len(datasource) == 0:
            response_data = QnAResponseData(
                response={},
                responseCde=ResponseCode.CLIENT_FAILURE,
                responseMsg="ERROR: Please provide valid Database name.",
                timestamp=datetime.now(timezone.utc),
            )
        elif not input_data.get("question", "").strip():
            response_data = QnAResponseData(
                response={},
                responseCde=ResponseCode.CLIENT_FAILURE,
                responseMsg="ERROR: Please provide Question.",
                timestamp=datetime.now(timezone.utc),
            )
        else:
            document_id_list = [os.path.basename(x)
                                for x in working_file_path_list]
            answers = []
            input_config_data = json.loads(file_sys_handler.read_file(
                config_file_path))

            # STEP 1: Set the pipeline to run only retriever or retriever and reader
            retriever_enabled = input_data.get('retrieval', {}).get(
                'enabled', True)
            generation_enabled = input_data.get('generation', {}).get(
                'enabled', True)
            processor_list_config_data = input_config_data['processor_list']
            processor_list_config_data[0]['enabled'] = retriever_enabled
            processor_list_config_data[1]['enabled'] = generation_enabled

            # STEP 2: Form the query dict
            retriever_query_config_data = input_config_data[
                'processor_input_config']['QueryRetriever']['queries'][0]
            query_dict = {
                "attribute_key": "generic_attribute_key",
                "question": input_data["question"].strip(),
                "top_k": input_data["retrieval"].get("top_k", 1),
                "pre_filter_fetch_k": input_data["retrieval"].get("pre_filter_fetch_k", 10),
                "filter_metadata": input_data["retrieval"].get("filter_metadata", {}),
                "min_distance": retriever_query_config_data.get('min_distance', 0),
                "max_distance": input_data["retrieval"].get("max_distance", 2),
            }
            input_config_data['processor_input_config']['QueryRetriever']['queries'] = [
                query_dict]

            # STEP 3: Set Datasource details
            index_id = input_data['retrieval'].get(
                'index_id', '')
            # a.vector_index
            vector_storage_config = input_config_data[
                'processor_input_config']['QueryRetriever']['storage']['vectordb']['infy_db_service']
            vector_input_data = input_data['retrieval']['datasource']['vectorindex']
            if vector_input_data.get('enabled'):
                vector_storage_config['enabled'] = True
                vector_storage_config['configuration']['model_name'] = vector_input_data.get(
                    'model_name')
                vector_storage_config['configuration']['index_id'] = index_id
                vector_storage_config['configuration']['collections'] = vector_input_data.get(
                    'collections')
            else:
                vector_storage_config['enabled'] = False

            # b.sparse_index
            sparse_storage_config = input_config_data[
                'processor_input_config']['QueryRetriever']['storage']['sparseindex']['infy_db_service']
            sparse_input_data = input_data['retrieval']['datasource']['sparseindex']
            if sparse_input_data.get('enabled'):
                sparse_storage_config['enabled'] = True
                sparse_storage_config['configuration']['method_name'] = sparse_input_data.get(
                    'method_name')
                sparse_storage_config['configuration']['index_id'] = index_id
                sparse_storage_config['configuration']['collections'] = sparse_input_data.get(
                    'collections')
            else:
                sparse_storage_config['enabled'] = False

            # STEP 4: Set Hybrid search details
            # a.rrf
            rrf_storage_config = input_config_data['processor_input_config'][
                'QueryRetriever']['hybrid_search']['rrf']
            rrf_input_data = input_data['retrieval']['hybrid_search']['rrf']
            if rrf_input_data.get('enabled'):
                rrf_storage_config['enabled'] = True
            else:
                rrf_storage_config['enabled'] = False

            # STEP 5: Set Inference details
            inference_config_data = input_config_data['processor_input_config']['Reader']
            if vector_input_data.get('enabled'):
                inference_config_data['storage']['vectordb']['infy_db_service']['enabled'] = True
            else:
                inference_config_data['storage']['vectordb']['infy_db_service']['enabled'] = False
            if sparse_input_data.get('enabled'):
                inference_config_data['storage']['sparseindex']['infy_db_service']['enabled'] = True
            else:
                inference_config_data['storage']['sparseindex']['infy_db_service']['enabled'] = False
            if rrf_input_data.get('enabled'):
                inference_config_data['hybrid_search']['rrf']['enabled'] = True
            else:
                inference_config_data['hybrid_search']['rrf']['enabled'] = False

            for llm_name, llm_detail in inference_config_data['llm'].items():
                if llm_detail.get('enabled'):
                    get_llm_config = llm_detail.get('configuration')
                    get_llm_config['temperature'] = input_data['generation']["temperature"]
                    # cache = llm_detail.get('cache', {})
                    # if cache:
                    #     cache['enabled'] = input_data['generation']["from_cache"]
            inference_config_data['inputs'][0]['top_k'] = input_data['generation']['top_k_used']
            prompt_temp_used = inference_config_data['inputs'][0]['prompt_template']
            if prompt_temp_used in inference_config_data['named_prompt_templates']:
                inference_config_data['named_prompt_templates'][prompt_temp_used][
                    'response_validation']['total_attempts'] = input_data['generation']['total_attempts']

            for document_id in document_id_list:
                metadata = infy_dpp_sdk.data.MetaData(
                    standard_data=infy_dpp_sdk.data.StandardData(
                        filepath=infy_dpp_sdk.data.ValueData()))
                document_data = infy_dpp_sdk.data.DocumentData(
                    metadata=metadata)
                document_data.document_id = document_id
                context_data = {
                }
                response_data = infy_dpp_sdk.data.ProcessorResponseData(
                    document_data=document_data, context_data=context_data)
                document_data_json = json.loads(response_data.json(indent=4))

                # Write the input config data to a temp file
                unique_filename = f"{uuid.uuid4()}_config.json"
                temp_path = f"/data/temp/{unique_filename}"
                file_sys_handler.write_file(
                    temp_path, json.dumps(input_config_data, indent=4))

                try:
                    # ---------------------Run the inference pipeline  LOGIC STARTS------------------------------ #

                    dpp_orchestrator = infy_dpp_sdk.orchestrator.OrchestratorNativeBasic(
                        input_config_file_path=temp_path)
                    response_data_list = dpp_orchestrator.run_batch([infy_dpp_sdk.data.DocumentData(**document_data_json.
                                                                                                    get('document_data'))],
                                                                    [document_data_json.get('context_data')])

                    # ---------------------Run the inference pipeline  LOGIC ENDS------------------------------ #
                    for processor_response_data in response_data_list:
                        response_data = processor_response_data.dict()
                        model_output = response_data.get('context_data', {}).get(
                            'reader', {}).get('output', [{}])[0].get('model_output', {})
                        if isinstance(model_output, dict):
                            answer = response_data.get('context_data', {}).get('reader', {}).get(
                                'output', [{}])[0].get('model_output', {}).get('answer', '')
                            chunk_id = model_output.get('sources')[0].get(
                                'chunk_id') if model_output.get('sources') else ""
                            page_num = model_output.get('sources')[0].get(
                                'page_no') if model_output.get('sources') else 0
                            segment_num = model_output.get('sources')[0].get(
                                'sequence_no') if model_output.get('sources') else 0
                        else:
                            answer = model_output
                            chunk_id = ""
                            page_num = 0
                            segment_num = 0

                        answers.append({
                            "db_name": document_id,
                            "doc_name": response_data.get('context_data', {}).get('reader', {}).get('output', [{}])[0].get('source_metadata', [{}])[0].get('doc_name', '') if response_data.get('context_data', {}).get('reader', {}).get('output', [{}])[0].get('source_metadata', [{}]) else '',
                            "answer": answer,
                            "chunk_id": chunk_id,
                            "page_num": page_num,
                            "segment_num": segment_num,
                            "source_metadata": response_data.get('context_data', {}).get('reader', {}).get('output', [{}])[0].get('source_metadata', []),
                            "embedding_model_name": response_data.get('context_data', {}).get('query_retriever', {}).get('queries', [{}])[0].get('embedding_model', ''),
                            "distance_metric": response_data.get('context_data', {}).get('query_retriever', {}).get('queries', [{}])[0].get('distance_metric', ''),
                            "top_k": input_data["retrieval"].get("top_k", 1),
                            "top_k_list": response_data.get('context_data', {}).get('query_retriever', {}).get('queries', [{}])[0].get('top_k_matches', [{}]),
                            "top_k_aggregated": response_data.get('context_data', {}).get('reader', {}).get('output', [{}])[0].get('retriever_output', [{}]).get('top_k', 0) if generation_enabled else 0,
                            "llm_model_name": response_data.get('context_data', {}).get('reader', {}).get('output', [{}])[0].get('model_name', ''),
                            "llm_total_attempts": response_data.get('context_data', {}).get('reader', {}).get('output', [{}])[0].get('total_attempts', 1) if generation_enabled else 0,
                            "llm_response": {
                                "response": json.dumps(model_output),
                                "from_cache": response_data.get('context_data', {}).get('reader', {}).get('output', [{}])[0].get('used_cache', False)
                            },
                            "llm_prompt": {
                                "prompt_template":  response_data.get('context_data', {}).get('reader', {}).get('output', [{}])[0].get('model_input', {}).get('prompt_template', ''),
                                "context": response_data.get('context_data', {}).get('reader', {}).get('output', [{}])[0].get('model_input', {}).get('template_var_to_value_dict', {}).get('context', ''),
                                "question": input_data.get("question", '').strip(),
                                "parameters": {
                                    "temperature": input_data.get("temperature", 0.5)
                                }
                            },
                            "version": "0.0.3",
                            "error": response_data.get('message_data').get('message') if response_data.get('message_data') else ""
                        })

                except Exception as e:
                    response_data = None
                    response_msg = e
                    response_cde = ResponseCode.SERVER_FAILURE
                finally:
                    file_sys_handler.delete_file(
                        file_path=temp_path)

            if len(answers) > 0:
                try:
                    response_data = QueryResponseData(answers=answers)
                    response_cde = ResponseCode.SUCCESS
                    response_msg = ResponseMessage.SUCCESS
                except Exception as e:
                    response_data = None
                    response_msg = e
                    response_cde = ResponseCode.SERVER_FAILURE

        elapsed_time = round(time.time() - start_time, 3)

        response = QnAResponseData(response=response_data, responseCde=response_cde,
                                   responseMsg=str(response_msg), timestamp=date_time_stamp,
                                   responseTimeInSecs=(elapsed_time))
        return response

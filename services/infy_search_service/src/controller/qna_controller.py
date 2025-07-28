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
from schema.qna_req_res_data import (
    QnARequestData, QnAResponseData, QueryResponseData)
from schema.base_req_res_data import (ResponseCode, ResponseMessage)
from .b_controller import BController
from common.app_config_manager import AppConfigManager
from common.ainauto_logger_factory import AinautoLoggerFactory


class QnAController(BController):
    """Perform search on a database through using an index"""

    __CONTROLLER_PATH = "/inference"

    def __init__(self, context_root_path: str = ''):
        super().__init__(context_root_path=context_root_path,
                         controller_path=self.__CONTROLLER_PATH)
        self.get_router().add_api_route(
            "/search", self.QnA_document, methods=["POST"], summary="Perform search on a database",
            tags=["inference"],
            response_model=QnAResponseData)

    def QnA_document(self, QnA_request_data: QnARequestData,
                     request: fastapi.Request,
                     response: fastapi.Response,
                     api_endpoint: str = fastapi.Header(...),
                     api_key: str = fastapi.Header(...)
                     ):
        app_config = AppConfigManager().get_app_config()
        logger = AinautoLoggerFactory().get_logger()
        file_sys_handler = infy_fs_utils.manager.FileSystemManager().get_fs_handler()

        start_time = time.time()
        date = datetime.now(timezone.utc)
        date_time_stamp = date.strftime("%Y-%m-%d %I:%M:%S %p")

        input_data = QnA_request_data.dict()
        working_file_path_list = ['documents']
        config_file_path = app_config['STORAGE']["dpp_input_config_file_path"]

        index_id = input_data.get("retrieval", {}).get(
            "index_id", '').strip()
        question = input_data.get("question", '').strip()
        vector_enabled = input_data.get('retrieval', {}).get(
            'datasource', {}).get('vectorindex', {}).get('enabled', False)
        sparse_enabled = input_data.get('retrieval', {}).get(
            'datasource', {}).get('sparseindex', {}).get('enabled', False)
        hybrid_enabled = input_data.get('retrieval', {}).get(
            'hybrid_search', {}).get('rrf', {}).get('enabled', False)
        cust_metadata_enabled = input_data.get('retrieval', {}).get(
            'custom_metadata_filter', {}).get('enabled', False)
        generate_enabled = input_data.get('generation', {}).get(
                'enabled', False)
        if not index_id:
            response_data = None
            response_cde = ResponseCode.CLIENT_FAILURE
            response_msg = "ERROR: Please provide valid Index id."
        elif not question:
            response_data = None
            response_cde = ResponseCode.CLIENT_FAILURE
            response_msg = "ERROR: Please provide Question."
        elif not vector_enabled and not sparse_enabled and hybrid_enabled or not vector_enabled and sparse_enabled and hybrid_enabled or vector_enabled and not sparse_enabled and hybrid_enabled:
            response_data = None
            response_cde = ResponseCode.CLIENT_FAILURE
            response_msg = "ERROR: Please enable both vector and sparse index for hybrid search."
        elif cust_metadata_enabled and not(input_data.get('retrieval', {}).get('custom_metadata_filter', {}).get('model_name','') and input_data.get('retrieval', {}).get('custom_metadata_filter', {}).get('deployment_name','')):
            response_data = None
            response_cde = ResponseCode.CLIENT_FAILURE
            response_msg = "ERROR: Please provide both model_name and deployment_name in custom_metadata_filter if you have it enabled."
        elif generate_enabled and not(input_data.get('generation', {}).get('model_name','') and input_data.get('generation', {}).get('deployment_name','')):
            response_data = None
            response_cde = ResponseCode.CLIENT_FAILURE
            response_msg = "ERROR: Please provide both model_name and deployment_name in generation if you have it enabled."
        else:
            document_id_list = [os.path.basename(x)
                                for x in working_file_path_list]
            answers = []
            input_config_data = json.loads(file_sys_handler.read_file(
                config_file_path))
            mde_enabled = False

            # STEP 1: Set the pipeline to run only retriever or retriever and reader
            retriever_enabled = input_data.get('retrieval', {}).get(
                'enabled', True)
            generation_enabled = input_data.get('generation', {}).get(
                'enabled', True)
            if retriever_enabled and input_data.get('retrieval', {}).get(
            'custom_metadata_filter', {}).get('enabled', False):
                mde_enabled = True
            processor_list_config_data = input_config_data['processor_list']
            processor_list_config_data[0]['enabled'] = mde_enabled
            processor_list_config_data[1]['enabled'] = retriever_enabled
            processor_list_config_data[2]['enabled'] = generation_enabled

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

            # STEP 2.5: check which data source is enabled
            vector_storage_key = ''
            vector_storage = input_config_data[
                'processor_input_config']['QueryRetriever']['storage']['vectordb']
            for e_key, e_value in vector_storage.items():
                if e_value.get('enabled'):
                    vector_storage_key = e_key

            # STEP 3: Set Datasource details
            # a.vector_index
            if vector_storage_key == 'infy_db_service':
                vector_storage_config = input_config_data[
                    'processor_input_config']['QueryRetriever']['storage']['vectordb']['infy_db_service']
                vector_storage_config['enabled'] = input_data['retrieval']['datasource']['vectorindex']['enabled']
                vector_storage_config['configuration']['model_name'] = ''
                vector_storage_config['configuration']['index_id'] = index_id
                vector_storage_config['configuration']['collections'][0]['collection_name'] = ''
                vector_storage_config['configuration']['collections'][0]['collection_secret_key'] = ''
            elif vector_storage_key == 'elasticsearch':
                vector_storage_config = input_config_data[
                    'processor_input_config']['QueryRetriever']['storage']['vectordb']['elasticsearch']
                vector_storage_config['enabled'] = input_data['retrieval']['datasource']['vectorindex']['enabled']
                vector_storage_config['configuration']['index_id'] = index_id

            # b.sparse_index
            sparse_storage_config = input_config_data[
                'processor_input_config']['QueryRetriever']['storage']['sparseindex']['infy_db_service']
            sparse_storage_config['enabled'] = input_data['retrieval']['datasource']['sparseindex']['enabled']
            sparse_storage_config['configuration']['method_name'] = ''
            sparse_storage_config['configuration']['index_id'] = index_id
            sparse_storage_config['configuration']['collections'][0]['collection_name'] = ''
            sparse_storage_config['configuration']['collections'][0]['collection_secret_key'] = ''

            # STEP 4: Set Hybrid search details
            # a.rrf
            rrf_storage_config = input_config_data['processor_input_config'][
                'QueryRetriever']['hybrid_search']['rrf']
            rrf_storage_config['enabled'] = input_data['retrieval']['hybrid_search']['rrf']['enabled']

            # STEP 5: Set Inference details
            if generation_enabled:
                inference_config_data = input_config_data['processor_input_config']['Reader']
                inference_config_data['storage']['vectordb']['faiss']['enabled'] = vector_storage_config['enabled']
                inference_config_data['storage']['sparseindex']['bm25s']['enabled'] = sparse_storage_config['enabled']
                inference_config_data['hybrid_search']['rrf']['enabled'] = rrf_storage_config['enabled']

                for llm_obj in inference_config_data['llm']['models']:
                    if llm_obj['enabled'] == True:
                        llm_obj['configuration']['api_url'] = api_endpoint
                        llm_obj['configuration']['api_key'] = api_key
                        llm_obj['configuration'][
                            'model_name'] = input_data['generation']["model_name"]
                        llm_obj['configuration'][
                            'deployment_name'] = input_data['generation']["deployment_name"]
                        llm_obj['configuration'][
                            'max_tokens'] = input_data['generation']["max_tokens"]
                        llm_obj['configuration'][
                            'temperature'] = input_data['generation']["temperature"]
                        inference_config_data['inputs'][0]['top_k'] = input_data['generation']['top_k_used']
                        prompt_temp_used = inference_config_data['inputs'][0]['prompt_template']
                        if prompt_temp_used in inference_config_data['named_prompt_templates']:
                            inference_config_data['named_prompt_templates'][prompt_temp_used][
                                'response_validation']['total_attempts'] = input_data['generation']['total_attempts']
                            
            # STEP 6: Set Metadata details
            if mde_enabled:
                mde_query_config_data = input_config_data[
                    'processor_input_config']['MetadataExtractorCustom']['query']
                mde_vector_storage = mde_query_config_data['storage']['vectordb']
                for e_key, e_value in mde_vector_storage.items():
                    if e_value.get('enabled'):
                        mde_vector_storage_key = e_key
                if mde_vector_storage_key == 'infy_db_service':
                    mde_vector_storage_config = mde_vector_storage['infy_db_service']
                    mde_vector_storage_config['enabled'] = input_data['retrieval']['custom_metadata_filter']['enabled']
                    mde_vector_storage_config['configuration']['model_name'] = ''
                    mde_vector_storage_config['configuration']['index_id'] = index_id
                    mde_vector_storage_config['configuration']['collections'][0]['collection_name'] = ''
                    mde_vector_storage_config['configuration']['collections'][0]['collection_secret_key'] = ''
                elif mde_vector_storage_key == 'elasticsearch':
                    mde_vector_storage_config = mde_vector_storage['elasticsearch']
                    mde_vector_storage_config['enabled'] = input_data['retrieval']['custom_metadata_filter']['enabled']
                    mde_vector_storage_config['configuration']['index_id'] = index_id

                for llm_obj in mde_query_config_data['llm']['models']:
                    if llm_obj['enabled'] == True:
                        llm_obj['configuration']['api_url'] = api_endpoint
                        llm_obj['configuration']['api_key'] = api_key
                        llm_obj['configuration'][
                            'model_name'] = input_data['retrieval']['custom_metadata_filter']["model_name"]
                        llm_obj['configuration'][
                            'deployment_name'] = input_data['retrieval']['custom_metadata_filter']["deployment_name"]
                                                        
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
                document_data_json = {
                    'document_data': response_data.document_data.dict(),
                    'context_data': response_data.context_data
                }

                # Write the input config data to a temp file
                unique_filename = f"{uuid.uuid4()}_config.json"
                temp_path = f"/data/temp/{unique_filename}"
                file_sys_handler.write_file(
                    temp_path, json.dumps(input_config_data, indent=4))

                try:
                    # ---------------------Run the inference pipeline  LOGIC STARTS------------------------------ #

                    dpp_orchestrator = infy_dpp_sdk.orchestrator.OrchestratorNativeBasic(
                        input_config_file_path=temp_path)
                    response_data_list = dpp_orchestrator.run_batch([infy_dpp_sdk.data.DocumentData(
                        **document_data_json.get('document_data'))], [document_data_json.get('context_data')])

                    # ---------------------Run the inference pipeline  LOGIC ENDS------------------------------ #

                    for processor_response_data in response_data_list:
                        response_data = processor_response_data.dict()
                        if response_data.get('message_data') is None:
                            model_output = response_data.get('context_data', {}).get(
                                'reader', {}).get('output', [{}])[0].get('model_output', {})
                            if isinstance(model_output, dict):
                                answer = response_data.get('context_data', {}).get('reader', {}).get(
                                    'output', [{}])[0].get('model_output', {}).get('answer', '')
                                sources = model_output.get('sources', [])
                                if len(sources) > 1:
                                    chunk_id = ",".join(
                                        [source.get('chunk_id', '') for source in sources])
                                    page_num = ",".join(
                                        [str(source.get('page_no', 0)) for source in sources])
                                    segment_num = ",".join(
                                        [str(source.get('sequence_no', 0)) for source in sources])
                                    doc_name = ",".join(
                                        [str(source.get('doc_name', '')) for source in sources])
                                else:
                                    chunk_id = sources[0].get(
                                        'chunk_id', '') if sources else ""
                                    page_num = sources[0].get(
                                        'page_no', 0) if sources else 0
                                    segment_num = sources[0].get(
                                        'sequence_no', 0) if sources else 0
                                    doc_name = sources[0].get(
                                        'doc_name', '') if sources else ""
                            elif isinstance(model_output, str):
                                try:
                                    model_output = json.loads(model_output)
                                    answer = model_output.get('answer', '')
                                    sources = model_output.get('sources', [])
                                    if len(sources) > 1:
                                        chunk_id = ",".join(
                                            [source.get('chunk_id', '') for source in sources])
                                        page_num = ",".join(
                                            [str(source.get('page_no', 0)) for source in sources])
                                        segment_num = ",".join(
                                            [str(source.get('sequence_no', 0)) for source in sources])
                                        doc_name = ",".join(
                                            [source.get('doc_name', '') for source in sources])
                                    else:
                                        chunk_id = sources[0].get(
                                            'chunk_id', '') if sources else ""
                                        page_num = sources[0].get(
                                            'page_no', 0) if sources else 0
                                        segment_num = sources[0].get(
                                            'sequence_no', 0) if sources else 0
                                        doc_name = sources[0].get(
                                            'doc_name', '') if sources else ""
                                except json.JSONDecodeError:
                                    answer = model_output
                                    chunk_id = ""
                                    page_num = 0
                                    segment_num = 0
                                    doc_name = ""
                            else:
                                answer = model_output
                                chunk_id = ""
                                page_num = 0
                                segment_num = 0
                                doc_name = ""

                            answers.append({
                                "db_name": document_id,
                                "doc_name": doc_name if doc_name else '',
                                "answer": answer,
                                "chunk_id": chunk_id,
                                "page_num": page_num,
                                "segment_num": segment_num,
                                "source_metadata": response_data.get('context_data', {}).get('reader', {}).get('output', [{}])[0].get('source_metadata', []),
                                # "embedding_model_name": response_data.get('context_data', {}).get('query_retriever', {}).get('queries', [{}])[0].get('embedding_model', ''),
                                # "distance_metric": response_data.get('context_data', {}).get('query_retriever', {}).get('queries', [{}])[0].get('distance_metric', ''),
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
                                    "question": response_data.get('context_data', {}).get('reader', {}).get('output', [{}])[0].get('model_input', {}).get('template_var_to_value_dict', {}).get('question', ''),
                                    "parameters": {
                                        "temperature": input_data.get("temperature", 0.5)
                                    }
                                },
                                "version": "0.0.3",
                                "error": response_data.get('message_data').get('message') if response_data.get('message_data') else ""
                            })
                        else:
                            answers = {}
                            error_msg = response_data.get('message_data').get('messages')[0].get('message_text')
                            
                except Exception as e:
                    response_data = None
                    response_msg = e
                    response_cde = ResponseCode.SERVER_FAILURE
                    error_msg = response_msg
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
                    response_msg =  e
                    response_cde = ResponseCode.SERVER_FAILURE
                    error_msg = response_msg
            else:
                response_data = None
                response_cde = ResponseCode.SERVER_FAILURE
                if 'litellm' in error_msg.lower() or 'metadata' in error_msg.lower():
                    response_msg = error_msg.replace("UNHANDLED EXCEPTION =>", "ERROR:").strip()
                else:
                    response_msg = "ERROR: An unexpected error occurred. Please try again."

        elapsed_time = round(time.time() - start_time, 3)

        response = QnAResponseData(response=response_data, responseCde=response_cde,
                                   responseMsg=str(response_msg), timestamp=date_time_stamp,
                                   responseTimeInSecs=(elapsed_time))
        return response

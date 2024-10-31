# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import os
import re
import json
import time
import uuid
from typing import List
from datetime import datetime, timezone
import fastapi
import infy_fs_utils
import infy_dpp_sdk
import infy_gen_ai_sdk
from schema.sparse_req_res_data import SaveRecordsRequestData, SaveRecordsResponseData, GetRecordsRequestData, GetMatchesRequestData, DeleteRecordsRequestData
from schema.base_req_res_data import (ResponseCode, ResponseMessage)
from .b_controller import BController
from common.app_config_manager import AppConfigManager
from common.ainauto_logger_factory import AinautoLoggerFactory


class SparsedbController(BController):
    """Sparse DB Controller Class"""

    __CONTROLLER_PATH = "/sparsedb"

    def __init__(self, context_root_path: str = ''):
        super().__init__(context_root_path=context_root_path,
                         controller_path=self.__CONTROLLER_PATH)
        self.get_router().add_api_route(
            "/saverecords", self.saveRecords, methods=["POST"], summary="Save records to a sparse database",
            tags=["Sparse Database"],
            response_model=SaveRecordsResponseData)
        self.get_router().add_api_route(
            "/getrecords", self.getRecords, methods=["POST"], summary="Get records from a sparse database",
            tags=["Sparse Database"],
            response_model=SaveRecordsResponseData)
        self.get_router().add_api_route(
            "/getmatches", self.getMatches, methods=["POST"], summary="Get matches from a sparse database",
            tags=["Sparse Database"],
            response_model=SaveRecordsResponseData)
        self.get_router().add_api_route(
            "/deleterecords", self.deleteRecords, methods=["POST"], summary="Delete records from a sparse database",
            tags=["Sparse Database"],
            response_model=SaveRecordsResponseData)

    def saveRecords(self, save_records_data: SaveRecordsRequestData,
                    request: fastapi.Request
                    ):
        app_config = AppConfigManager().get_app_config()
        logger = AinautoLoggerFactory().get_logger()

        file_sys_handler = infy_fs_utils.manager.FileSystemManager(
        ).get_fs_handler(infy_gen_ai_sdk.common.Constants.FSH_GEN_AI_SDK)

        container_root_path = app_config['CONTAINER']["container_root_path"]
        client_config_data = infy_gen_ai_sdk.ClientConfigData(
            **{
                "container_data": {
                    "container_root_path": f"{container_root_path}",
                }
            })
        infy_gen_ai_sdk.ClientConfigManager().load(client_config_data)

        config_file_path = app_config['STORAGE']["model_details_path"]
        model_details_data = json.loads(
            file_sys_handler.read_file(config_file_path))

        start_time = time.time()
        date = datetime.now(timezone.utc)
        date_time_stamp = date.strftime("%Y-%m-%d %I:%M:%S %p")

        input_data = save_records_data.dict()

        method_name = input_data.get("method_name", '')
        index_id = input_data.get("index_id", '')
        db_index_name = input_data.get(
            "collection_name", '')
        db_index_secret_key = input_data.get(
            "collection_secret_key", '')
        record_data_dict = input_data.get("record_data_dict", {})
        if not method_name:
            response_data = SaveRecordsResponseData(
                response={},
                responseCde=ResponseCode.FAILURE,
                responseMsg="ERROR: Required configuration data is missing.",
                timestamp=datetime.now(timezone.utc),
            )
        elif not db_index_name:
            response_data = SaveRecordsResponseData(
                response={},
                responseCde=ResponseCode.FAILURE,
                responseMsg="ERROR: Required configuration data is missing.",
                timestamp=datetime.now(timezone.utc),
            )
        elif not record_data_dict:
            response_data = SaveRecordsResponseData(
                response={},
                responseCde=ResponseCode.FAILURE,
                responseMsg="ERROR: Required configuration data is missing.",
                timestamp=datetime.now(timezone.utc),
            )
        else:

            try:
                # ---------------------LOGIC STARTS------------------------------ #
                if method_name == 'bm25s':
                    method_config = model_details_data.get(
                        'storage').get('sparseindex').get('bm25s').get('configuration')
                    os.environ["NLTK_DATA_DIR"] = method_config.get(
                        'nltk_data_dir')
                else:
                    raise Exception(
                        f"Method '{method_name}' is not supported.")

                sparse_index_root_path = method_config.get(
                    'sparse_index_root_path')
                sparse_db_name = method_config.get('db_name')
                if index_id:
                    server_faiss_write_path = f'{sparse_index_root_path}/{method_name}/{sparse_db_name}/{index_id}'
                else:
                    server_faiss_write_path = f'{sparse_index_root_path}/{method_name}/{sparse_db_name}'

                sparse_db_provider_config_data = infy_gen_ai_sdk.sparsedb.provider.bm25s.SparseDbProviderConfigData(
                    **{
                        'db_folder_path': server_faiss_write_path,
                        'db_index_name': db_index_name,
                        "db_index_secret_key": db_index_secret_key if db_index_secret_key else None
                    })
                sparse_db_provider = infy_gen_ai_sdk.sparsedb.provider.bm25s.Bm25sSparseDbProvider(
                    sparse_db_provider_config_data)

                unique_filename = f"{uuid.uuid4()}.txt"
                temp_path = f"/data/temp/{unique_filename}"
                file_sys_handler.write_file(
                    file_path=temp_path, data=record_data_dict.get('content'))
                # Step 3 - Add record(s) to sparse db
                db_record_data = infy_gen_ai_sdk.sparsedb.provider.bm25s.SparseDbRecordConfigData(
                    **{
                        'content_file_path': temp_path,
                        'metadata': record_data_dict.get('metadata', {})
                    })
                sparse_db_provider.save_record(db_record_data)
                file_sys_handler.delete_file(
                    file_path=temp_path)

                response_data = {
                    'encoded_path_list': server_faiss_write_path,
                    'method_name': method_name
                }
                response_cde = ResponseCode.SUCCESS
                response_msg = ResponseMessage.SUCCESS

                # ---------------------LOGIC ENDS------------------------------ #

            except Exception as e:
                response_data = {}
                response_cde = ResponseCode.FAILURE
                response_msg = e

        elapsed_time = round(time.time() - start_time, 3)

        response = SaveRecordsResponseData(response=response_data, responseCde=response_cde,
                                           responseMsg=str(response_msg), timestamp=date_time_stamp,
                                           responseTimeInSecs=(elapsed_time))
        return response

    def getRecords(self, get_records_data: GetRecordsRequestData,
                   request: fastapi.Request
                   ):
        app_config = AppConfigManager().get_app_config()
        logger = AinautoLoggerFactory().get_logger()

        file_sys_handler = infy_fs_utils.manager.FileSystemManager(
        ).get_fs_handler(infy_gen_ai_sdk.common.Constants.FSH_GEN_AI_SDK)

        container_root_path = app_config['CONTAINER']["container_root_path"]
        client_config_data = infy_gen_ai_sdk.ClientConfigData(
            **{
                "container_data": {
                    "container_root_path": f"{container_root_path}",
                }
            })
        infy_gen_ai_sdk.ClientConfigManager().load(client_config_data)

        config_file_path = app_config['STORAGE']["model_details_path"]
        model_details_data = json.loads(
            file_sys_handler.read_file(config_file_path))

        start_time = time.time()
        date = datetime.now(timezone.utc)
        date_time_stamp = date.strftime("%Y-%m-%d %I:%M:%S %p")

        input_data = get_records_data.dict()

        method_name = input_data.get("method_name", '')
        index_id = input_data.get("index_id", '')
        db_index_name = input_data.get(
            "collection_name", '')
        db_index_secret_key = input_data.get(
            "collection_secret_key", '')
        if not index_id and (not method_name or not db_index_name):
            response_data = SaveRecordsResponseData(
                response={},
                responseCde=ResponseCode.FAILURE,
                responseMsg="ERROR: Either 'index_id' must be provided or both 'method_name' and 'collection_name' must be provided.",
                timestamp=datetime.now(timezone.utc),
            )
        else:
            try:

                # ---------------------LOGIC STARTS------------------------------ #
                if not method_name:
                    if index_id:
                        sparse_root_path = model_details_data.get(
                            'common').get('base_sparse_encoded_root_path')
                        base_file_list = file_sys_handler.list_files(
                            sparse_root_path)
                        index_file_list = [
                            item for item in base_file_list if index_id in item]
                        if len(index_file_list) >= 6:
                            pattern = re.compile(
                                rf"{index_id}/[^/]+\.metadata\.json$")
                            secret_key_path = ''
                            for item in index_file_list:
                                if pattern.search(item):
                                    secret_key_path = item
                                    db_index_secret_key = (json.loads(
                                        file_sys_handler.read_file(secret_key_path))).get('secret_key')
                                    break
                            if secret_key_path:
                                index_file_list = [
                                    item for item in index_file_list if item != secret_key_path]
                            rel_path = (
                                f'/{index_file_list[0]}').split(sparse_root_path, 1)[1]
                            path_parts = rel_path.strip(
                                '/').split('/')
                            method_name = path_parts[0]
                            db_index_name = path_parts[3]
                        else:
                            raise Exception(
                                f"Index '{index_id}' not found.")

                if method_name == 'bm25s':
                    method_config = model_details_data.get(
                        'storage').get('sparseindex').get('bm25s').get('configuration')
                    os.environ["NLTK_DATA_DIR"] = method_config.get(
                        'nltk_data_dir')
                else:
                    raise Exception(
                        f"Method '{method_name}' is not supported.")

                sparse_index_root_path = method_config.get(
                    'sparse_index_root_path')
                sparse_db_name = method_config.get('db_name')
                if index_id:
                    server_faiss_write_path = f'{sparse_index_root_path}/{method_name}/{sparse_db_name}/{index_id}'
                else:
                    server_faiss_write_path = f'{sparse_index_root_path}/{method_name}/{sparse_db_name}'

                sparse_db_provider_config_data = infy_gen_ai_sdk.sparsedb.provider.bm25s.SparseDbProviderConfigData(
                    **{
                        'db_folder_path': server_faiss_write_path,
                        'db_index_name': db_index_name,
                        "db_index_secret_key": db_index_secret_key if db_index_secret_key else None
                    })
                sparse_db_provider = infy_gen_ai_sdk.sparsedb.provider.bm25s.Bm25sSparseDbProvider(
                    sparse_db_provider_config_data)

                records: List[infy_gen_ai_sdk.sparsedb.provider.bm25s.SparseDbRecordData] = sparse_db_provider.get_records()

                response_data = {
                    'records': records,
                }
                response_cde = ResponseCode.SUCCESS
                response_msg = ResponseMessage.SUCCESS

                # ---------------------LOGIC ENDS------------------------------ #

            except Exception as e:
                response_data = {}
                response_cde = ResponseCode.FAILURE
                response_msg = e

        elapsed_time = round(time.time() - start_time, 3)

        response = SaveRecordsResponseData(response=response_data, responseCde=response_cde,
                                           responseMsg=str(response_msg), timestamp=date_time_stamp,
                                           responseTimeInSecs=(elapsed_time))
        return response

    def getMatches(self, get_matches_data: GetMatchesRequestData,
                   request: fastapi.Request
                   ):
        app_config = AppConfigManager().get_app_config()
        logger = AinautoLoggerFactory().get_logger()

        file_sys_handler = infy_fs_utils.manager.FileSystemManager(
        ).get_fs_handler(infy_gen_ai_sdk.common.Constants.FSH_GEN_AI_SDK)

        container_root_path = app_config['CONTAINER']["container_root_path"]
        client_config_data = infy_gen_ai_sdk.ClientConfigData(
            **{
                "container_data": {
                    "container_root_path": f"{container_root_path}",
                }
            })
        infy_gen_ai_sdk.ClientConfigManager().load(client_config_data)

        config_file_path = app_config['STORAGE']["model_details_path"]
        model_details_data = json.loads(
            file_sys_handler.read_file(config_file_path))

        start_time = time.time()
        date = datetime.now(timezone.utc)
        date_time_stamp = date.strftime("%Y-%m-%d %I:%M:%S %p")

        input_data = get_matches_data.dict()

        method_name = input_data.get("method_name", '')
        index_id = input_data.get("index_id", '')
        db_index_name = input_data.get(
            "collection_name", '')
        db_index_secret_key = input_data.get(
            "collection_secret_key", '')
        query_dict = input_data.get("query_dict", {})
        if not index_id and (not method_name or not db_index_name):
            response_data = SaveRecordsResponseData(
                response={},
                responseCde=ResponseCode.FAILURE,
                responseMsg="ERROR: Either 'index_id' must be provided or both 'method_name' and 'collection_name' must be provided.",
                timestamp=datetime.now(timezone.utc),
            )
        elif not query_dict:
            response_data = SaveRecordsResponseData(
                response={},
                responseCde=ResponseCode.FAILURE,
                responseMsg="ERROR: query_dict is required.",
                timestamp=datetime.now(timezone.utc),
            )
        else:

            try:
                # ---------------------LOGIC STARTS------------------------------ #
                if not method_name:
                    if index_id:
                        sparse_root_path = model_details_data.get(
                            'common').get('base_sparse_encoded_root_path')
                        base_file_list = file_sys_handler.list_files(
                            sparse_root_path)
                        index_file_list = [
                            item for item in base_file_list if index_id in item]
                        if len(index_file_list) >= 6:
                            pattern = re.compile(
                                rf"{index_id}/[^/]+\.metadata\.json$")
                            secret_key_path = ''
                            for item in index_file_list:
                                if pattern.search(item):
                                    secret_key_path = item
                                    db_index_secret_key = (json.loads(
                                        file_sys_handler.read_file(secret_key_path))).get('secret_key')
                                    break
                            if secret_key_path:
                                index_file_list = [
                                    item for item in index_file_list if item != secret_key_path]
                            rel_path = (
                                f'/{index_file_list[0]}').split(sparse_root_path, 1)[1]
                            path_parts = rel_path.strip(
                                '/').split('/')
                            method_name = path_parts[0]
                            db_index_name = path_parts[3]
                        else:
                            raise Exception(
                                f"Index '{index_id}' not found.")

                if method_name == 'bm25s':
                    method_config = model_details_data.get(
                        'storage').get('sparseindex').get('bm25s').get('configuration')
                    os.environ["NLTK_DATA_DIR"] = method_config.get(
                        'nltk_data_dir')
                else:
                    raise Exception(
                        f"Method '{method_name}' is not supported.")

                sparse_index_root_path = method_config.get(
                    'sparse_index_root_path')
                sparse_db_name = method_config.get('db_name')
                if index_id:
                    server_faiss_write_path = f'{sparse_index_root_path}/{method_name}/{sparse_db_name}/{index_id}'
                else:
                    server_faiss_write_path = f'{sparse_index_root_path}/{method_name}/{sparse_db_name}'

                sparse_db_provider_config_data = infy_gen_ai_sdk.sparsedb.provider.bm25s.SparseDbProviderConfigData(
                    **{
                        'db_folder_path': server_faiss_write_path,
                        'db_index_name': db_index_name,
                        "db_index_secret_key": db_index_secret_key if db_index_secret_key else None
                    })
                sparse_db_provider = infy_gen_ai_sdk.sparsedb.provider.bm25s.Bm25sSparseDbProvider(
                    sparse_db_provider_config_data)

                query_params_data = infy_gen_ai_sdk.sparsedb.provider.bm25s.SparseDbQueryParamsData(
                    **{
                        'query': query_dict.get('query'),
                        'top_k': query_dict.get('top_k'),
                        'pre_filter_fetch_k': query_dict.get('pre_filter_fetch_k'),
                        'filter_metadata': query_dict.get('filter_metadata')
                    })
                records: List[infy_gen_ai_sdk.sparsedb.provider.bm25s.SparseDbMatchesRecordData] = sparse_db_provider.get_matches(
                    query_params_data)

                total_records = []
                for record in records:
                    if query_dict.get('min_distance') < record.score:
                        total_records.append({"file_path": record.db_folder_path,
                                              "score": record.score,
                                              "content": record.content,
                                              "meta_data": record.metadata
                                              })

                response_data = {
                    'top_k': query_dict.get('top_k'),
                    'records': total_records
                }
                response_cde = ResponseCode.SUCCESS
                response_msg = ResponseMessage.SUCCESS

                # ---------------------LOGIC ENDS------------------------------ #

            except Exception as e:
                response_data = {}
                response_cde = ResponseCode.FAILURE
                response_msg = e

        elapsed_time = round(time.time() - start_time, 3)

        response = SaveRecordsResponseData(response=response_data, responseCde=response_cde,
                                           responseMsg=str(response_msg), timestamp=date_time_stamp,
                                           responseTimeInSecs=(elapsed_time))
        return response

    def deleteRecords(self, delete_records_data: DeleteRecordsRequestData,
                      request: fastapi.Request
                      ):
        app_config = AppConfigManager().get_app_config()
        logger = AinautoLoggerFactory().get_logger()

        file_sys_handler = infy_fs_utils.manager.FileSystemManager(
        ).get_fs_handler(infy_gen_ai_sdk.common.Constants.FSH_GEN_AI_SDK)

        container_root_path = app_config['CONTAINER']["container_root_path"]
        client_config_data = infy_gen_ai_sdk.ClientConfigData(
            **{
                "container_data": {
                    "container_root_path": f"{container_root_path}",
                }
            })
        infy_gen_ai_sdk.ClientConfigManager().load(client_config_data)

        config_file_path = app_config['STORAGE']["model_details_path"]
        model_details_data = json.loads(
            file_sys_handler.read_file(config_file_path))

        start_time = time.time()
        date = datetime.now(timezone.utc)
        date_time_stamp = date.strftime("%Y-%m-%d %I:%M:%S %p")

        input_data = delete_records_data.dict()

        method_name = input_data.get("method_name", '')
        index_id = input_data.get("index_id", '')
        db_index_name = input_data.get(
            "collection_name", '')
        db_index_secret_key = input_data.get(
            "collection_secret_key", '')
        if not index_id and (not method_name or not db_index_name):
            response_data = SaveRecordsResponseData(
                response={},
                responseCde=ResponseCode.FAILURE,
                responseMsg="ERROR: Either 'index_id' must be provided or both 'method_name' and 'collection_name' must be provided.",
                timestamp=datetime.now(timezone.utc),
            )
        else:

            try:
                # ---------------------LOGIC STARTS------------------------------ #
                if not method_name:
                    if index_id:
                        sparse_root_path = model_details_data.get(
                            'common').get('base_sparse_encoded_root_path')
                        base_file_list = file_sys_handler.list_files(
                            sparse_root_path)
                        index_file_list = [
                            item for item in base_file_list if index_id in item]
                        if len(index_file_list) >= 6:
                            pattern = re.compile(
                                rf"{index_id}/[^/]+\.metadata\.json$")
                            secret_key_path = ''
                            for item in index_file_list:
                                if pattern.search(item):
                                    secret_key_path = item
                                    db_index_secret_key = (json.loads(
                                        file_sys_handler.read_file(secret_key_path))).get('secret_key')
                                    break
                            if secret_key_path:
                                index_file_list = [
                                    item for item in index_file_list if item != secret_key_path]
                            rel_path = (
                                f'/{index_file_list[0]}').split(sparse_root_path, 1)[1]
                            path_parts = rel_path.strip(
                                '/').split('/')
                            method_name = path_parts[0]
                            db_index_name = path_parts[3]
                        else:
                            raise Exception(
                                f"Index '{index_id}' not found.")

                if method_name == 'bm25s':
                    method_config = model_details_data.get(
                        'storage').get('sparseindex').get('bm25s').get('configuration')
                    os.environ["NLTK_DATA_DIR"] = method_config.get(
                        'nltk_data_dir')
                else:
                    raise Exception(
                        f"Method '{method_name}' is not supported.")

                sparse_index_root_path = method_config.get(
                    'sparse_index_root_path')
                sparse_db_name = method_config.get('db_name')
                if index_id:
                    server_faiss_write_path = f'{sparse_index_root_path}/{method_name}/{sparse_db_name}/{index_id}'
                else:
                    server_faiss_write_path = f'{sparse_index_root_path}/{method_name}/{sparse_db_name}'

                sparse_db_provider_config_data = infy_gen_ai_sdk.sparsedb.provider.bm25s.SparseDbProviderConfigData(
                    **{
                        'db_folder_path': server_faiss_write_path,
                        'db_index_name': db_index_name,
                        "db_index_secret_key": db_index_secret_key if db_index_secret_key else None
                    })
                sparse_db_provider = infy_gen_ai_sdk.sparsedb.provider.bm25s.Bm25sSparseDbProvider(
                    sparse_db_provider_config_data)

                sparse_db_provider.delete_records()

                response_data = {
                    "response": f"All records under collection:'{db_index_name}' deleted successfully"
                }
                response_cde = ResponseCode.SUCCESS
                response_msg = ResponseMessage.SUCCESS

                # ---------------------LOGIC ENDS------------------------------ #

            except Exception as e:
                response_data = {}
                response_cde = ResponseCode.FAILURE
                response_msg = e

        elapsed_time = round(time.time() - start_time, 3)

        response = SaveRecordsResponseData(response=response_data, responseCde=response_cde,
                                           responseMsg=str(response_msg), timestamp=date_time_stamp,
                                           responseTimeInSecs=(elapsed_time))
        return response

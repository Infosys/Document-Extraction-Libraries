# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

from typing import List, Optional
from pydantic import BaseModel, root_validator
from .base_req_res_data import BaseRequestData, BaseResponseData
from pydantic import Field


class RecordData(BaseModel):
    """Common index detail"""
    content: str = ''
    metadata: dict


class SaveRecordsRequestData(BaseRequestData):
    """SaveRecords request data"""
    method_name: str = ''
    index_id: str = ''
    collection_name: str = ''
    collection_secret_key: str = ''
    record_data_dict: RecordData


class SaveRecordsResponseData(BaseResponseData):
    """SaveRecords response data"""
    response: object
    responseCde: int
    responseMsg: str
    timestamp: str
    responseTimeInSecs: float


class GetRecordsRequestData(BaseRequestData):
    """GetRecords data"""
    method_name: str = ''
    index_id: str = ''
    collection_name: str = ''
    collection_secret_key: str = ''


class QueryObject(BaseRequestData):
    """QueryObject data"""
    query: str = ''
    top_k: int = 1
    pre_filter_fetch_k: int = 10
    filter_metadata: object = {}
    min_distance: int = 0
    max_distance: int = 0


class GetMatchesRequestData(BaseRequestData):
    """GetRecords data"""
    method_name: str = ''
    index_id: str = ''
    collection_name: str = ''
    collection_secret_key: str = ''
    query_dict: QueryObject


class DeleteRecordsRequestData(BaseRequestData):
    """GetRecords data"""
    method_name: str = ''
    index_id: str = ''
    collection_name: str = ''
    collection_secret_key: str = ''

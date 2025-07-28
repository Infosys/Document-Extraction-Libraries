# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

from typing import List, Optional
from pydantic import BaseModel
from .base_req_res_data import BaseRequestData, BaseResponseData
from datetime import datetime


class LlmDetail(BaseModel):
    """Common index detail"""
    llm_name: str = ""
    llm_url: str = ""
    llm_password: Optional[str] = ""


class InferenceRequestData(BaseModel):
    """Inference request data"""
    # llm: LlmDetail
    enabled: bool = True
    temperature: float = 0.5
    # from_cache: bool = False
    top_k_used: int = 1
    total_attempts: int = 1


class CollectionDetail(BaseModel):
    """Common index detail"""
    collection_name: str = ""
    collection_secret_key: str = ""


class VectorIndexDetail(BaseModel):
    """Common index detail"""
    enabled: bool = True
    model_name: str = ""
    collections: List[CollectionDetail]


class SparseIndexDetail(BaseModel):
    """Common index detail"""
    enabled: bool = True
    method_name: str = ""
    collections: List[CollectionDetail]


class DatasourceDetail(BaseModel):
    """Datasource detail"""
    vectorindex: VectorIndexDetail
    sparseindex: SparseIndexDetail


class RRFdetail(BaseModel):
    """Datasource detail"""
    enabled: bool = True


class HybridDetail(BaseModel):
    """Datasource detail"""
    rrf: RRFdetail


class RetrievalRequestData(BaseModel):
    """Retrieval request data"""
    enabled: bool = True
    index_id: str = ""
    pre_filter_fetch_k: int = 10
    filter_metadata: dict = {}
    top_k: int = 1
    max_distance: int = 2
    datasource: DatasourceDetail
    hybrid_search: HybridDetail


class QnARequestData(BaseRequestData):
    """QnA request data"""
    question: str = ""
    retrieval: RetrievalRequestData
    generation: InferenceRequestData


###
class SourceMetadataDetail(BaseModel):
    chunk_id: str
    bbox_format: str
    bbox: Optional[List]
    doc_name: str


class Parameter(BaseModel):
    temperature: float


class LLMPromptDetail(BaseModel):
    prompt_template: str
    context: str
    question: str
    parameters: Parameter


class LLMResponseDetail(BaseModel):
    response: str
    from_cache: bool


class DocBasedQueryResponseData(BaseModel):
    db_name: str
    doc_name: str
    answer: str
    chunk_id: str
    page_num: int
    segment_num: int
    source_metadata: List[SourceMetadataDetail] = []
    embedding_model_name: str
    # distance_metric: str
    top_k: int
    top_k_list: List
    top_k_aggregated: int
    llm_model_name: str
    llm_total_attempts: int
    llm_response: LLMResponseDetail
    llm_prompt: LLMPromptDetail
    version: str
    error: str


class QueryResponseData(BaseModel):
    answers: List[DocBasedQueryResponseData]


class QnAResponseData(BaseResponseData):
    """QnA response data"""
    response: QueryResponseData = None
    responseCde: int
    responseMsg: str
    timestamp: str
    responseTimeInSecs: float

# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

from typing import List, Optional, Union
from pydantic import BaseModel
from .base_req_res_data import BaseRequestData, BaseResponseData
from datetime import datetime


class LlmDetail(BaseModel):
    """Common index detail"""
    llm_name: str = ""
    llm_password: Optional[str] = ""


class InferenceRequestData(BaseModel):
    """Inference request data"""
    # llm: LlmDetail
    enabled: bool = True
    model_name: str = ""
    deployment_name: str = ""
    max_tokens: int = 1000
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


class SparseIndexDetail(BaseModel):
    """Common index detail"""
    enabled: bool = True


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
    
class CustomMetadataFilter(BaseModel):
    """Custom Metadata Filter detail"""
    enabled: bool = True
    model_name: str = ""
    deployment_name: str = ""

class RetrievalRequestData(BaseModel):
    """Retrieval request data"""
    enabled: bool = True
    index_id: str = ""
    pre_filter_fetch_k: int = 10
    filter_metadata: dict = {}
    top_k: int = 1
    datasource: DatasourceDetail
    hybrid_search: HybridDetail
    custom_metadata_filter: CustomMetadataFilter


class QnARequestData(BaseRequestData):
    """QnA request data"""
    question: str = ""
    retrieval: RetrievalRequestData
    generation: InferenceRequestData


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
    page_num:  Union[int, str]
    segment_num:  Union[int, str]
    source_metadata: List[SourceMetadataDetail] = []
    # embedding_model_name: str
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
    response: Optional[QueryResponseData] = None
    responseCde: int
    responseMsg: str
    timestamp: str
    responseTimeInSecs: float

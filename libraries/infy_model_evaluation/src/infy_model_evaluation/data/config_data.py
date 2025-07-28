"""Base class for Evaluator config data"""
# ===============================================================================================================#
# Copyright 2022 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

from typing import Optional
try:
    from pydantic.v1 import BaseModel
except ImportError:
    from pydantic import BaseModel

from langchain_openai import AzureOpenAI
from langchain_openai.embeddings import AzureOpenAIEmbeddings
from langchain_openai.chat_models import AzureChatOpenAI


class EvaluatorEmbedding(BaseModel):
    """Base class for Evaluator embedding provider config data"""
    api_type: str = None
    api_version: str = None
    api_url: str = None
    api_key: str = None
    model_name: str = None
    deployment_name: str = None


class EvaluatorLlm(BaseModel):
    """Base class for Evaluator LLM provider config data"""
    api_type: str = None
    api_version: str = None
    api_url: str = None
    api_key: str = None
    model_name: str = None
    deployment_name: str = None
    top_p: float = None
    frequency_penalty: float = None
    presence_penalty: float = None
    stop: str = None
    is_chat_model: bool = None


class EvaluatorMetrics(BaseModel):
    """Base class for Evaluator metrics config data"""
    metrics: list = None


class PromptTemplate(BaseModel):
    """Base class for Prompt Template config data"""
    file_path: str = None


class TargetLlm(BaseModel):
    """Base class for Target LLM provider config data"""
    api_type: str = None
    api_version: str = None
    api_url: str = None
    api_key: str = None
    model_name: str = None
    deployment_name: str = None
    max_tokens: int = None
    temperature: float = None  # 0.7
    prompt_template: PromptTemplate = None
    remove_prompt_from_response: bool = None
    requires_num_return_sequences: bool = None
    num_return_sequences: int = None
    do_sample: bool = None
    is_chat_model: bool = None
    top_p: float = None
    frequency_penalty: float = None
    presence_penalty: float = None
    stop: str = None


class Datasource(BaseModel):
    """Base class for Datasource config data"""
    file_path: str = None
    files: list = None


class Result(BaseModel):
    """Base class for Result config data"""
    file_path: str = None
    meta_data:  Optional[dict] = None


class OpenAIFormatCustomChatLlm(BaseModel):
    """A openAI format custom LLM class"""
    api_url: str = None
    api_key: str = None
    model_name: str = None
    deployment_name: str = None
    max_tokens: int = None
    temperature: int = None  # 0.7
    top_p: float = None
    frequency_penalty: float = None
    presence_penalty: float = None
    stop: str = None
    timeout: int = None


class OpenAIFormatCustomEmbedding(BaseModel):
    """A openAI format custom LLM class"""
    api_url: str = None
    api_key: str = None
    model_name: str = None
    api_version: str = None


class EvaluatorConfigData(BaseModel):
    """Base class for Evaluator config data"""
    embedding: AzureOpenAIEmbeddings = None
    custom_embedding: OpenAIFormatCustomEmbedding = None
    llm: AzureOpenAI = None
    llm_chat: AzureChatOpenAI = None
    custom_llm_chat: OpenAIFormatCustomChatLlm = None
    metrics: list = None
    target_llm: TargetLlm = None
    evaluation_only: bool = True
    context_filter: int = None
    datasource: Datasource = None
    result: Result = None
    is_evaluator_llm_chat_model: bool = None
    evaluator_embedding_tiktoken_cache_dir: str = None


class BaseLlmProviderConfigData(BaseModel):
    """Base class for LLM provider config data"""
    api_url: str = None
    model_name: str = None

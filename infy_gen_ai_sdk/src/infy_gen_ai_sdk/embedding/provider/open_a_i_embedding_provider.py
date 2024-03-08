# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                   #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

"""Module for OpenAI embedding provider class"""

from langchain.embeddings.openai import OpenAIEmbeddings
from infy_gen_ai_sdk.data.config_data import BaseEmbeddingProviderConfigData
from infy_gen_ai_sdk.embedding.interface.i_embedding_provider import IEmbeddingProvider


class OpenAIEmbeddingProviderConfigData(BaseEmbeddingProviderConfigData):
    """Domain class"""
    api_key: str
    api_version: str
    api_type: str
    chunk_size: int


class OpenAIEmbeddingProvider(IEmbeddingProvider):
    """OpenAI embedding provider"""

    def __init__(self, config_data: OpenAIEmbeddingProviderConfigData) -> None:
        service_config_data = {
            'openai_api_key': config_data.api_key,
            'openai_api_version': config_data.api_version,
            'openai_api_base': config_data.api_url,
            'openai_api_type': config_data.api_type,
            'chunk_size': config_data.chunk_size,
        }
        self.__embeddings = OpenAIEmbeddings(**service_config_data)
        super().__init__(self.__embeddings)

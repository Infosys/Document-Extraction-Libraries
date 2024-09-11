# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

"""Module for OpenAI embedding provider class"""

from ....schema.config_data import BaseEmbeddingProviderConfigData
from ....embedding.interface.i_embedding_provider import IEmbeddingProvider
from .openai_service import OpenAIService
from ....schema.embedding_data import EmbeddingData


class OpenAIEmbeddingProviderConfigData(BaseEmbeddingProviderConfigData):
    """Domain class"""
    api_key: str
    api_version: str
    api_type: str
    api_url: str
    chunk_size: int
    model_name: str
    deployment_name: str


class OpenAIEmbeddingProvider(IEmbeddingProvider):
    """OpenAI embedding provider"""

    def __init__(self, config_data: OpenAIEmbeddingProviderConfigData) -> None:
        self.__embeddings = OpenAIService(model_name=config_data.model_name,
                                          api_key=config_data.api_key, api_base=config_data.api_url,
                                          api_version=config_data.api_version)
        self.__config_data = config_data
        super().__init__()

    def generate_embedding(self, text: str) -> EmbeddingData:
        text_embeddings = self.__embeddings.embed_query(text)
        vector = self.convert_to_numpy_array(text_embeddings)
        embedding_data = EmbeddingData(vector=vector,
                                       vector_dimension=len(text_embeddings),
                                       error_message=None,
                                       model_name=self.__config_data.model_name)
        return embedding_data

# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

"""Module for Custom embedding provider class"""

from ....schema.config_data import BaseEmbeddingProviderConfigData
from ....embedding.interface.i_embedding_provider import IEmbeddingProvider
from .custom_embedding_service import CustomEmbeddingService
from ....schema.embedding_data import EmbeddingData


class CustomEmbeddingProviderConfigData(BaseEmbeddingProviderConfigData):
    """Domain class"""
    api_key: str
    endpoint: str


class CustomEmbeddingProvider(IEmbeddingProvider):
    """Custom embedding provider"""

    def __init__(self, config_data: CustomEmbeddingProviderConfigData) -> None:
        self.__embeddings = CustomEmbeddingService(
            api_key=config_data.api_key, endpoint=config_data.endpoint)
        super().__init__()

    def generate_embedding(self, text: str) -> EmbeddingData:
        embedding_dict = self.__embeddings.generate_embedding(text)
        text_embeddings = embedding_dict['embedding']
        vector = self.convert_to_numpy_array(text_embeddings)
        embedding_data = EmbeddingData(vector=vector,
                                       vector_dimension=len(text_embeddings),
                                       error_message=None)
        return embedding_data

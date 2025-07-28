# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

"""Module for OpenAI embedding provider class"""

import os
import litellm
from ....schema.config_data import BaseEmbeddingProviderConfigData
from ....embedding.interface.i_embedding_provider import IEmbeddingProvider
from ....schema.embedding_data import EmbeddingData


class OpenAIFormatEmbeddingProviderConfigData(BaseEmbeddingProviderConfigData):
    """Domain class"""
    api_url: str
    api_key: str
    model_name: str
    api_version: str


class OpenAIFormatEmbeddingProvider(IEmbeddingProvider):
    """OpenAI embedding provider"""

    def __init__(self, config_data: OpenAIFormatEmbeddingProviderConfigData) -> None:
        self.config_data = config_data
        self.api_base = self.config_data.api_url
        self.api_key = self.config_data.api_key
        self.model_name = self.config_data.model_name
        self.api_version = self.config_data.api_version
        super().__init__()

    def generate_embedding(self, text: str) -> EmbeddingData:
        os.environ["AZURE_API_KEY"] = self.api_key

        response = litellm.embedding(
            api_base=self.api_base,
            api_key=self.api_key,
            model=self.model_name,
            api_version=self.api_version,
            input=[text],
            timeout=120)

        response_dict = response.json()
        text_embeddings = response_dict['data'][0].get('embedding')
        vector = self.convert_to_numpy_array(text_embeddings)
        embedding_data = EmbeddingData(vector=vector,
                                       vector_dimension=len(text_embeddings),
                                       error_message=None,
                                       model_name=self.config_data.model_name)
        return embedding_data

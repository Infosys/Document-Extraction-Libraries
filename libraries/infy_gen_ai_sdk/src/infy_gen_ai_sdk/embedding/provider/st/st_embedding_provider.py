# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

"""Module for Sentence Transformer embedding provider class"""

import requests
from ....embedding.interface.i_embedding_provider import IEmbeddingProvider
from ....schema.config_data import BaseEmbeddingProviderConfigData
from ....schema.embedding_data import EmbeddingData


class StEmbeddingProviderConfigData(BaseEmbeddingProviderConfigData):
    """Domain class"""


class StEmbeddingProvider(IEmbeddingProvider):
    """Sentence Transformer embedding provider"""

    def __init__(self, config_data: StEmbeddingProviderConfigData) -> None:
        base_url = config_data.api_url.rstrip('/')
        self.base_url = f"{base_url}/api/v1/model/embedding/generate"
        # self.model_name = config_data.model_name

    def generate_embedding(self, text: str) -> EmbeddingData:
        payload = {"text": text}
        response_obj = requests.post(
            self.base_url,
            json=payload,
            timeout=300
        )
        embedding_dict = response_obj.json()
        text_embeddings = embedding_dict.get('vector', [])
        vector = self.convert_to_numpy_array(text_embeddings)
        embedding_data = EmbeddingData(vector=vector,
                                       vector_dimension=embedding_dict.get(
                                           'vector_dimension'),
                                       error_message=embedding_dict.get(
                                           'error_message'),
                                       model_name=embedding_dict.get(
                                           'model_name')
                                       )
        return embedding_data

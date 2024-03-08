# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                   #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

"""Module for Sentence Transformer embedding provider class"""

from infy_gen_ai_sdk.embedding.interface.i_embedding_provider import IEmbeddingProvider
from infy_gen_ai_sdk.embedding.langchain.sentence_transformer_embeddings import SentenceTransformerEmbeddings
from infy_gen_ai_sdk.data.config_data import BaseEmbeddingProviderConfigData


class StEmbeddingProviderConfigData(BaseEmbeddingProviderConfigData):
    """Domain class"""


class StEmbeddingProvider(IEmbeddingProvider):
    """Sentence Transformer embedding provider"""

    def __init__(self, config_data: StEmbeddingProviderConfigData) -> None:
        service_config_data = {
            'base_url': config_data.api_url,
            'model': config_data.model_name
        }
        self.__embeddings = SentenceTransformerEmbeddings(
            **service_config_data)
        super().__init__(self.__embeddings)

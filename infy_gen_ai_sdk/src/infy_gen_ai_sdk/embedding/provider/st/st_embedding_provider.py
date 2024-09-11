# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

"""Module for Sentence Transformer embedding provider class"""

from ....embedding.interface.i_embedding_provider import IEmbeddingProvider
from ....schema.config_data import BaseEmbeddingProviderConfigData
from .st_service import StService
from ....schema.embedding_data import EmbeddingData


class StEmbeddingProviderConfigData(BaseEmbeddingProviderConfigData):
    """Domain class"""


class StEmbeddingProvider(IEmbeddingProvider):
    """Sentence Transformer embedding provider"""

    def __init__(self, config_data: StEmbeddingProviderConfigData) -> None:
        self.__config_data = config_data
        if config_data.model_home_path:
            st_service_obj = StService(model_name=config_data.model_name,
                                       model_home_path=config_data.model_home_path)
        else:
            st_service_obj = StService(model_name=config_data.model_name,
                                       base_url=config_data.api_url)
        self.__st_service_obj = st_service_obj
        super().__init__()

    def generate_embedding(self, text: str) -> EmbeddingData:
        embedding_dict = self.__st_service_obj.generate_embedding(text,
                                                                  self.__config_data.model_name)
        text_embeddings = embedding_dict['embedding']
        vector = self.convert_to_numpy_array(text_embeddings)
        embedding_data = EmbeddingData(vector=vector,
                                       vector_dimension=embedding_dict['size'],
                                       error_message=embedding_dict['error_message'],
                                       model_name=embedding_dict['model_name'])
        return embedding_data

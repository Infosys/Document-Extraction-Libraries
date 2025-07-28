# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

"""This module contains the OpenAIFormatCustomEmbeddingProvider class."""

from typing import List
from langchain_core.embeddings import Embeddings
import infy_gen_ai_sdk


class OpenAIFormatCustomEmbeddingProvider(Embeddings):
    """A custom Embeddings class"""
    api_url: str = None
    api_key: str = None
    model_name: str = None
    api_version: str = None

    def __init__(self, model_name: str, api_key: str, api_url: str, api_version: str):
        self.api_url = api_url
        self.api_key = api_key
        self.model_name = model_name
        self.api_version = api_version

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed search docs."""
        embeddings = []
        embedding_provider_config_data = infy_gen_ai_sdk.embedding.provider.OpenAIFormatEmbeddingProviderConfigData(
            **{
                "api_url": self.api_url,
                "api_key": self.api_key,
                "model_name": self.model_name,
                "api_version": self.api_version
            })
        embedding_provider = infy_gen_ai_sdk.embedding.provider.OpenAIFormatEmbeddingProvider(
            embedding_provider_config_data)
        embeddings = [
            embedding_provider.generate_embedding(text).vector
            for text in texts
        ]
        return embeddings

    def embed_query(self, text: str) -> List[float]:
        """Embed query text."""
        return self.embed_documents([text])[0]

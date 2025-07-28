# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import time
from typing import List
import logging
from openai import AzureOpenAI
import infy_fs_utils

from ....common.singleton import Singleton
from ....common import Constants


class OpenAIService(metaclass=Singleton):
    """Wrapper class for Open AI library"""

    def __init__(self, model_name: str, api_key: str, api_base: str, api_version) -> None:

        self.openai_api_key = api_key
        self.openai_api_version = api_version
        self.openai_api_base = api_base
        self.model = model_name

    def _create_embeddings(self, input) -> List[float]:
        if infy_fs_utils.manager.FileSystemLoggingManager().has_fs_logging_handler():
            __logger = infy_fs_utils.manager.FileSystemLoggingManager(
            ).get_fs_logging_handler().get_logger()
        else:
            __logger = logging.getLogger(__name__)
        try:
            response_list: List[float] = []
            client = AzureOpenAI(
                api_key=self.openai_api_key,
                api_version=self.openai_api_version,
                azure_endpoint=self.openai_api_base
            )
            embeddings = client.embeddings.create(
                input=[input], model=self.model)
            response_list = embeddings.data[0].embedding
        except Exception as ex:
            message = 'Error occurred while creating embedddings'
            __logger.exception(message)
            raise IOError(message) from ex
        return response_list

    def _embed(self, input: List[str]) -> List[List[float]]:
        embeddings_list: List[List[float]] = []
        for prompt in input:
            embeddings = self._create_embeddings(prompt)
            embeddings_list.append(embeddings)
        return embeddings_list

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed documents using a Ollama deployed embedding model.

        Args:
            texts: The list of texts to embed.

        Returns:
            List of embeddings, one for each text.
        """
        embeddings = self._embed(texts)
        return embeddings

    def embed_query(self, text: str) -> List[float]:
        """Embed a query using a Ollama deployed embedding model.

        Args:
            text: The text to embed.

        Returns:
            Embeddings for the text.
        """
        # self._model_initialize()
        embedding = self._embed([text])[0]
        return embedding

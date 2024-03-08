# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                   #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#


import ast
import requests

from langchain.pydantic_v1 import BaseModel, Extra
from langchain.schema.embeddings import Embeddings
from typing import Any, Dict, List, Mapping, Optional

from infy_gen_ai_sdk.common.logger_factory import LoggerFactory


class SentenceTransformerEmbeddings(BaseModel, Embeddings):
    base_url: str = ""
    model: str = ""

    def _call_api(self, input) -> List[float]:
        __logger = LoggerFactory().get_logger()
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json',
        }

        json_data = {
            'text': input,
            'modelName': self.model,
        }
        try:
            response_list: List[float] = []
            response = requests.post(
                self.base_url, headers=headers, json=json_data, timeout=120)
            if response.status_code == 200:
                content = ast.literal_eval(response.content.decode("utf-8"))
                if content.get('responseCde') == 0:
                    content_response = content.get('response')
                    response_list = content_response.get('embedding')
                else:
                    raise ValueError(
                        f'Error in API response {content.get("responseMsg")}')
            else:
                message = f'Error in calling API {response.status_code}'
                __logger.error(message)
                raise IOError(message)
        except Exception as ex:
            message = 'Error occurred while calling API'
            __logger.exception(message)
            raise IOError(message) from ex
        return response_list

    def _embed(self, input: List[str]) -> List[List[float]]:
        embeddings_list: List[List[float]] = []
        for prompt in input:
            embeddings = self._call_api(prompt)
            # embeddings_list = transf_embeddings.tolist()
            embeddings_list.append(embeddings)
        return embeddings_list

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed documents using a Ollama deployed embedding model.

        Args:
            texts: The list of texts to embed.

        Returns:
            List of embeddings, one for each text.
        """
        # self._model_initialize()
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

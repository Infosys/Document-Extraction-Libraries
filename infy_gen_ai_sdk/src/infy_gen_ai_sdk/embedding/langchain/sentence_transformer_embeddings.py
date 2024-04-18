# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#


import ast
import requests
import logging
from typing import Any, Dict, List, Mapping, Optional
from langchain.pydantic_v1 import BaseModel, Extra
from langchain.schema.embeddings import Embeddings
import infy_fs_utils
from infy_gen_ai_sdk.embedding.langchain.sentence_transformer_service import SentenceTransformerService
from ...common import Constants


class SentenceTransformerEmbeddings(BaseModel, Embeddings):
    base_url: str = None
    model: str = ""
    model_home_path: str = None

    def _call_api(self, input) -> List[float]:
        if infy_fs_utils.manager.FileSystemLoggingManager().has_fs_logging_handler(
                Constants.FSLH_GEN_AI_SDK):
            __logger = infy_fs_utils.manager.FileSystemLoggingManager(
            ).get_fs_logging_handler(Constants.FSLH_GEN_AI_SDK).get_logger()
        else:
            __logger = logging.getLogger(__name__)
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
            if self.model_home_path:
                sentence_transform_service_obj = SentenceTransformerService(model_name=self.model,
                                                                            model_home_path=self.model_home_path)
                embeddings_result = sentence_transform_service_obj.generate_embedding(prompt,
                                                                                      self.model)
                embeddings = embeddings_result.get('embedding')
            else:
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

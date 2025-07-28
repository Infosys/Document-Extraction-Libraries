# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import sys
from common.app_config_manager import AppConfigManager
from common.ainauto_logger_factory import AinautoLoggerFactory
from service.st_service import StService
from schema.embedding_data import EmbeddingData
from ray import serve
from fastapi import FastAPI, Body
app_fastapi = FastAPI()

app_config = AppConfigManager().get_app_config()
logger = AinautoLoggerFactory().get_logger()


@serve.ingress(app_fastapi)
class EmbeddingGeneratorBaseApp():
    def __init__(self):
        self.__model_name = app_config['MODEL_PATHS']['embed_model_name_1']
        self.__model_path = app_config['MODEL_PATHS']['embed_model_path_1']
        self.__st_service_obj = StService(model_name=self.__model_name,
                                          model_home_path=self.__model_path)

    @app_fastapi.post("/generate")
    def generate_embedding(self, text: str = Body(..., embed=True)) -> EmbeddingData:
        embedding_dict = self.__st_service_obj.generate_embedding(text,
                                                                  self.__model_name)
        text_embeddings = embedding_dict['embedding']
        vector = text_embeddings
        embedding_data = EmbeddingData(vector=[vector],
                                       vector_dimension=embedding_dict['size'],
                                       error_message=embedding_dict['error_message'],
                                       model_name=embedding_dict['model_name'])
        return embedding_data


if not 'pytest' in sys.modules:
    @serve.deployment()
    class EmbeddingGenerator_l6v2(EmbeddingGeneratorBaseApp):
        pass
    app = EmbeddingGenerator_l6v2.bind()

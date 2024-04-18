# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import time
from sentence_transformers import SentenceTransformer
from infy_gen_ai_sdk.common.singleton import Singleton


class SentenceTransformerService(metaclass=Singleton):

    def __init__(self,model_name,model_home_path):
        model_to_obj_dict = {}
        overall_elapsed_time = 0
        if model_name and model_home_path:
            start_time = time.time()
            model_path=model_home_path+'/'+model_name
            model_to_obj_dict[model_name] = SentenceTransformer(model_path)
            elapsed_time = round(time.time() - start_time, 3)
            print(f'Load time for model {model_name}: {elapsed_time} secs')
            overall_elapsed_time += elapsed_time
        self.__model_to_obj_dict = model_to_obj_dict

    def generate_embedding(self, text, model_name) -> dict:
        result = {
            'embedding': [],
            'size': 0,
            'error_message': None,
            'model_name': model_name
        }
        model_obj = self.__model_to_obj_dict.get(model_name, None)
        if not model_obj:
            result['error_message'] = f'Model not found: {model_name}'
        else:
            embedding_as_numpy = model_obj.encode(text)
            embedding_as_list = embedding_as_numpy.astype(float).tolist()
            result['embedding'] = embedding_as_list
            result['size'] = len(embedding_as_list)

        return result

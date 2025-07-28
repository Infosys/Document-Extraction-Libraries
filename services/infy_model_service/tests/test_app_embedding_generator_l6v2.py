# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#
import time
import requests
from models.app_embedding_generator_l6v2 import EmbeddingGeneratorBaseApp


def test_base_app():
    """ Test method for testing base app directly"""
    base_app = EmbeddingGeneratorBaseApp()
    embedding_data = base_app.generate_embedding("Hello world!")
    assert {
        "vector_dimension": 384,
        "error_message": "",
        "model_name": 'all-MiniLM-L6-v2'
    } == {
        "vector_dimension": embedding_data.vector_dimension,
        "error_message": embedding_data.error_message,
        "model_name": embedding_data.model_name
    }
    assert len(embedding_data.vector[0]) == 384


def test_ray_app():
    """ Test method for testing all-MiniLM-L6-v2 model hosted on ray server"""
    average_time = 0
    for i in range(10):
        start = time.time()
        english_text = "Hello world!"
        response_obj = requests.post(
            "http://localhost:8003/modelservice/api/v1/model/embedding/generate", json=english_text, timeout=10)
        response_dict = response_obj.json()
        print(i, response_dict.get("vector_dimension"))
        elapsed_time = time.time() - start
        average_time += elapsed_time
        print(f"Time taken: {elapsed_time} seconds")

    print(f"Average time taken: {average_time/10} seconds")

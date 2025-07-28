# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

""" Test FAISS directly with SentenceTransformer to represent any embedding model"""
import json
import os
import tempfile
import pytest
import numpy as np
import faiss
import infy_gen_ai_sdk

# Create inside temp folder for the purpose of unit testing
DATA_ROOT_PATH = f"{tempfile.gettempdir()}/{__name__}"
DATA_ROOT_PATH = f"C:/temp/unittest/infy_gen_ai_sdk/{__name__}/STORAGE"

DOCUMENTS = [
    "The concert's electric guitar solo electrified the cheering crowd.",
    "Exploring the ancient ruins uncovered fascinating historical artifacts.",
    "The robot's advanced sensors navigated the complex maze.",
    "Baking the chocolate cake filled the kitchen with delicious aromas.",
    "The comet's dazzling tail streaked across the night sky."
]
# FAISS file saves only vectors/embeddings, so we need to save the content in a separate file
VECTOR_DB_INDEX_PATH = f"{DATA_ROOT_PATH}/my_db.faiss"
VECTOR_DB_CONTENT_PATH = f"{DATA_ROOT_PATH}/my_db.json"

model_home_path = r"C:\MyProgramFiles\AI\models\all-MiniLM-L6-v2"


@pytest.fixture(scope='module', autouse=True)
def pre_test(create_root_folders):
    """Initialization method"""
    create_root_folders([DATA_ROOT_PATH])


def test_create_search_vector_db():
    """Test method"""

    embedding_provider_config_data = infy_gen_ai_sdk.embedding.provider.StEmbeddingProviderConfigData(
        **{
            "api_url": os.environ['INFY_MODEL_SERVICE_BASE_URL']
        })
    embedding_provider = infy_gen_ai_sdk.embedding.provider.StEmbeddingProvider(
        embedding_provider_config_data)

    def _create_index():
        metadata_dict = {}
        VECTOR_DIMENSION = 384
        index = faiss.IndexFlatL2(VECTOR_DIMENSION)
        for _, document in enumerate(DOCUMENTS):
            embedding = embedding_provider.generate_embedding(
                document)
            vector = embedding.vector[0]
            # if vector.ndim == 1:
            #     vector = vector.reshape(1, vector.shape[0])
            vector = np.array([vector])
            faiss.normalize_L2(vector)
            # Pass the vector as an argument to the add method
            index.add(vector)
            _id = str(index.ntotal - 1)
            metadata_dict[_id] = document

        faiss.write_index(index, VECTOR_DB_INDEX_PATH)
        with open(VECTOR_DB_CONTENT_PATH, 'w', encoding='utf-8') as file:
            json.dump(metadata_dict, file)

    def _search_index():
        index = faiss.read_index(VECTOR_DB_INDEX_PATH)
        metadata_dict = {}
        with open(VECTOR_DB_CONTENT_PATH, 'r', encoding='utf-8') as file:
            metadata_dict = json.load(file)

        queries = [
            "What happened in the kitchen?",
            "What is the cause of global warming?",
            "What did the robot do to the crowd?",
            "What did the robot have?"
        ]

        print("---------------------")
        for query in queries:
            embedding = embedding_provider.generate_embedding(query)
            vector_list = embedding.vector[0]
            vector = np.array([vector_list])
            faiss.normalize_L2(vector)
            k = min(index.ntotal, 3)
            distances, distance_ids = index.search(vector, k=k)
            print(f"Query: {query}")
            for distance, distance_id in zip(distances[0], distance_ids[0]):
                _id = str(distance_id)
                print(
                    f"Distance: {distance}, Document: {metadata_dict[_id]}")
            print("---------------------")

    def _search_by_removal_of_each_word_from_original_content():
        index = faiss.read_index(VECTOR_DB_INDEX_PATH)
        metadata_dict = {}
        with open(VECTOR_DB_CONTENT_PATH, 'r', encoding='utf-8') as file:
            metadata_dict = json.load(file)

        # Select a particular sentence for this test
        sentence = DOCUMENTS[3]
        words = sentence.split(" ")
        for idx, _ in enumerate(words):
            _words = words[0:idx] + words[idx+1:]
            _sentence = " ".join(_words)
            print(_sentence)
            embedding = embedding_provider.generate_embedding(_sentence)
            vector_list = embedding.vector[0]
            vector = np.array([vector_list])
            faiss.normalize_L2(vector)
            k = min(index.ntotal, 3)
            distances, ann = index.search(vector, k=k)
            print(f"Sentence: {_sentence}")
            for idx, (distance, ann_idx) in enumerate(zip(distances[0], ann[0])):
                _id = str(ann_idx)
                print(
                    f"Distance: {distance}, Document: {metadata_dict[_id]}")
                if idx == 0:
                    # Since only a word is removed from the original content, the distance should be very low
                    assert distance < 0.25
                    assert metadata_dict[_id] == sentence
                else:
                    assert distance > 1
            print("---------------------")

    _create_index()
    _search_index()
    _search_by_removal_of_each_word_from_original_content()

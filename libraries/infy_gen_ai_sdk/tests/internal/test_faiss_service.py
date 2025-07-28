# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

""" Test FAISS wrapper service with SentenceTransformer to represent any embedding model"""
import os
import pytest
import numpy as np
from infy_gen_ai_sdk.vectordb.provider.faiss.faiss_service import FaissService
import infy_gen_ai_sdk


# Create inside temp folder for the purpose of unit testing
CONTAINER_ROOT_PATH = f"C:/temp/unittest/infy_gen_ai_sdk/{__name__}/CONTAINER"

DOCUMENTS = [
    "The concert's electric guitar solo electrified the cheering crowd.",
    "Exploring the ancient ruins uncovered fascinating historical artifacts.",
    "The robot's advanced sensors navigated the complex maze.",
    "Baking the chocolate cake filled the kitchen with delicious aromas.",
    "The comet's dazzling tail streaked across the night sky."
]
# FAISS file saves only vectors/embeddings, so we need to save the content in a separate file
VECTOR_DB_PATH = f"{CONTAINER_ROOT_PATH}/my_db"
DB_NAME = "thoughts"
model_home_path = r"C:\MyProgramFiles\AI\models\all-MiniLM-L6-v2"


@pytest.fixture(scope='module', autouse=True)
def pre_test(create_root_folders):
    """Initialization method"""
    create_root_folders([CONTAINER_ROOT_PATH])


def test_create_search_vector_db():
    """Test method"""
    embedding_provider_config_data = infy_gen_ai_sdk.embedding.provider.StEmbeddingProviderConfigData(
        **{
            "api_url": os.environ['INFY_MODEL_SERVICE_BASE_URL']
        })
    embedding_provider = infy_gen_ai_sdk.embedding.provider.StEmbeddingProvider(
        embedding_provider_config_data)

    def _create_db():
        faiss_service_obj = FaissService(VECTOR_DB_PATH, DB_NAME)
        VECTOR_DIMENSION = 384  # For model all-MiniLM-L6-v2
        faiss_service_obj.create_new(VECTOR_DIMENSION)
        for document in DOCUMENTS:
            embedding = embedding_provider.generate_embedding(
                document)
            vector_list = embedding.vector[0]
            vector = np.array([vector_list])
            faiss_service_obj.add_record(vector, document, {})

        faiss_service_obj.save_local()
        assert os.path.exists(f"{VECTOR_DB_PATH}/{DB_NAME}.faiss")
        assert os.path.exists(f"{VECTOR_DB_PATH}/{DB_NAME}.data.json")
        assert os.path.exists(f"{VECTOR_DB_PATH}/{DB_NAME}.map.json")
        records_added = faiss_service_obj.get_records()
        assert len(records_added) == len(DOCUMENTS)

    def _export_db():
        faiss_service_obj = FaissService(VECTOR_DB_PATH, DB_NAME)
        faiss_service_obj.load_local()
        EXPORT_FILE_PATH = f"{CONTAINER_ROOT_PATH}/my_db.json"
        record_count = faiss_service_obj.export_db(EXPORT_FILE_PATH)
        assert os.path.exists(EXPORT_FILE_PATH)
        assert record_count == len(DOCUMENTS)

    def _search_db():
        faiss_service_obj = FaissService(VECTOR_DB_PATH, DB_NAME)
        faiss_service_obj.load_local()

        queries = [
            "What happened in the kitchen?",
            "What is the cause of global warming?",
            "What did the robot do to the crowd?",
            "What did the robot have?"
        ]

        print("---------------------")
        for query in queries:
            embedding = embedding_provider.generate_embedding(
                query)
            vector_list = embedding.vector[0]
            vector = np.array([vector_list])
            records = faiss_service_obj.search_records(vector, 3)
            print(f"Query: {query}")
            for record in records:
                print(
                    f"Distance: {record['distance']}, Content: {record['content']}")
            print("---------------------")

    def _search_by_removal_of_each_word_from_original_content():
        faiss_service_obj = FaissService(VECTOR_DB_PATH, DB_NAME)
        faiss_service_obj.load_local()

        # Select a particular sentence for this test
        sentence = DOCUMENTS[3]
        words = sentence.split(" ")
        for idx, _ in enumerate(words):
            _words = words[0:idx] + words[idx+1:]
            _sentence = " ".join(_words)
            print(_sentence)
            embedding = embedding_provider.generate_embedding(
                _sentence)
            vector_list = embedding.vector[0]
            vector = np.array([vector_list])

            records = faiss_service_obj.search_records(vector, 3)
            print(f"Sentence: {_sentence}")
            for idx, record in enumerate(records):
                distance = record['distance']
                content = record['content']
                print(
                    f"Distance: {distance}, Document: {content}")
                if idx == 0:
                    # Since only a word is removed from the original content, the distance should be very low
                    assert distance < 0.25
                    assert content == sentence
                else:
                    assert distance > 1
            print("---------------------")

    _create_db()
    _export_db()
    _search_db()
    _search_by_removal_of_each_word_from_original_content()

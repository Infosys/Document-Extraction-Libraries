# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                   #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

from infy_gen_ai_sdk.embedding.langchain.sentence_transformer_embeddings import SentenceTransformerEmbeddings
import time
import os


def test_1():
    # keep model in model home path folder
    service_config_data = {

        'model': "all-MiniLM-L6-v2",
        'model_home_path': r"C:\MyProgramFiles\AI\models"
    }

    st_embedding = SentenceTransformerEmbeddings(**service_config_data)
    list1 = st_embedding.embed_query("Hello")
    # generate timestamp and store into variable
    timestamp = time.time()
    with open(f"./test_embedding_{timestamp}.json", "w") as f:
        f.write(str(list1))
    print(list1)

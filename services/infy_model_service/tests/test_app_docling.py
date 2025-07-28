# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import pytest
import time
import os
import requests
from models.app_docling import DoclingBaseApp


@pytest.mark.skip(reason="To run this test, remove async and await from target method")
def test_base_app():
    """ Test method for testing base app directly"""
    os.environ['USE_DOCLING_CACHE'] = 'True'
    base_app = DoclingBaseApp()
    source = ".\data\sample_1.png"
    file = open(source, "rb")
    result = base_app.extract_from_file_obj(file)
    assert result['unique_id'] is not None
    assert result['document_data'] is not None


def test_app_docling_extractor_retriever():
    """ Test method for testing all-MiniLM-L6-v2 model hosted on ray server"""
    average_time = 0
    start = time.time()
    source = ".\data\sample_1.png"
    try:
        with open(source, 'rb') as f:
            files = {'file': f}
            response_obj = requests.post(
                "http://localhost:8003/modelservice/api/v1/model/docling/extract", files=files, timeout=400)

            document_data = response_obj.json()

        unique_id = document_data.get("unique_id")
        response = requests.post(
            "http://localhost:8003/modelservice/api/v1/model/docling/retrieve",
            json={"unique_id": unique_id,
                  "document_html": False, "table_html": True},
            timeout=10)
        table_data_html = response.json()
    except Exception as e:
        print(f"Error: {e}")

    elapsed_time = time.time() - start
    print(f"Time taken: {elapsed_time} seconds")
    assert document_data.get("document_data") is not None
    assert table_data_html.get("table_data_html") is not None

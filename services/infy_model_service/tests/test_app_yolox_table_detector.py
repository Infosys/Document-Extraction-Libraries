# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#
import pytest
import time
import requests
from models.app_yolox_table_detector import YoloxTableDetectorBaseApp


@pytest.mark.skip(reason="To run this test, remove async and await from target method")
def test_yolox_td_base_app():
    """ Test method for testing base app directly"""
    base_app = YoloxTableDetectorBaseApp()
    file_path = ".\data\sample_1.png"
    with open(file_path, "rb") as file:
        response = base_app.detect_table(file)
    table_response = response
    print("table_response", table_response)
    assert hasattr(table_response.table_data[0], 'bbox')
    assert hasattr(table_response.table_data[0], 'td_confidence_pct')
    assert table_response.table_data[0].bbox == [
        109.6, 1995.86, 4050.69, 2937.74]
    assert table_response.table_data[1].bbox == [
        253.03, 3243.47, 1201.77, 4048.87]


def test_yolox_td_ray_app():
    """ Test method for testing yolox model hosted on ray server for table detection"""
    average_time = 0

    start = time.time()
    file_path = ".\data\sample_1.png"
    url = "http://localhost:8003/modelservice/api/v1/model/yolox/detect"
    # Open the file in binary mode and send it to the server
    with open(file_path, "rb") as file:
        response_obj = requests.post(
            url, files={"file": file}, timeout=400)
    response_dict = response_obj.json()
    print("response_dict", response_dict)
    elapsed_time = time.time() - start
    average_time += elapsed_time
    print(f"Time taken: {elapsed_time} seconds")

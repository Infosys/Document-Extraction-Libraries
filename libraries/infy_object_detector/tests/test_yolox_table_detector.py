# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

"""Testing module"""
import os
import json
import time
import pytest
import infy_object_detector
from infy_object_detector.detector.table_detector import TableDetector


@pytest.fixture(scope='module', autouse=True)
def setup() -> dict:
    """Initialization method"""


def test_yolox_table_detector():
    """This is a Test method for yolox table detector call to service"""
    start = time.time()
    image_path = "./data/sample/input/sample_1.png"
    url = f"{os.environ['INFY_MODEL_SERVICE_BASE_URL']}/api/v1/model/yolox"
    table_detector_provider = infy_object_detector.detector.provider.YoloxTdProvider(
        infy_object_detector.detector.provider.YoloxTdProviderConfigData(
            **{

                "model_service_url": url
            }
        ))

    table_detector = TableDetector(table_detector_provider)
    table_response = table_detector.detect_table(
        infy_object_detector.detector.provider.YoloxTdRequestData(
            **{
                "image_file_path": image_path
            }
        ))
    elapsed_time = time.time() - start
    print(json.dumps(table_response.dict(), indent=4))
    print(f"Time taken: {elapsed_time} seconds")
    assert hasattr(table_response.table_data[0], 'bbox')
    assert hasattr(table_response.table_data[0], 'td_confidence_pct')
    assert table_response.table_data[0].bbox == [
        109.6, 1995.86, 4050.69, 2937.74]
    assert table_response.table_data[1].bbox == [
        253.03, 3243.47, 1201.77, 4048.87]


def test_yolox_td_throughput():
    """This is a Test method for dummy table provider"""

    start = time.time()
    doc_count = 10
    url = f"{os.environ['INFY_MODEL_SERVICE_BASE_URL']}/api/v1/model/yolox"
    for i in range(0, doc_count):
        image_path = "./data/sample/input/sample_1.png"

        table_detector_provider = infy_object_detector.detector.provider.YoloxTdProvider(
            infy_object_detector.detector.provider.YoloxTdProviderConfigData(
                **{

                    "model_service_url": url
                }
            ))
        table_detector = TableDetector(table_detector_provider)
        table_response = table_detector.detect_table(
            infy_object_detector.detector.provider.YoloxTdRequestData(
                **{
                    "image_file_path": image_path
                }
            ))

    elapsed_time = time.time() - start
    print(json.dumps(table_response.dict(), indent=4))
    print(f"Time taken: {elapsed_time} seconds")
    print(f"Throughput: {doc_count/elapsed_time} images per second")
    print(f"Average time taken per image: {elapsed_time/doc_count} seconds")
    assert hasattr(table_response.table_data[0], 'bbox')
    assert hasattr(table_response.table_data[0], 'td_confidence_pct')
    assert table_response.table_data[0].bbox == [
        109.6, 1995.86, 4050.69, 2937.74]
    assert table_response.table_data[1].bbox == [
        253.03, 3243.47, 1201.77, 4048.87]

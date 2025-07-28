# ===============================================================================================================#
# Copyright 2025 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#
"""Testing module to demonstrate table detection and extraction using Yolox and Docling models."""
import os
import json
import time
import math
import pytest
import infy_object_detector
import infy_table_extractor as ite
from infy_object_detector.detector.table_detector import TableDetector
from infy_object_detector.structure_recogniser.provider.bordered_table_tsr_provider import (
    BorderedTableTsrProviderConfigData, BorderedTableTsrProvider, BorderedTableTsrProviderRequestData)


@pytest.fixture(scope='module', autouse=True)
def setup() -> dict:
    """Initialization method"""


def __pretty_print(dictionary):
    p = json.dumps(dictionary, indent=4)
    print(p.replace('\"', '\''))


def __save_to_json(dictionary, file_path):
    if os.path.exists(file_path):
        os.remove(file_path)
    with open(file_path, 'w') as file:
        file.write(json.dumps(dictionary, indent=4))


def __save_to_html(dictionary, file_path):
    if os.path.exists(file_path):
        os.remove(file_path)
    html_content = ""
    for table_list in dictionary:
        for table_html_data in table_list.table_html_data:
            html_content += table_html_data.cell_data_html
    with open(file_path, 'w') as file:
        file.write(html_content)


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

    print(json.dumps(table_response.dict(), indent=4))

    response_list = []
    table_number = 1
    for table_data in table_response.table_data:
        table_bbox = []
        table_data.bbox = [
            math.ceil(x) for x in table_data.bbox]

        table_bbox.append(table_data.bbox[0])
        table_bbox.append(table_data.bbox[1])
        table_bbox.append(
            table_data.bbox[2] - table_data.bbox[0])
        table_bbox.append(
            table_data.bbox[3] - table_data.bbox[1])

        config_param_dict: dict = {
            'custom_cells': [{'rows': [], 'columns': []}],
            'col_header': {'use_first_row': True, 'values': []},
            'deskew_image_reqd': False,
            'auto_detect_border': False,
            'image_cell_cleanup_reqd': True,
            'output': {
                'path': None,
                'format': None
            },
            'rgb_line_skew_detection_method': [ite.interface.RgbSkewDetectionMethod.CONVOLUTION_CONTRAST_METHOD],
            'line_detection_method': [ite.interface.LineDetectionMethod.RGB_LINE_DETECT]
        }

        bordered_table_extractor_provider_config_data = BorderedTableTsrProviderConfigData(
            **{
                "model_path": "C:/Program Files/Tesseract-OCR/tesseract.exe",
                "model_name": "Tesseract",
                "ocr_engine_exe_dir_path": "",
                "ocr_engine_model_dir_path": "",
                "method_name": "rgb",
                "temp_folder_path": "C:/temp/",
                "config_param_dict": config_param_dict

            })

        provider = BorderedTableTsrProvider(
            bordered_table_extractor_provider_config_data)
        table_request_data = BorderedTableTsrProviderRequestData(
            image_file_path='./data/sample/input/sample_1.png',
            bbox=table_bbox)  # bbox format -> [x1, y1, width, height]
        response = provider.extract_table_data(table_request_data)
        table_number += 1
        response_list.append(response)
    elapsed_time = time.time() - start
    __pretty_print([response.dict() for response in response_list])
    # Save the HTML content to a file
    html_file_path = './data/sample/output/sample_1.png_yolox_ite.html'
    __save_to_html(response_list, html_file_path)
    __save_to_json([response.dict() for response in response_list],
                   './data/sample/output/sample_1.png_yolox_ite.json')


def test_docling_td_tsr():
    """Test the Docling Table Detector and Extractor Provider"""
    ### Make sure the model service is running and urls are working before running this test ###
    image_path = "./data/sample/input/sample_1.png"
    url = f"{os.environ['INFY_MODEL_SERVICE_BASE_URL']}/api/v1/model/docling"
    response_list = []
    table_detector_provider = infy_object_detector.detector.provider.DoclingTableTdTsrProvider(
        infy_object_detector.detector.provider.DoclingTableTdTsrProviderConfigData(
            **{
                "model_service_url": url,
                "is_table_html_view": True
            }
        ))

    table_detector = TableDetector(table_detector_provider)
    response = table_detector.detect_table(
        infy_object_detector.detector.provider.DoclingTableTdTsrProviderRequestData(
            **{
                "image_file_path": image_path
            }
        ))

    response_list.append(response)

    __pretty_print([response.dict() for response in response_list])
    # Save the HTML content to a file
    html_file_path = './data/sample/output/sample_1.png_docling.html'
    __save_to_html(response_list, html_file_path)
    __save_to_json([response.dict() for response in response_list],
                   './data/sample/output/sample_1.png_docling.json')
    assert response is not None and response.table_data is not None
    assert response.table_data[0].bbox is not None
    assert response.table_data[1].bbox is not None

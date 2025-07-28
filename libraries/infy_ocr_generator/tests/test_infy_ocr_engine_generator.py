# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import os
import logging
import tempfile
import pytest
from infy_ocr_generator.ocr_generator import OcrGenerator
from infy_ocr_generator.providers.infy_ocr_engine_data_service_provider import InfyOcrEngineDataServiceProvider


@pytest.fixture(scope='module', autouse=True)
def pre_test():
    """Initialization method"""
    # Logging configuration
    if not os.path.exists("./logs"):
        os.makedirs("./logs")
    logging.basicConfig(filename=("./logs" + "/app_log.log"),
                        format="%(asctime)s- %(levelname)s- %(message)s", level=logging.INFO,
                        datefmt="%d-%b-%y %H:%M:%S",)
    logger = logging.getLogger()
    logger.info('Initialization Completed')


def test_ocr_format_hocr():
    """Test method"""
    EXPECTED_FILE_PATH = "./data/sample_1.png.hocr"
    if os.path.exists(EXPECTED_FILE_PATH):
        os.remove(EXPECTED_FILE_PATH)

    CONFIG_PARAMS_DICT = {
        'ocr_engine': {
            'exe_dir_path': 'C:/MyProgramFiles/InfyOcrEngine',
            'model_dir_path': 'C:/MyProgramFiles/AI/models/tessdata',
            'ocr_format': 'hocr',
            'lang': 'eng'
        }
    }

    ocr_engine_provider = InfyOcrEngineDataServiceProvider(
        config_params_dict=CONFIG_PARAMS_DICT)

    ocr_generator_obj = OcrGenerator(
        data_service_provider=ocr_engine_provider)
    img_file_path = './data/sample_1.png'
    img_file_path = os.path.abspath(img_file_path)

    ocr_result_list = ocr_generator_obj.generate(
        doc_data_list=[{'doc_path': img_file_path, 'pages': '1'}]
    )
    assert len(ocr_result_list) == 1

    ocr_result = ocr_result_list[0]
    assert not ocr_result['error']
    assert os.path.exists(ocr_result['output_doc'])
    assert os.path.normpath(ocr_result['output_doc']) == os.path.normpath(
        os.path.abspath(EXPECTED_FILE_PATH))
    # Verify content
    with open(ocr_result['output_doc'], 'r', encoding='utf-8') as f:
        content = f.read()
        assert content.startswith('<!DOCTYPE html')


def test_ocr_format_txt():
    """Test method"""
    # Give a specific output folder e.g. a temp dir
    output_path = tempfile.mkdtemp()

    EXPECTED_FILE_PATH = f"{output_path}/sample_1.png.txt"
    if os.path.exists(EXPECTED_FILE_PATH):
        os.remove(EXPECTED_FILE_PATH)

    CONFIG_PARAMS_DICT = {
        'ocr_engine': {
            'exe_dir_path': 'C:/MyProgramFiles/InfyOcrEngine',
            'model_dir_path': 'C:/MyProgramFiles/AI/models/tessdata',
            'ocr_format': 'txt',
            'lang': 'eng'
        }
    }

    ocr_engine_provider = InfyOcrEngineDataServiceProvider(
        config_params_dict=CONFIG_PARAMS_DICT,
        output_dir=output_path)

    ocr_generator_obj = OcrGenerator(
        data_service_provider=ocr_engine_provider)
    img_file_path = './data/sample_1.png'
    img_file_path = os.path.abspath(img_file_path)

    ocr_result_list = ocr_generator_obj.generate(
        doc_data_list=[{'doc_path': img_file_path, 'pages': '1'}]
    )
    assert len(ocr_result_list) == 1

    ocr_result = ocr_result_list[0]

    assert not ocr_result['error']
    assert os.path.exists(ocr_result['output_doc'])
    assert os.path.normpath(ocr_result['output_doc']) == os.path.normpath(
        os.path.abspath(EXPECTED_FILE_PATH))
    # Verify content
    with open(ocr_result['output_doc'], 'r', encoding='utf-8') as f:
        content = f.read()
        assert 'GRADE SHEET' in content

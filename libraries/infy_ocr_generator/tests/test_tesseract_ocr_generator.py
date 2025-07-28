# ===============================================================================================================#
# Copyright 2021 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import os
import glob
import copy
import logging
import pytest
from infy_ocr_generator.ocr_generator import OcrGenerator
from infy_ocr_generator.providers.tesseract_ocr_data_service_provider import TesseractOcrDataServiceProvider
from .test_util import TestUtil

# Create inside temp folder for the purpose of unit testing
CONTAINER_ROOT_PATH = f"C:/temp/unittest/infy_ocr_generator/{__name__}/CONTAINER"


@pytest.fixture(scope='module', autouse=True)
def pre_test(create_root_folders):
    """Initialization method"""
    create_root_folders([CONTAINER_ROOT_PATH])
    yield  # Run all test methods
    # Post run cleanup


def test_tesseract_ocr_generator():
    """Test method"""
    # Logging configuration
    if not os.path.exists("./logs"):
        os.makedirs("./logs")
    logging.basicConfig(filename=("./logs" + "/app_log.log"),
                        format="%(asctime)s- %(levelname)s- %(message)s", level=logging.INFO,
                        datefmt="%d-%b-%y %H:%M:%S",)
    logger = logging.getLogger()
    logger.info('Initialization Completed')

    EXPECTED_FILE_PATH = "./data/sample_1.png.hocr"
    if os.path.exists(EXPECTED_FILE_PATH):
        os.remove(EXPECTED_FILE_PATH)

    CONFIG_PARAMS_DICT = {
        "tesseract": {
            "pytesseract_path": os.environ['TESSERACT_PATH']
        }
    }
    output_path = './data'

    tesseract_ocr_provider = TesseractOcrDataServiceProvider(
        config_params_dict=CONFIG_PARAMS_DICT,
        logger=logger,
        output_dir=output_path
    )

    ocr_generator_obj = OcrGenerator(
        data_service_provider=tesseract_ocr_provider)
    img_file_path = './data/sample_1.png'

    ocr_result_list = ocr_generator_obj.generate(
        doc_data_list=[{'doc_path': img_file_path, 'pages': '1'}]
    )

    assert os.path.exists(ocr_result_list[0]['output_doc'])
    assert ocr_result_list[0]['output_doc'] == EXPECTED_FILE_PATH


def test_normal_match_bbox_tesct_ocr_gen_1():
    """Test method"""
    # test_normal_match_bbox_tesct.py, test_ocr_parser_bbox_tesct.py,
    # test_ocr_parser_tesct_tokens.py used sample
    img_file_path = './data/sample_1.png'
    psm_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]
    CONFIG_PARAMS_DICT = {
        "tesseract": {
            "pytesseract_path": os.environ['TESSERACT_PATH']
        }
    }
    CONFIG_PARAMS_DICT_TEMP = copy.deepcopy(CONFIG_PARAMS_DICT)
    for i in psm_list:
        try:
            CONFIG_PARAMS_DICT_TEMP["psm"] = i
            tesseract_ocr_provider_tp = TesseractOcrDataServiceProvider(
                config_params_dict=CONFIG_PARAMS_DICT,
                output_dir=TestUtil.create_dirs_if_absent(
                    CONTAINER_ROOT_PATH + "/psm_batch" + str(i))
            )
            ocr_generator_obj_tp = OcrGenerator(
                data_service_provider=tesseract_ocr_provider_tp)

            ocr_result_list = ocr_generator_obj_tp.generate(
                doc_data_list=[{'doc_path': img_file_path, 'pages': '1'}])

            assert os.path.exists(ocr_result_list[0]['output_doc'])
        except Exception as e:
            print(e)


def test_ocr_parser_bbox_tesct_aod_ocr_gen_1():
    """Test method"""
    img_file_path = './data/sample_1.png'
    CONFIG_PARAMS_DICT = {
        "tesseract": {
            "pytesseract_path": os.environ['TESSERACT_PATH']
        }
    }
    tesseract_ocr_provider = TesseractOcrDataServiceProvider(
        config_params_dict=CONFIG_PARAMS_DICT,
        output_dir=TestUtil.create_dirs_if_absent(
            CONTAINER_ROOT_PATH+"/psm3")
    )
    ocr_generator_obj = OcrGenerator(
        data_service_provider=tesseract_ocr_provider)
    doc_data_list = []
    for doc_path in glob.glob(img_file_path):
        doc_data_list.append(
            {'doc_path': doc_path, 'pages': '1'})

    ocr_result_list = ocr_generator_obj.generate(
        doc_data_list=doc_data_list
    )

    assert os.path.exists(ocr_result_list[0]['output_doc'])


def test_tesseract_not_found_error():
    """Test method"""
    try:
        CONFIG_PARAMS_DICT = {
            "tesseract": {
                "pytesseract_path": " "
            }
        }
        output_path = './data'
        TesseractOcrDataServiceProvider(
            config_params_dict=CONFIG_PARAMS_DICT,
            output_dir=output_path
        )

    except Exception as ex:
        assert ex.__class__.__name__ == 'TesseractNotFoundError'
        assert str(ex) == "  is not installed or it's not in your path"

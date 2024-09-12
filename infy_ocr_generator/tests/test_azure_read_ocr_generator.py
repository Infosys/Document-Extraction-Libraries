# ===============================================================================================================#
# Copyright 2021 Infosys Ltd.                                                                                   #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import os
import time
import pytest
from infy_ocr_generator.ocr_generator import OcrGenerator
from infy_ocr_generator.providers.azure_read_ocr_data_service_provider import \
    AzureReadOcrDataServiceProvider
from .test_util import TestUtil

# Create inside temp folder for the purpose of unit testing
CONTAINER_ROOT_PATH = f"C:/temp/unittest/infy_ocr_generator/{__name__}/CONTAINER"

CONFIG_PARAMS_DICT = {
    'azure': {
        'computer_vision': {
            'subscription_key': os.environ['AZURE_CV_SECRET_KEY'],
            'api_read': {
                'url': os.environ['AZURE_CV_SERVER_URL'] + '/vision/v3.2/read/analyze',
            }
        }
    }
}


@pytest.fixture(scope='module', autouse=True)
def pre_test(create_root_folders):
    """Initialization method"""
    create_root_folders([CONTAINER_ROOT_PATH])
    yield  # Run all test methods
    # Post run cleanup


def test_azure_read_ocr_generator():
    """AZURE OCR test method"""
    image_file_path = os.path.abspath('./data/sample_1.png')
    EXPECTED_FILE_PATH = image_file_path + '_azure_read.json'
    if os.path.exists(EXPECTED_FILE_PATH):
        os.remove(EXPECTED_FILE_PATH)
    doc_data_list = [{"doc_path": image_file_path, "pages": "1"}]

    azure_read_provider_obj = AzureReadOcrDataServiceProvider(
        config_params_dict=CONFIG_PARAMS_DICT
    )
    ocr_generator_obj = OcrGenerator(
        data_service_provider=azure_read_provider_obj)

    submit_req_result = ocr_generator_obj.submit_request(doc_data_list)
    time.sleep(6)
    re_res_result = ocr_generator_obj.receive_response(
        submit_req_result)
    ocr_result_list = ocr_generator_obj.generate(
        api_response_list=re_res_result
    )

    assert os.path.exists(ocr_result_list[0]['output_doc'])
    assert os.path.exists(EXPECTED_FILE_PATH)


def test_ocr_parser_azure_read_2():
    """AZURE OCR test method"""
    DATA_ROOT_PATH = f"{CONTAINER_ROOT_PATH}/test2"
    TestUtil.create_dirs_if_absent(DATA_ROOT_PATH)
    pdf_file_path = os.path.abspath('./data/sample/swnlp.pdf')
    doc_data_list = [{"doc_path": pdf_file_path, "pages": "1-2"}]
    azure_read_provider_obj = AzureReadOcrDataServiceProvider(
        config_params_dict=CONFIG_PARAMS_DICT,
        output_to_supporting_folder=True,
        output_dir=DATA_ROOT_PATH
    )
    ocr_generator_obj = OcrGenerator(
        data_service_provider=azure_read_provider_obj)
    submit_req_result = ocr_generator_obj.submit_request(doc_data_list)
    time.sleep(6)
    re_res_result = ocr_generator_obj.receive_response(submit_req_result)
    ocr_result_list = ocr_generator_obj.generate(
        api_response_list=re_res_result
    )
    assert len(ocr_result_list) == 1


def test_ocr_parser_azure_read_3():
    """AZURE OCR test method"""
    DATA_ROOT_PATH = f"{CONTAINER_ROOT_PATH}/test3"
    TestUtil.create_dirs_if_absent(DATA_ROOT_PATH)
    pdf_file_path = os.path.abspath('./data/sample/swnlp.pdf')
    azure_read_provider_obj = AzureReadOcrDataServiceProvider(
        config_params_dict=CONFIG_PARAMS_DICT,
        output_dir=DATA_ROOT_PATH,
        output_to_supporting_folder=True
    )
    ocr_generator_obj_tmp = OcrGenerator(
        data_service_provider=azure_read_provider_obj)

    doc_data_list = [{"doc_path": pdf_file_path, "pages": "1"}]

    submit_req_result = ocr_generator_obj_tmp.submit_request(doc_data_list)
    time.sleep(6)
    re_res_result = ocr_generator_obj_tmp.receive_response(
        submit_req_result, rerun_unsucceeded_mode=True)
    ocr_result_list = ocr_generator_obj_tmp.generate(
        api_response_list=re_res_result
    )
    assert len(ocr_result_list) == 1


def test_ocr_parser_azure_read_4():
    """AZURE OCR test method"""
    azure_read_provider_obj = AzureReadOcrDataServiceProvider(
        config_params_dict=CONFIG_PARAMS_DICT,
        output_to_supporting_folder=True, output_dir=CONTAINER_ROOT_PATH)
    ocr_generator_obj = OcrGenerator(
        data_service_provider=azure_read_provider_obj)

    pdf_file_path = os.path.abspath('./data/sample/swnlp.pdf')
    doc_data_list = [{"doc_path": pdf_file_path, "pages": "1-2"}]
    submit_req_result = ocr_generator_obj.submit_request(doc_data_list)
    time.sleep(6)
    re_res_result = ocr_generator_obj.receive_response(
        submit_req_result, rerun_unsucceeded_mode=True)

    ocr_result_list = ocr_generator_obj.generate(
        api_response_list=re_res_result
    )
    assert len(ocr_result_list) == 1

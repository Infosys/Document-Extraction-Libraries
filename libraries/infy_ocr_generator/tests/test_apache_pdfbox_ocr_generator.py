# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import os
import pytest
from infy_ocr_generator.ocr_generator import OcrGenerator
from infy_ocr_generator.providers.apache_pdfbox_data_service_provider import ApachePdfboxDataServiceProvider
from .test_util import TestUtil

# Create inside temp folder for the purpose of unit testing
CONTAINER_ROOT_PATH = f"C:/temp/unittest/infy_ocr_generator/{__name__}/CONTAINER"

CONFIG_PARAMS_DICT = {
    "format_converter": {
        "format_converter_path": "C:/MyProgramFiles/InfyFormatConverter"
    }
}


@pytest.fixture(scope='module', autouse=True)
def pre_test(create_root_folders, copy_files_to_root_folder):
    """Initialization method"""
    create_root_folders([CONTAINER_ROOT_PATH])
    # Copy files to pick up folder
    SAMPLE_ROOT_PATH = "./data/sample"
    BASELINE_ROOT_PATH = "./data/baseline"
    FILES_TO_COPY = [
        # -- test1 -- #
        ['swnlp.pdf', f"{SAMPLE_ROOT_PATH}",
            f"{CONTAINER_ROOT_PATH}/test1"],
        ['*', f"{BASELINE_ROOT_PATH}/test1",
            f"{CONTAINER_ROOT_PATH}/test1"],
        # -- test2 -- #
        ['swnlp.pdf', f"{SAMPLE_ROOT_PATH}",
            f"{CONTAINER_ROOT_PATH}/test2"],
        ['*', f"{BASELINE_ROOT_PATH}/test2",
            f"{CONTAINER_ROOT_PATH}/test2"],
        # -- test3 -- #
        ['swnlp.pdf', f"{SAMPLE_ROOT_PATH}",
            f"{CONTAINER_ROOT_PATH}/test3"],
        ['1.jpg', f"{SAMPLE_ROOT_PATH}",
            f"{CONTAINER_ROOT_PATH}/test3"],
        ['*', f"{BASELINE_ROOT_PATH}/test3",
            f"{CONTAINER_ROOT_PATH}/test3"],
        # -- test4 -- #
        ['swnlp.pdf', f"{SAMPLE_ROOT_PATH}",
            f"{CONTAINER_ROOT_PATH}/test4"],
        ['2.jpg', f"{SAMPLE_ROOT_PATH}",
            f"{CONTAINER_ROOT_PATH}/test5"],
        ['*', f"{BASELINE_ROOT_PATH}/test4",
            f"{CONTAINER_ROOT_PATH}/test4"],
        # -- test5 -- #
        ['swnlp.pdf', f"{SAMPLE_ROOT_PATH}",
            f"{CONTAINER_ROOT_PATH}/test5"],
        ['2.jpg', f"{SAMPLE_ROOT_PATH}",
            f"{CONTAINER_ROOT_PATH}/test5"],
        ['*', f"{BASELINE_ROOT_PATH}/test5",
            f"{CONTAINER_ROOT_PATH}/test5"],
    ]
    copy_files_to_root_folder(FILES_TO_COPY)
    yield  # Run all test methods
    # Post run cleanup


pdfbox_ocr_provider = ApachePdfboxDataServiceProvider(
    config_params_dict=CONFIG_PARAMS_DICT)
ocr_generator_obj = OcrGenerator(
    data_service_provider=pdfbox_ocr_provider)

# Private methods


def __validate_generated_ocr_files(ocr_file_path_list: list):
    BASELINE_SUFFIX_JSON = "_baseline.json"
    for i, _ in enumerate(ocr_file_path_list):
        ocr_file_path = ocr_file_path_list[i]['output_doc']
        assert os.path.exists(ocr_file_path)
        baseline_file_path = ocr_file_path + BASELINE_SUFFIX_JSON
        error_message = f"Generated file {ocr_file_path} not matching with {baseline_file_path}"
        assert TestUtil.compare_json_file(
            ocr_file_path, baseline_file_path), error_message


def test_pdfbox_sop_pdf_doc():
    """Test method 1"""
    DATA_ROOT_PATH = f"{CONTAINER_ROOT_PATH}/test1"

    pdf_doc_file_path = f"{DATA_ROOT_PATH}/swnlp.pdf"
    doc_data_list = [{'doc_path': pdf_doc_file_path}]
    ocr_list = ocr_generator_obj.generate(doc_data_list=doc_data_list)

    __validate_generated_ocr_files(ocr_list)


def test_pdfbox_with_page():
    """Test method 2"""
    DATA_ROOT_PATH = f"{CONTAINER_ROOT_PATH}/test2"

    pdf_doc_file_path = f"{DATA_ROOT_PATH}/swnlp.pdf"
    doc_data_list = [{'doc_path': pdf_doc_file_path, 'pages': '1'}]
    ocr_list = ocr_generator_obj.generate(doc_data_list=doc_data_list)

    __validate_generated_ocr_files(ocr_list)

    page_data_dict = TestUtil.load_json(ocr_list[0]['output_doc'])[0]
    assert page_data_dict.get('page') == 1


def test_pdfbox_with_individual_ocr_1():
    """Test method 3"""
    DATA_ROOT_PATH = f"{CONTAINER_ROOT_PATH}/test3"

    pdf_doc_file_path = f"{DATA_ROOT_PATH}/swnlp.pdf"
    doc_data_list = [{'doc_path': pdf_doc_file_path}]
    ocr_list = ocr_generator_obj.generate(doc_data_list=doc_data_list)

    __validate_generated_ocr_files(ocr_list)

    ocr_file_path = ocr_list[0]['output_doc']
    RESCALE_DATA = {
        'doc_page_num': '1',
        'doc_page_width': 0,
        'doc_page_height': 0,
        'doc_file_path': fr'{DATA_ROOT_PATH}/1.jpg',
        'doc_file_extension': 'jpg'
    }

    page_ocr_list = pdfbox_ocr_provider.rescale_dimension(
        ocr_file_path, [RESCALE_DATA])

    __validate_generated_ocr_files(page_ocr_list)
    assert os.path.basename(
        page_ocr_list[0]['output_doc']) == "1.jpg_pdfbox.json"


def test_pdfbox_with_individual_ocr_2():
    """Test method 4"""
    DATA_ROOT_PATH = f"{CONTAINER_ROOT_PATH}/test4"

    pdf_doc_file_path = f"{DATA_ROOT_PATH}/swnlp.pdf"
    doc_data_list = [{'doc_path': pdf_doc_file_path}]
    ocr_list = ocr_generator_obj.generate(doc_data_list=doc_data_list)

    __validate_generated_ocr_files(ocr_list)

    ocr_file_path = ocr_list[0]['output_doc']
    RESCALE_DATA = {
        'doc_page_num': '2',
        'doc_page_width': 2550,
        'doc_page_height': 3299,
        'doc_file_path': '',
        'doc_file_extension': 'jpg'
    }

    page_ocr_list = pdfbox_ocr_provider.rescale_dimension(
        ocr_file_path, [RESCALE_DATA])

    __validate_generated_ocr_files(page_ocr_list)
    assert os.path.basename(
        page_ocr_list[0]['output_doc']) == "2.jpg_pdfbox.json"


def test_pdfbox_with_individual_ocr_3():
    """Test method 5
    output file name should according to the doc_page_num and doc_file_path extension
    """
    DATA_ROOT_PATH = f"{CONTAINER_ROOT_PATH}/test5"

    pdf_doc_file_path = f"{DATA_ROOT_PATH}/swnlp.pdf"
    doc_data_list = [{'doc_path': pdf_doc_file_path}]
    ocr_list = ocr_generator_obj.generate(doc_data_list=doc_data_list)

    __validate_generated_ocr_files(ocr_list)

    ocr_file_path = ocr_list[0]['output_doc']
    RESCALE_DATA = {
        'doc_page_num': '5',
        'doc_page_width': 0,
        'doc_page_height': 0,
        'doc_file_path': fr'{DATA_ROOT_PATH}/2.jpg',
        'doc_file_extension': 'jpg'
    }
    page_ocr_list = pdfbox_ocr_provider.rescale_dimension(
        ocr_file_path, [RESCALE_DATA])

    __validate_generated_ocr_files(page_ocr_list)
    assert os.path.basename(
        page_ocr_list[0]['output_doc']) == "5.jpg_pdfbox.json"


def test_pdfbox_with_individual_ocr_4():
    """Test method 6
    rescaled bbox
    """
    DATA_ROOT_PATH = f"{CONTAINER_ROOT_PATH}/test5"

    pdf_doc_file_path = f"{DATA_ROOT_PATH}/swnlp.pdf"
    doc_data_list = [{'doc_path': pdf_doc_file_path}]
    ocr_list = ocr_generator_obj.generate(doc_data_list=doc_data_list)

    __validate_generated_ocr_files(ocr_list)

    ocr_file_path = ocr_list[0]['output_doc']
    RESCALE_DATA = {
        'doc_page_num': '5',
        'doc_page_width': 0,
        'doc_page_height': 0,
        'doc_file_path': fr'{DATA_ROOT_PATH}/2.jpg',
        'doc_file_extension': 'jpg'
    }
    page_ocr_list = pdfbox_ocr_provider.rescale_dimension(
        ocr_file_path, [RESCALE_DATA])

    __validate_generated_ocr_files(page_ocr_list)

    updated_bbox = TestUtil.load_json(
        page_ocr_list[0]['output_doc']).get('tokens')[0].get('bbox')
    assert updated_bbox == [300, 296, 1000, 318]

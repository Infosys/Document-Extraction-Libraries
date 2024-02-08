# ===============================================================================================================#
# Copyright 2021 Infosys Ltd.
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at
# http://www.apache.org/licenses/
# ===============================================================================================================#

import os
import pytest
import logging
## Note: Please install infy_ocr_parser==0.0.10 manually ##
from infy_ocr_parser import ocr_parser
from infy_ocr_parser.providers.tesseract_ocr_data_service_provider import TesseractOcrDataServiceProvider

from infy_field_extractor import checkbox_extractor
from infy_field_extractor.providers.ocr_data_service_provider import OcrDataServiceProvider


def __create_new_instance():
    if not os.path.exists("./logs"):
        os.makedirs("./logs")
    logging.basicConfig(
        filename=("./logs" + "/app_log.log"),
        format="%(asctime)s- %(levelname)s- %(message)s",
        level=logging.INFO,
        datefmt="%d-%b-%y %H:%M:%S",
    )
    logger = logging.getLogger()
    temp_folderpath = os.path.abspath('./data/temp')
    if not os.path.exists(temp_folderpath):
        os.makedirs(temp_folderpath)
    hocr_file = './data/sample_1.png.hocr'
    ocr_parser_object = ocr_parser.OcrParser(
        [hocr_file], TesseractOcrDataServiceProvider())
    provider = OcrDataServiceProvider(ocr_parser_object)
    checkbox_obj = checkbox_extractor.CheckboxExtractor(
        provider, provider, temp_folderpath, logger=logger)
    return checkbox_obj


def test_checkbox_extract_all_fields():
    """test method"""
    checkbox_obj = __create_new_instance()
    img_file_path = os.path.abspath(
        './data/sample_1.png')

    result = checkbox_obj.extract_all_fields(
        img_file_path)

    assert result['fields'] == {'Sub-6': False,
                                'Sub-5': True, 'Sub-4': True, 'Sub-7': False}


def test_checkbox_extract_from_key():
    """test method"""
    checkbox_obj = __create_new_instance()
    img_file_path = os.path.abspath(
        './data/sample_1.png')
    checkbox_field_data_list = [
        {"field_key": ["Sub-4"], "field_state_pos": "left"},
        {"field_key": ["Sub-6"]}]

    result = checkbox_obj.extract_custom_fields(
        img_file_path,
        checkbox_field_data_list
    )

    assert result['fields'] == [
        {'field_key': ['Sub-4'], 'field_state': True, 'error': None},
        {'field_key': ['Sub-6'], 'field_state': False, 'error': None}]


def test_checkbox_extract_custom_from_bbox():
    """test method"""
    checkbox_obj = __create_new_instance()
    img_file_path = os.path.abspath(
        './data/sample_1.png')
    # Use ocr_parser library for getting "field_state_bbox"
    checkbox_field_data_list = [
        {"field_key": ["Sub-4"], "field_state_bbox": [433, 1533, 229, 177]}]

    result = checkbox_obj.extract_custom_fields(
        img_file_path, checkbox_field_data_list)

    assert result['fields'][0]['field_state'] is True


def test_checkbox_extractor_exception_imagepath():
    """test method"""
    checkbox_obj = __create_new_instance()
    with pytest.raises(Exception, match="property imagepath not found"):
        checkbox_obj.extract_all_fields(
            '')


def test_checkbox_extractor_exception_tempfolderpath():
    """test method"""
    with pytest.raises(Exception, match="property temp_folderpath not found"):
        checkbox_extractor.CheckboxExtractor(
            None, None, ' ')

# ===============================================================================================================#
# Copyright 2021 Infosys Ltd.                                                                                   #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#


import os
import pytest
## Note: Please install infy_ocr_parser==0.0.10 manually ##
from infy_ocr_parser import ocr_parser
from infy_ocr_parser.providers.tesseract_ocr_data_service_provider import TesseractOcrDataServiceProvider

from infy_field_extractor import text_extractor
from infy_field_extractor.providers.ocr_data_service_provider import OcrDataServiceProvider


def __create_new_instance():
    temp_folderpath = os.path.abspath('./data/temp/')
    hocr_file_1 = './data/sample_1.png.hocr'
    ocr_parser_object = ocr_parser.OcrParser(
        [hocr_file_1], TesseractOcrDataServiceProvider())
    provider = OcrDataServiceProvider(ocr_parser_object)
    text_object = text_extractor.TextExtractor(
        provider, provider, temp_folderpath)
    return text_object


def test_text_extract_all_fields():
    """test method"""
    text_object = __create_new_instance()
    img_file_path = os.path.abspath(
        './data/sample_1.png')

    result = text_object.extract_all_fields(
        img_file_path,
        config_params_dict={"within_bbox": [185, 437, 2873, 585]})

    assert result['fields'] == {'FULL NAME:': 'JOHN DOE', 'GRADE:': 'VIII'}


def test_extract_from_keys():
    """test method"""
    text_object = __create_new_instance()
    img_file_path = os.path.abspath(
        './data/sample_1.png')
    field_data_list = [
        {"field_key": ["FULL NAME:"], "field_value_pos":"right"},
        {"field_key": ["GRADE:$"], "field_value_pos":"right",
         "field_key_match": {"method": "regex"}}]

    result = text_object.extract_custom_fields(
        img_file_path, field_data_list)

    assert result['fields'] == [
        {'field_key': ['FULL NAME:'],
         'field_value': 'JOHN DOE',
         'field_value_confidence_pct': 95.5,
         'error': None},
        {'field_key': ['GRADE:$'],
         'field_value': 'VIII',
         'field_value_confidence_pct': 55.0,
         'error': None}]


def test_extract_from_field_value_bboxes():
    """test method"""
    text_object = __create_new_instance()
    img_file_path = os.path.abspath(
        './data/sample_1.png')
    # Use ocr_parser library for getting "field_state_bbox"
    field_data_list = [
        {"field_key": ["FULL NAME"],
         "field_value_bbox": [890, 530, 1249, 169]},
        {"field_key": ["GRADE"],
         "field_value_bbox":[715, 800, 737, 169]}]

    result = text_object.extract_custom_fields(
        img_file_path, field_data_list)

    assert result['fields'] == [
        {'field_key': ['FULL NAME'], 'field_value_bbox': [890, 530, 1249, 169],
         'field_value': 'JOHN DOE', 'field_value_confidence_pct': 95.5},
        {'field_key': ['GRADE'], 'field_value_bbox': [715, 800, 737, 169],
         'field_value': 'VIII', 'field_value_confidence_pct': 55.0}]


def test_text_extractor_exception_imagepath():
    """test method"""
    text_object = __create_new_instance()
    with pytest.raises(Exception, match="property imagepath not found"):
        text_object.extract_all_fields(
            '')


def test_text_extractor_exception_tempfolderpath():
    """test method"""
    with pytest.raises(Exception, match="property temp_folderpath not found"):
        text_extractor.TextExtractor(
            None, None, ' ')

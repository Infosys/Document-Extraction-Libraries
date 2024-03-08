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

from infy_field_extractor import radio_button_extractor
from infy_field_extractor.providers.ocr_data_service_provider import OcrDataServiceProvider


def __create_new_instance():
    temp_folderpath = os.path.abspath('./data/temp/')
    hocr_file = './data/sample_1.png.hocr'
    ocr_parser_object = ocr_parser.OcrParser(
        [hocr_file], TesseractOcrDataServiceProvider())
    provider = OcrDataServiceProvider(ocr_parser_object)
    radiobutton_obj = radio_button_extractor.RadioButtonExtractor(
        provider, provider, temp_folderpath)
    return radiobutton_obj


def test_radiobutton_extract_all_fields():
    """test method"""
    radiobutton_obj = __create_new_instance()
    img_file_path = os.path.abspath(
        './data/sample_1.png')
    template_checked_folder = './data/radio_button_sample/template/checked'
    template_unchecked_folder = './data/radio_button_sample/template/unchecked'
    config_params_dict = {'template_checked_folder': template_checked_folder,
                          'template_unchecked_folder': template_unchecked_folder,
                          }

    result = radiobutton_obj.extract_all_fields(
        img_file_path, config_params_dict)

    assert result['fields'] == {'Male': True, 'Female': False}


def test_radiobutton_extract_custom_from_keys():
    """test method"""
    radiobutton_obj = __create_new_instance()
    img_file_path = os.path.abspath(
        './data/sample_1.png')
    radiobutton_field_data_list = [
        {"field_key": ["Male"], "field_state_pos": "left"},
        {"field_key": ["Female"], "field_state_pos": "left"}]

    result = radiobutton_obj.extract_custom_fields(
        img_file_path,
        radiobutton_field_data_list)

    assert result['fields'] == [{'field_key': ['Male'], 'field_state': True, 'error': None},
                                {'field_key': ['Female'], 'field_state': False, 'error': None}]


def test_radiobutton_extract_custom_from_bbox():
    """test method"""
    radiobutton_obj = __create_new_instance()
    img_file_path = os.path.abspath(
        './data/sample_1.png')
    # Use ocr_parser library for getting "field_state_bbox"
    radiobutton_field_data_list = [
        {"field_key": ["Male"], "field_state_bbox": [410, 1053, 171, 171]},
        {"field_key": ["Female"], "field_state_bbox": [945, 1065, 171, 149]}]

    result = radiobutton_obj.extract_custom_fields(
        img_file_path, radiobutton_field_data_list)

    assert result['fields'] == [
        {'field_key': ['Male'], 'field_state_bbox': [
            410, 1053, 171, 171], 'field_state': False, 'error': None},
        {'field_key': ['Female'], 'field_state_bbox': [
            945, 1065, 171, 149], 'field_state': True, 'error': None}]


def test_radiobutton_extractor_exception_tempfolderpath():
    """test method"""
    with pytest.raises(Exception, match="property temp_folderpath not found"):
        radio_button_extractor.RadioButtonExtractor(
            None, None, ' ')

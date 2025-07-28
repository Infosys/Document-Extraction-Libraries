# ===============================================================================================================#
# Copyright 2020 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import os
import glob
import pytest
import imageio
import tests.internal.test_helper as thelp
from infy_ocr_parser import ocr_parser
from infy_ocr_parser.providers.tesseract_ocr_data_service_provider import TesseractOcrDataServiceProvider

INFY_SP_ROOT_PATH = os.environ['INFY_SP_ROOT_PATH']
UNIT_TEST_DATA_LOCATION = INFY_SP_ROOT_PATH + \
    "\\workbenchlibraries - Documents\\SHARED_DATA\\unit_test_data"
img_file_path = UNIT_TEST_DATA_LOCATION + \
    "\\ocr_parser\\Assa Abloy America_19052015240693\\2.jpg"
ocr_doc_list_psm3 = glob.glob(
    UNIT_TEST_DATA_LOCATION +
    "\\ocr_parser\\Assa Abloy America_19052015240693\\2.jpg.hocr")

img = imageio.imread(img_file_path)

tesseract_ocr_data_obj = TesseractOcrDataServiceProvider()


def test_get_phrase_token_1():
    """test method"""
    ocr_obj = ocr_parser.OcrParser(
        ocr_doc_list_psm3, data_service_provider=tesseract_ocr_data_obj)
    phrase_tokens_1 = ocr_obj.get_tokens_from_ocr(
        token_type_value=3)
    phrase_tokens_2 = ocr_obj.get_tokens_from_ocr(
        token_type_value=3, max_word_space='1.0t')
    phrase_tokens_3 = ocr_obj.get_tokens_from_ocr(
        token_type_value=3, max_word_space='1.25t')
    phrase_tokens_4 = ocr_obj.get_tokens_from_ocr(
        token_type_value=3, max_word_space='2.0t')
    # Verify one item from list
    # max_word_space = '1.5t'
    assert phrase_tokens_1[11]['text'] == 'See Certificate Number:'
    # max_word_space = '1.0t'
    assert phrase_tokens_2[11]['text'] == 'See'
    # max_word_space = '1.25t'
    assert phrase_tokens_3[11]['text'] == 'See Certificate Number:'
    # max_word_space = '2.0t'
    assert phrase_tokens_4[11]['text'] == 'See Certificate Number: 570076315049'


def test_get_bbox_for_1():
    """test method"""
    ocr_obj = ocr_parser.OcrParser(ocr_doc_list_psm3, data_service_provider=tesseract_ocr_data_obj,
                                   config_params_dict={
                                       'match_method': 'regex', 'similarity_score': 1})
    # "maxWordSpace": '1.5t'
    reg_def_dict_list = [
        {"anchorText": ["See Certificate Number:"]}]
    ap_bbox, error = thelp.get_bbox_for(
        reg_def_dict_list, ocr_obj, img.copy())
    assert ap_bbox[0][0]['bbox'] == [162, 381, 450, 27]

    # "maxWordSpace": '1.25t'
    reg_def_dict_list = [{"anchorText": [
        "See Certificate Number: 570076315049"], "anchorTextMatch": {"maxWordSpace": '1.25t'}}]
    ap_bbox, error = thelp.get_bbox_for(
        reg_def_dict_list, ocr_obj, img.copy())
    assert error == 'Key: See Certificate Number: 570076315049 not found'

    # "maxWordSpace": '1.5%' of page width
    reg_def_dict_list = [
        {"anchorText": ["See Certificate Number: 570076315049"], "anchorTextMatch": {"maxWordSpace": '1.5%'}}]
    ap_bbox, error = thelp.get_bbox_for(
        reg_def_dict_list, ocr_obj, img.copy())
    print(ap_bbox)
    assert ap_bbox[0][0]['bbox'] == [162, 471, 719, 27]


def test_get_bbox_for_2():
    ocr_obj = ocr_parser.OcrParser(ocr_doc_list_psm3, data_service_provider=tesseract_ocr_data_obj,
                                   config_params_dict={
                                       'match_method': 'regex', 'similarity_score': 1})
    # "maxWordSpace": '1.5t'
    reg_def_dict_list = [
        {"anchorText": ["See Certificate Number:"],
            "anchorTextMatch": {"maxWordSpace": '1.5t'}},
        {"anchorText": ["^aon$"],
         "anchorTextMatch": {
            "method": "regex",
            "similarityScore": 1
        }}]
    ap_bbox, error = thelp.get_bbox_for(
        reg_def_dict_list, ocr_obj, img.copy())
    assert error == 'Key: ^aon$ not found'

    reg_def_dict_list = [
        {"anchorText": ["See Certificate Number:"],
            "anchorTextMatch": {"maxWordSpace": '1.5t'}},
        {"anchorText": ["^aon$"],
         "anchorTextMatch": {
            "method": "regex",
            "similarityScore": 1,
            "maxWordSpace": '1.0t'
        }}]
    ap_bbox, error = thelp.get_bbox_for(
        reg_def_dict_list, ocr_obj, img.copy())
    assert ap_bbox[0][0]['bbox'] == [160, 302, 2, 79]


def test_max_word_space_units():
    """test method"""
    ocr_obj = ocr_parser.OcrParser(
        ocr_doc_list_psm3, data_service_provider=tesseract_ocr_data_obj)
    phrase_tokens_1 = ocr_obj.get_tokens_from_ocr(
        token_type_value=3, max_word_space=30)
    phrase_tokens_2 = ocr_obj.get_tokens_from_ocr(
        token_type_value=3, max_word_space='30')
    phrase_tokens_3 = ocr_obj.get_tokens_from_ocr(
        token_type_value=3, max_word_space='30px')
    phrase_tokens_4 = ocr_obj.get_tokens_from_ocr(
        token_type_value=3, max_word_space='2.0%')
    phrase_tokens_5 = ocr_obj.get_tokens_from_ocr(
        token_type_value=3, max_word_space='2.0t')
    # Verify one item from list
    # max_word_space = 30
    assert phrase_tokens_1[11]['text'] == 'See Certificate Number:'
    # max_word_space = '30'
    assert phrase_tokens_2[11]['text'] == 'See Certificate Number:'
    # max_word_space = '30px'
    assert phrase_tokens_3[11]['text'] == 'See Certificate Number:'
    # max_word_space = '2.0%'
    assert phrase_tokens_4[11]['text'] == 'See Certificate Number: 570076315049'
    # max_word_space = '2.0t'
    assert phrase_tokens_5[11]['text'] == 'See Certificate Number: 570076315049'


def test_no_unhandled_error_when_empty_hocr_file():
    """test method"""
    file_path = f"{UNIT_TEST_DATA_LOCATION}\\ocr_parser\\general\\empty.hocr"

    ocr_obj = ocr_parser.OcrParser(
        [file_path], data_service_provider=tesseract_ocr_data_obj)
    phrase_tokens_2 = ocr_obj.get_tokens_from_ocr(
        token_type_value=3, max_word_space='1.0t')
    assert (len(phrase_tokens_2) == 0)

    reg_def_dict_list = [{"anchorText": [
        "Some non existent text"], "anchorTextMatch": {"maxWordSpace": '1.25t'}}]
    _, error = thelp.get_bbox_for(
        reg_def_dict_list, ocr_obj, img.copy())
    assert error == 'Key: Some non existent text not found'

# ===============================================================================================================#
# Copyright 2020 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import os
import glob
import json
import imageio
from infy_ocr_parser import ocr_parser
from infy_ocr_parser.providers.tesseract_ocr_data_service_provider import TesseractOcrDataServiceProvider

INFY_SP_ROOT_PATH = os.environ['INFY_SP_ROOT_PATH']
UNIT_TEST_DATA_LOCATION = INFY_SP_ROOT_PATH + \
    "\\workbenchlibraries - Documents\\SHARED_DATA\\unit_test_data"
img_file_path = UNIT_TEST_DATA_LOCATION + \
    "\\ocr_parser\\Assa Abloy America_19052015240693\\2.jpg"
ocr_doc_list_psm3 = glob.glob(
    UNIT_TEST_DATA_LOCATION+"/ocr_parser/Assa Abloy America_19052015240693/2.jpg.hocr")

img = imageio.imread(img_file_path)
tesseract_ocr_data_obj = TesseractOcrDataServiceProvider()


def test_get_nearby_tokens_phrase_1():
    """test method"""
    ocr_obj = ocr_parser.OcrParser(
        ocr_doc_list_psm3, data_service_provider=tesseract_ocr_data_obj)
    anchor_text = {
        'anchorText': ['See Certificate Number:'],
        'pageNum': [2]
    }
    response = ocr_obj.get_nearby_tokens(
        anchor_text, token_min_alignment_threshold=0.1)
    print(json.dumps(response, indent=4))
    assert response['tokenData'][0]['regions']['top']['regionBbox'] == [
        161,
        347,
        186,
        17
    ]
    assert len(response['tokenData']) == 2
    assert len(response['tokenData'][0]['regions']['top']['tokens']) == 1
    assert len(response['tokenData'][0]['regions']['bottom']['tokens']) == 1
    assert len(response['tokenData'][0]['regions']['right']['tokens']) == 1
    assert len(response['tokenData'][0]['regions']['left']['tokens']) == 0


def test_get_nearby_tokens_phrase_2():
    """test method"""
    ocr_obj = ocr_parser.OcrParser(
        ocr_doc_list_psm3, data_service_provider=tesseract_ocr_data_obj)
    anchor_text = {
        'anchorText': ['See Certificate Number:'],
        'pageNum': [2]
    }
    response = ocr_obj.get_nearby_tokens(
        anchor_text, token_count=2, token_min_alignment_threshold=0.2)
    print(json.dumps(response, indent=4))
    assert response['tokenData'][0]['regions']['top']['regionBbox'] == [
        160,
        297,
        572,
        67
    ]
    assert len(response['tokenData']) == 2
    assert len(response['tokenData'][0]['regions']['top']['tokens']) == 2


def test_get_nearby_tokens_phrase_3():
    """test method"""
    ocr_obj = ocr_parser.OcrParser(
        ocr_doc_list_psm3, data_service_provider=tesseract_ocr_data_obj)
    anchor_text = {
        'anchorText': ['See Certificate Number:'],
        'pageNum': [2]
    }
    response = ocr_obj.get_nearby_tokens(
        anchor_text, token_count=3, token_min_alignment_threshold=0.1)
    # print(json.dumps(response, indent=4))
    assert response['tokenData'][0]['regions']['top']['regionBbox'] == [
        159, 259, 573, 105]
    assert len(response['tokenData']) == 2
    assert len(response['tokenData'][0]['regions']['top']['tokens']) == 3


def test_get_nearby_tokens_word_1():
    """test method"""
    ocr_obj = ocr_parser.OcrParser(
        ocr_doc_list_psm3, data_service_provider=tesseract_ocr_data_obj)
    anchor_text = {
        'anchorText': ['form'],
        'pageNum': [2]
    }
    response = ocr_obj.get_nearby_tokens(anchor_text, token_type_value=1)
    print(json.dumps(response, indent=4))
    assert len(response['tokenData']) == 3
    assert response['tokenData'][0]['regions']['top']['regionBbox'] == [
        647,
        473,
        234,
        25
    ]
    assert len(response['tokenData'][0]['regions']['top']['tokens']) == 1


def test_get_nearby_tokens_word_2():
    """test method"""
    ocr_obj = ocr_parser.OcrParser(
        ocr_doc_list_psm3, data_service_provider=tesseract_ocr_data_obj)
    anchor_text = {
        'anchorText': ['form'],
        'pageNum': [2]
    }
    response = ocr_obj.get_nearby_tokens(
        anchor_text, token_type_value=1, token_count=2)
    print(json.dumps(response, indent=4))
    assert len(response['tokenData']) == 3
    assert response['tokenData'][0]['regions']['top']['regionBbox'] == [
        647,
        379,
        240,
        119
    ]
    assert len(response['tokenData'][0]['regions']['top']['tokens']) == 2


def test_get_nearby_tokens_line_1():
    """test method"""
    ocr_obj = ocr_parser.OcrParser(
        ocr_doc_list_psm3, data_service_provider=tesseract_ocr_data_obj)
    anchor_text = {
        'anchorText': ['form number:'],
        'pageNum': [2]
    }
    response = ocr_obj.get_nearby_tokens(
        anchor_text, token_type_value=2, token_count=1)
    print(json.dumps(response, indent=4))
    assert response['tokenData'][0]['regions']['top']['regionBbox'] == [
        160,
        591,
        1136,
        30
    ]
    assert len(response['tokenData']) == 1
    assert len(response['tokenData'][0]['regions']['top']['tokens']) == 1


def test_anchor_txt_dict_error():
    ocr_obj = ocr_parser.OcrParser(
        ocr_doc_list_psm3, data_service_provider=tesseract_ocr_data_obj)
    anchor_text = {
        'anchorText': ['form number:'],
        'pageNo': [2]
    }
    response = ocr_obj.get_nearby_tokens(
        anchor_text, token_type_value=2, token_count=1)
    print(json.dumps(response, indent=4))
    assert response['error'] == "Invalid keys found in anchor_txt_dict: ['pageNo']."


def test_token_alignment_1():
    doc_list_psm3 = glob.glob(
        UNIT_TEST_DATA_LOCATION + "/ocr_parser/aon_crop/alignment_0.01.hocr")
    ocr_obj = ocr_parser.OcrParser(
        doc_list_psm3, data_service_provider=tesseract_ocr_data_obj)
    anchor_text = {
        'anchorText': ['po box 83720'],
        'pageNum': [1]
    }
    response = ocr_obj.get_nearby_tokens(
        anchor_text, token_type_value=3, token_count=1, token_min_alignment_threshold=0.3)
    assert len(response['tokenData'][0]['regions']['top']['tokens']) == 0

    response = ocr_obj.get_nearby_tokens(
        anchor_text, token_type_value=3, token_count=1, token_min_alignment_threshold=0.2)
    assert len(response['tokenData'][0]['regions']['top']['tokens']) == 0

    response = ocr_obj.get_nearby_tokens(
        anchor_text, token_type_value=3, token_count=1, token_min_alignment_threshold=0.1)
    assert len(response['tokenData'][0]['regions']['top']['tokens']) == 0

    # the phrase on top of the anchor text is aligned only 1% of the entire anchor text width
    response = ocr_obj.get_nearby_tokens(
        anchor_text, token_type_value=3, token_count=1, token_min_alignment_threshold=0.01)
    print(json.dumps(response, indent=4))
    assert len(response['tokenData'][0]['regions']['top']['tokens']) == 1


def test_token_alignment_2():
    doc_list_psm3 = glob.glob(
        UNIT_TEST_DATA_LOCATION + "/ocr_parser/aon_crop/alignment_0.2.hocr")
    ocr_obj = ocr_parser.OcrParser(
        doc_list_psm3, data_service_provider=tesseract_ocr_data_obj)
    anchor_text = {
        'anchorText': ['po box 83720'],
        'pageNum': [1]
    }
    response = ocr_obj.get_nearby_tokens(
        anchor_text, token_type_value=3, token_count=1, token_min_alignment_threshold=0.3)
    assert len(response['tokenData'][0]['regions']['top']['tokens']) == 0

    # the phrase on top of the anchor text is aligned only 20% of the entire anchor text width
    response = ocr_obj.get_nearby_tokens(
        anchor_text, token_type_value=3, token_count=1, token_min_alignment_threshold=0.2)
    assert len(response['tokenData'][0]['regions']['top']['tokens']) == 1

    # the phrase on top of the anchor text should align 20% or less
    response = ocr_obj.get_nearby_tokens(
        anchor_text, token_type_value=3, token_count=1, token_min_alignment_threshold=0.1)
    assert len(response['tokenData'][0]['regions']['top']['tokens']) == 1


def test_token_alignment_3():
    doc_list_psm3 = glob.glob(
        UNIT_TEST_DATA_LOCATION + "/ocr_parser/aon_crop/alignment_0.9.hocr")
    ocr_obj = ocr_parser.OcrParser(
        doc_list_psm3, data_service_provider=tesseract_ocr_data_obj)
    anchor_text = {
        'anchorText': ['po box 83720'],
        'pageNum': [1]
    }

    # the phrase on top of the anchor text is aligned only 90% or less of the entire anchor text width
    response = ocr_obj.get_nearby_tokens(
        anchor_text, token_type_value=3, token_count=1, token_min_alignment_threshold=0.9)
    assert len(response['tokenData'][0]['regions']['top']['tokens']) == 1

    # the phrase on top of the anchor text is aligned only 90% or less of the entire anchor text width
    response = ocr_obj.get_nearby_tokens(
        anchor_text, token_type_value=3, token_count=1, token_min_alignment_threshold=0.5)
    assert len(response['tokenData'][0]['regions']['top']['tokens']) == 1

    # the phrase on top of the anchor text should align 90% or less so with threshold 1 it does
    # not match as the nearby token is not aligning with 100% of anchor text
    response = ocr_obj.get_nearby_tokens(
        anchor_text, token_type_value=3, token_count=1, token_min_alignment_threshold=1)
    assert len(response['tokenData'][0]['regions']['top']['tokens']) == 0


def test_token_alignment_4():
    doc_list_psm3 = glob.glob(
        UNIT_TEST_DATA_LOCATION + "/ocr_parser/aon_crop/alignment_1.hocr")
    ocr_obj = ocr_parser.OcrParser(
        doc_list_psm3, data_service_provider=tesseract_ocr_data_obj)
    anchor_text = {
        'anchorText': ['po box 83720'],
        'pageNum': [1]
    }

    # the phrase on top of the anchor text is aligned only 100% or less of the entire anchor text width
    response = ocr_obj.get_nearby_tokens(
        anchor_text, token_type_value=3, token_count=1, token_min_alignment_threshold=0.9)
    assert len(response['tokenData'][0]['regions']['top']['tokens']) == 1

    # the phrase on top of the anchor text is aligned only 100% or less of the entire anchor text width
    response = ocr_obj.get_nearby_tokens(
        anchor_text, token_type_value=3, token_count=1, token_min_alignment_threshold=0.5)
    assert len(response['tokenData'][0]['regions']['top']['tokens']) == 1

    # the phrase on top of the anchor text should align 100 %
    response = ocr_obj.get_nearby_tokens(
        anchor_text, token_type_value=3, token_count=1, token_min_alignment_threshold=1)
    assert len(response['tokenData'][0]['regions']['top']['tokens']) == 1


def test_token_alignment_5():
    doc_list_psm3 = glob.glob(
        UNIT_TEST_DATA_LOCATION + "/ocr_parser/aon_crop/alignment_0.hocr")
    ocr_obj = ocr_parser.OcrParser(
        doc_list_psm3, data_service_provider=tesseract_ocr_data_obj)
    anchor_text = {
        'anchorText': ['Boise, ID 83720-0080'],
        'pageNum': [1]
    }

    # the phrase on top of the anchor text has to strictly within the bbox of anchor text
    response = ocr_obj.get_nearby_tokens(
        anchor_text, token_type_value=3, token_count=1, token_min_alignment_threshold=0)
    assert len(response['tokenData'][0]['regions']['top']['tokens']) == 1

    # the phrase on top of the anchor text is aligned only 50% or less of the entire anchor text width
    response = ocr_obj.get_nearby_tokens(
        anchor_text, token_type_value=3, token_count=1, token_min_alignment_threshold=0.5)
    assert len(response['tokenData'][0]['regions']['top']['tokens']) == 1

    # the phrase on top of the anchor text should align 100 %
    response = ocr_obj.get_nearby_tokens(
        anchor_text, token_type_value=3, token_count=1, token_min_alignment_threshold=0.9)
    assert len(response['tokenData'][0]['regions']['top']['tokens']) == 0


def test_token_distance():
    doc_list_psm3 = glob.glob(
        UNIT_TEST_DATA_LOCATION + "/ocr_parser/aon_crop/alignment_0.hocr")
    ocr_obj = ocr_parser.OcrParser(
        doc_list_psm3, data_service_provider=tesseract_ocr_data_obj)
    anchor_text = {
        'anchorText': ['Boise, ID 83720-0080'],
        'pageNum': [1]
    }

    # the nearest token on top of the anchor text can be anywhere above the anchor text
    response = ocr_obj.get_nearby_tokens(
        anchor_text, token_type_value=3, token_count=1, token_min_alignment_threshold=0)
    assert len(response['tokenData'][0]['regions']['top']['tokens']) == 1

    anchor_text = {
        'anchorText': ['Boise, ID 83720-0080'],
        'pageNum': [1],
        'distance': {'top': '10'}
    }
    # the nearest token on top of the anchor text cannot be more than 10 px
    response = ocr_obj.get_nearby_tokens(
        anchor_text, token_type_value=3, token_count=1, token_min_alignment_threshold=0.5)
    assert len(response['tokenData'][0]['regions']['top']['tokens']) == 0

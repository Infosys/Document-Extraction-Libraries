# ===============================================================================================================#
# Copyright 2020 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import glob
import json
from infy_ocr_parser import ocr_parser
from infy_ocr_parser.providers.tesseract_ocr_data_service_provider import TesseractOcrDataServiceProvider
from infy_ocr_parser.providers.azure_ocr_data_service_provider import AzureOcrDataServiceProvider
from infy_ocr_parser.providers.azure_read_ocr_data_service_provider import AzureReadOcrDataServiceProvider

IMAGE_WIDTH = 4185
IMAGE_HEIGHT = 4121


def __create_new_instance():
    ocr_doc_list = glob.glob("./data/sample_1.png.hocr")
    config_params_dict = {'match_method': 'regex', 'similarity_score': 1}
    # Select the required provider
    data_service_provider = TesseractOcrDataServiceProvider()
    # data_service_provider = AzureReadOcrDataServiceProvider()
    # data_service_provider=AzureOcrDataServiceProvider()
    ocr_obj = ocr_parser.OcrParser(
        ocr_doc_list, data_service_provider=data_service_provider,
        config_params_dict=config_params_dict)

    return ocr_obj


def test_get_bbox_for_no_anchor_points():
    """test method"""
    ocr_obj = __create_new_instance()
    reg_def_dict_list = [{"anchorText": ["FULL NAME"]}]
    result = ocr_obj.get_bbox_for(reg_def_dict_list)
    assert __validate_bbox(
        [region['bbox'] for region in result['regions'][0]['regionBBox']]) is True


def test_get_bbox_for_1_anchor_points():
    """test method"""
    ocr_obj = __create_new_instance()
    reg_def_dict_list = [{"anchorText": ["FULL NAME:", "GRADE:"],
                          "anchorPoint1": {"left": None, "top": '-0.2t', "right": 10, "bottom": None}},
                         {"anchorText": ["GENDER:"],
                          "anchorPoint1": {"left": None, "top": '0.2t', "right": '50%', "bottom": None}}]
    result = ocr_obj.get_bbox_for(reg_def_dict_list)
    assert __validate_bbox(
        [region['bbox'] for region in result['regions'][0]['regionBBox']]) is True


def test_get_bbox_for_2_anchor_points():
    """test method"""
    ocr_obj = __create_new_instance()
    reg_def_dict_list = [{"anchorText": ["FULL NAME"],
                          "anchorPoint1": {"left": None, "top": '0.2t', "right": '0.5t', "bottom": None},
                          "anchorPoint2": {"left": None, "top": None, "right": "1.5t", "bottom": "0.3t"}
                          }]
    result = ocr_obj.get_bbox_for(reg_def_dict_list)
    assert __validate_bbox(
        [region['bbox'] for region in result['regions'][0]['regionBBox']]) is True


def test_get_nearby_tokens():
    """test method"""
    ocr_obj = __create_new_instance()
    anchor_text = {'anchorText': ['FULL NAME']}
    response = ocr_obj.get_nearby_tokens(anchor_text)
    print(json.dumps(response, indent=4))
    assert len(response['tokenData'][0]['regions']['top']['tokens']) == 0

    assert len(response['tokenData'][0]['regions']['bottom']['tokens']) == 1
    assert response['tokenData'][0]['regions']['bottom']['tokens'][0]['text'] == "GRADE:"

    assert len(response['tokenData'][0]['regions']['right']['tokens']) == 1
    assert response['tokenData'][0]['regions']['right']['tokens'][0]['text'] == "JOHN DOE"

    assert len(response['tokenData'][0]['regions']['left']['tokens']) == 0


def test_get_tokens():
    """test method"""
    ocr_obj = __create_new_instance()

    word_tokens = ocr_obj.get_tokens_from_ocr(
        token_type_value=1, pages=[1])
    assert isinstance(word_tokens, list)
    assert __validate_bbox([token['bbox'] for token in word_tokens]) is True

    phrase_tokens = ocr_obj.get_tokens_from_ocr(token_type_value=3)
    assert isinstance(phrase_tokens, list)
    assert __validate_bbox([token['bbox'] for token in phrase_tokens]) is True
    assert len(phrase_tokens) > 0

    line_tokens = ocr_obj.get_tokens_from_ocr(token_type_value=2)
    assert isinstance(line_tokens, list)
    assert __validate_bbox([token['bbox'] for token in line_tokens]) is True
    assert len(line_tokens) > 0


def test_save_tokens_as_json():
    """test method"""
    ocr_obj = __create_new_instance()
    res = ocr_obj.save_tokens_as_json(
        "./data/output.json", token_type_value=1)
    assert res["isFileSaved"] is True


def __validate_bbox(bbox_list):

    for bbox in bbox_list:
        if len(bbox) is 4:
            for index, val in enumerate(bbox):
                if val < 0:
                    return False
                if index in [0, 2] and val > IMAGE_WIDTH:
                    return False
                elif index in [1, 3] and val > IMAGE_HEIGHT:
                    return False
        else:
            return False
    return True

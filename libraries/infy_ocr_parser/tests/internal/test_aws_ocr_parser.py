# ===============================================================================================================#
# Copyright 2020 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import os
import json
import glob
import imageio
from infy_ocr_parser.providers.aws_detect_doc_txt_ocr_data_service_provider import AwsDetectDocumentTextDataServiceProvider
from infy_ocr_parser.providers.azure_read_ocr_data_service_provider import AzureReadOcrDataServiceProvider
from infy_ocr_parser.providers.tesseract_ocr_data_service_provider import TesseractOcrDataServiceProvider
from infy_ocr_parser import ocr_parser
import tests.internal.test_helper as thelp
from tests.test_ocr_parser import IMAGE_HEIGHT, IMAGE_WIDTH


IMAGE_WIDTH = 2880
IMAGE_HEIGHT = 2321

INFY_SP_ROOT_PATH = os.environ['INFY_SP_ROOT_PATH']
UNIT_TEST_DATA_LOCATION = INFY_SP_ROOT_PATH + \
    "\\workbenchlibraries - Documents\\SHARED_DATA\\unit_test_data\\ocr_parser"
img_file_path = UNIT_TEST_DATA_LOCATION + "\\aws\\Handwriting Sample 3.png"


def test_aws_with_anchor_text():
    """test aws api with input image"""
    ocr_obj = __create_new_instance()

    reg_def_dict_list = [{"anchorText": [["Employment Application"]]
                          }]
    img = imageio.imread(img_file_path)

    ap_bbox, _ = thelp.get_bbox_for(
        reg_def_dict_list, ocr_obj, img.copy())
    assert ap_bbox == [[{'bbox': [850, 63, 977, 161], 'page': 1, 'confidencePct': 99.94, 'scalingFactor': {
        'external': {'ver': 1.0, 'hor': 1.0}, 'internal': {'ver': 2.321, 'hor': 2.88}}}]]


def test_aws_with_anchor_text_with_synonymns():
    """test aws api with input image"""

    ocr_obj = __create_new_instance()
    img = imageio.imread(img_file_path)

    reg_def_dict_list = [{"anchorText": [["Employment"]]
                          }]
    ap_bbox, _ = thelp.get_bbox_for(
        reg_def_dict_list, ocr_obj, img.copy())
    assert ap_bbox == [[{'bbox': [850, 78, 503, 146], 'page': 1, 'confidencePct': 99.95, 'scalingFactor': {'external': {'ver': 1.0, 'hor': 1.0}, 'internal': {'ver': 2.321, 'hor': 2.88}}}], [
        {'bbox': [1213, 1211, 405, 108], 'page': 1, 'confidencePct': 99.15, 'scalingFactor': {'external': {'ver': 1.0, 'hor': 1.0}, 'internal': {'ver': 2.321, 'hor': 2.88}}}]]


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
    reg_def_dict_list = [{"anchorText": ["FULL NAME:", "PHONE NUMBER:"],
                          "anchorPoint1": {"left": None, "top": '-0.2t', "right": 10, "bottom": None}},
                         {"anchorText": ["HOME ADDRESS:"],
                          "anchorPoint1": {"left": None, "top": '0.2t', "right": '50%', "bottom": None}}]
    result = ocr_obj.get_bbox_for(reg_def_dict_list)
    assert __validate_bbox(
        [region['bbox'] for region in result['regions'][0]['regionBBox']]) is True


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


def test_save_word_tokens_as_json():
    """
    test method
    data_service_provider,
           1: AwsDetectDocumentTextDataServiceProvider(),
           2: AzureReadOcrDataServiceProvider(),
           3: TesseractOcrDataServiceProvider()
    """
    data_service_provider = 1
    ocr_obj = __create_new_instance(data_service_provider)
    res = ocr_obj.save_tokens_as_json(
        "./data/output_aws_word.json", token_type_value=1)
    assert res["isFileSaved"] is True

    data_service_provider = 2
    ocr_obj = __create_new_instance(data_service_provider)
    res = ocr_obj.save_tokens_as_json(
        "./data/output_azure_read_word.json", token_type_value=1)
    assert res["isFileSaved"] is True

    f = open("./data/output_aws_word.json", "r")
    data = json.load(f)
    lst = []
    for i in data:
        lst.append([i["text"], i["page"], i["scalingFactor"]])

    f1 = open("./data/output_azure_read_word.json", "r")
    data1 = json.load(f1)
    lst1 = []
    for i in data1:
        lst1.append([i["text"], i["page"], i["scalingFactor"]])

    lst.sort()
    lst1.sort()
    with open("./data/temp/shortened_aws_word.json", 'w') as fp:
        json.dump(lst, fp)
    with open("./data/temp/shortened_azure_word.json", 'w') as fp:
        json.dump(lst1, fp)


def test_save_lines_tokens_as_json():
    """
    test method
    data_service_provider,
           1: AwsDetectDocumentTextDataServiceProvider(),
           2: AzureReadOcrDataServiceProvider(),
           3: TesseractOcrDataServiceProvider()
    """
    data_service_provider = 1
    ocr_obj = __create_new_instance(data_service_provider)
    res = ocr_obj.save_tokens_as_json(
        "./data/output_aws_lines.json", token_type_value=2)
    assert res["isFileSaved"] is True

    data_service_provider = 2
    ocr_obj = __create_new_instance(data_service_provider)
    res = ocr_obj.save_tokens_as_json(
        "./data/output_azure_read_lines.json", token_type_value=2)
    assert res["isFileSaved"] is True

    f = open("./data/output_aws_lines.json", "r")
    data = json.load(f)
    lst = []
    for i, val in enumerate(data):
        lst.append([val["text"], val["page"], val["scalingFactor"]])
        for j in val["words"]:
            lst[i].extend([j["text"], j["page"], j["scalingFactor"]])

    f1 = open("./data/output_azure_read_lines.json", "r")
    data1 = json.load(f1)
    lst1 = []
    for i, val in enumerate(data1):
        lst1.append([val["text"], val["page"], val["scalingFactor"]])
        for j in val["words"]:
            lst1[i].extend([j["text"], j["page"], j["scalingFactor"]])

    lst.sort()
    lst1.sort()
    with open("./data/temp/shortened_aws_lines.json", 'w') as fp:
        json.dump(lst, fp)
    with open("./data/temp/shortened_azure_lines.json", 'w') as fp:
        json.dump(lst1, fp)


def test_save_phrase_tokens_as_json():
    """
    test method
    data_service_provider,
           1: AwsDetectDocumentTextDataServiceProvider(),
           2: AzureReadOcrDataServiceProvider(),
           3: TesseractOcrDataServiceProvider()
    """
    data_service_provider = 1
    ocr_obj = __create_new_instance(data_service_provider)
    res = ocr_obj.save_tokens_as_json(
        "./data/output_aws_phrase.json", token_type_value=3)
    assert res["isFileSaved"] is True

    data_service_provider = 2
    ocr_obj = __create_new_instance(data_service_provider)
    res = ocr_obj.save_tokens_as_json(
        "./data/output_azure_read_phrase.json", token_type_value=3)
    assert res["isFileSaved"] is True

    f = open("./data/output_aws_phrase.json", "r")
    data = json.load(f)
    lst = []
    for i, val in enumerate(data):
        lst.append([val["text"], val["page"], val["scalingFactor"]])
        for j in val["words"]:
            lst[i].extend([j["text"], j["page"], j["scalingFactor"]])

    f1 = open("./data/output_azure_read_phrase.json", "r")
    data1 = json.load(f1)
    lst1 = []
    for i, val in enumerate(data1):
        lst1.append([val["text"], val["page"], val["scalingFactor"]])
        for j in val["words"]:
            lst1[i].extend([j["text"], j["page"], j["scalingFactor"]])

    lst.sort()
    lst1.sort()
    with open("./data/temp/shortened_aws_phrase.json", 'w') as fp:
        json.dump(lst, fp)
    with open("./data/temp/shortened_azure_phrase.json", 'w') as fp:
        json.dump(lst1, fp)


def __create_new_instance(data_service_provider_choice=None):
    config_params_dict = {'match_method': 'regex', 'similarity_score': 1}

    data_service_provider_dict = {1: AwsDetectDocumentTextDataServiceProvider(),
                                  2: AzureReadOcrDataServiceProvider(),
                                  3: TesseractOcrDataServiceProvider()}
    if data_service_provider_choice:
        data_service_provider = data_service_provider_dict[data_service_provider_choice]
        if data_service_provider_choice == 1:
            ocr_doc_list = glob.glob(
                UNIT_TEST_DATA_LOCATION+"\\aws\\Handwriting Sample 3.png_aws.json")
        elif data_service_provider_choice == 2:
            ocr_doc_list = glob.glob(
                UNIT_TEST_DATA_LOCATION+"\\aws\\Handwriting Sample 3.jpg_azure_read.json")
        elif data_service_provider_choice == 3:
            ocr_doc_list = glob.glob(
                UNIT_TEST_DATA_LOCATION+"\\aws\\Handwriting Sample 3.png.hocr")
    else:
        data_service_provider = AwsDetectDocumentTextDataServiceProvider()
        ocr_doc_list = glob.glob(
            UNIT_TEST_DATA_LOCATION+"\\aws\\Handwriting Sample 3.png_aws.json")
    ocr_obj = ocr_parser.OcrParser(
        ocr_doc_list, data_service_provider=data_service_provider,
        config_params_dict=config_params_dict)

    return ocr_obj


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

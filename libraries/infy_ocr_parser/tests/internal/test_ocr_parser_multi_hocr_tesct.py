# ===============================================================================================================#
# Copyright 2020 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import time
import os
import glob
from infy_ocr_parser import ocr_parser
from infy_ocr_parser.providers.tesseract_ocr_data_service_provider import TesseractOcrDataServiceProvider
import tests.internal.test_helper as thelp


TEMP_DIR_PATH = './data/temp'
if not os.path.exists(TEMP_DIR_PATH):
    os.makedirs(TEMP_DIR_PATH)

INFY_SP_ROOT_PATH = os.environ['INFY_SP_ROOT_PATH']
UNIT_TEST_DATA_LOCATION = INFY_SP_ROOT_PATH + \
    "\\workbenchlibraries - Documents\\SHARED_DATA\\unit_test_data"
FILE_PATH = UNIT_TEST_DATA_LOCATION + \
    "\\ocr_parser\\Assa Abloy America_19052015240693"
OCR_FILE_LIST = glob.glob(FILE_PATH+"/*.hocr")

tesseract_ocr_data_obj = TesseractOcrDataServiceProvider()
ocr_obj = ocr_parser.OcrParser(
    ocr_file_list=OCR_FILE_LIST, data_service_provider=tesseract_ocr_data_obj)


def test_multi_ocr():
    reg_def_dict_list = [{"anchorText": ["expiration date thereof"],
                          "anchorTextMatch": {"method": "normal", "similarityScore": 0.96},
                          "anchorPoint1": {"left": None, "top": 0, "right": 0, "bottom": None}
                          },
                         {"anchorText": ["additional insured"],
                          "anchorTextMatch": {"method": "normal", "similarityScore": 0.96},
                          "anchorPoint1": {"left": None, "top": 0, "right": "50%", "bottom": None}
                          }]
    multi_page_res_bbox, error = thelp.get_bbox_for(
        reg_def_dict_list, ocr_obj, img_file_path=FILE_PATH)
    assert error is None
    assert len(multi_page_res_bbox) == 8


def test_multi_ocr_2():
    reg_def_dict_list = [{"anchorText": ["should any of", "policy provisions"],
                          "anchorPoint1": {"left": None, "top": 0, "right": 0, "bottom": None}
                          },
                         {"anchorText": ["Effective Date"],
                          "anchorPoint1": {"left": None, "top": 0, "right": "50%", "bottom": None}
                          }]
    multi_page_res_bbox, error = thelp.get_bbox_for(
        reg_def_dict_list, ocr_obj, img_file_path=FILE_PATH)
    print(multi_page_res_bbox)
    assert error == "All the key-list elements are not aligned in the same column"


def test_single_page_exclude_footer_1():
    reg_def_dict_list = [{"anchorText": ["^certificate holder"],
                          "anchorTextMatch":{"method": "regex"},
                          "anchorPoint1": {"left": "0", "top": None, "right": None, "bottom": 0},
                          "anchorPoint2": {"left": None, "top": None, "right": "35%", "bottom": "100%"}
                          }]
    sub_reg_def_dict_list = [[{"anchorText": ["The acord name and logo are registered marks of acord"],
                               "anchorPoint1": {"left": "-100%", "top": 0, "right": None, "bottom": None},
                               "anchorPoint2": {"left": None, "top": None, "right": "100%", "bottom": "100%"}
                               }]]
    multi_page_res_bbox, error = thelp.get_bbox_for(
        reg_def_dict_list, ocr_obj, img_file_path=FILE_PATH, sub_reg_def_dict=sub_reg_def_dict_list)
    assert error is None
    assert multi_page_res_bbox == [
        [{'bbox': [146, 2700, 1078, 427], 'page':1, "confidencePct": 90.19, 'scalingFactor': {'external': {'ver': 1.0, 'hor': 1.0}, 'internal': {'ver': 3.299, 'hor': 2.55}}}]]


def test_multi_page_exclude_header_footer_1():
    reg_def_dict_list = [{"pageNum": ["1"], "anchorText": ["expiration date thereof"],
                          "anchorTextMatch": {"method": "normal", "similarityScore": 0.96},
                          "anchorPoint1": {"left": None, "top": 0, "right": 0, "bottom": None}
                          },
                         {"pageNum": [":2"], "anchorText": ["Effective Date"], "anchorTextMatch":{"method": "regex"},
                          "anchorPoint1": {"left": None, "top": 0, "right": "50%", "bottom": None}
                          }]
    sub_reg_def_dict_list = [
        [{"anchorText": ["The acord name and logo are registered marks of acord"],
          "anchorPoint1": {"left": "-100%", "top": 0, "right": None, "bottom": None},
          "anchorPoint2": {"left": None, "top": None, "right": "100%", "bottom": "100%"}}],
        [{"anchorText": ["additional remarks schedule"],
          "anchorPoint1": {"left": "-100%", "top": "-100%", "right": None, "bottom": None},
          "anchorPoint2": {"left": None, "top": 0, "right": "100%", "bottom": None}}]
    ]
    multi_page_res_bbox, error = thelp.get_bbox_for(
        reg_def_dict_list, ocr_obj, img_file_path=FILE_PATH, sub_reg_def_dict=sub_reg_def_dict_list)
    assert error is None
    assert len(multi_page_res_bbox) == 2


def test_multi_page_exclude_header_footer_2():
    reg_def_dict_list = [{"pageNum": ["-1"], "anchorText": ["This endorsement changes the policy. Please read it carefully.", "NOTICE OF CANCELLATION TO THIRD PARTIES"],
                          "anchorPoint1": {"left": "-100%", "top": None, "right": None, "bottom": 0},
                          "anchorPoint2": {"left": None, "top": None, "right": "100%", "bottom": "100%"}
                          }]
    sub_reg_def_dict_list = [[{"pageNum": [-1], "anchorText": ["^Includes copyrighted material of Insurance*", "its permission."],
                               "anchorTextMatch":{"method": "regex"},
                               "anchorPoint1": {"left": "-100%", "top": 0, "right": None, "bottom": None},
                               "anchorPoint2": {"left": None, "top": None, "right": "100%", "bottom": "100%"}
                               }],
                             [{"pageNum": ["-1"], "anchorText": ["This endorsement changes the policy. Please read it carefully.", "NOTICE OF CANCELLATION TO THIRD PARTIES"],
                               "anchorPoint1": {"left": "-100%", "top": 0, "right": None, "bottom": None},
                                 "anchorPoint2": {"left": None, "top": "-100%", "right": "100%", "bottom": None}
                               }]]
    multi_page_res_bbox, error = thelp.get_bbox_for(
        reg_def_dict_list, ocr_obj, img_file_path=FILE_PATH, sub_reg_def_dict=sub_reg_def_dict_list)
    assert error is None
    assert multi_page_res_bbox == [
        [{'bbox': [0, 518, 2550, 2487], 'page':6, 'confidencePct': 95.39, 'scalingFactor': {'external': {'ver': 1.0, 'hor': 1.0}, 'internal': {'ver': 3.299, 'hor': 2.55}}}]]


def test_exclude_region_inside_interest_Reg_1():
    reg_def_dict_list = [{"anchorText": ["This additional remarks form is a"],
                          "anchorPoint1": {"left": "-100%", "top": 0, "right": None, "bottom": None},
                          "anchorPoint2": {"left": None, "top": None, "right": "100%", "bottom": "20%"}
                          }]
    sub_reg_def_dict_list = [[{"anchorText": ["Form Number:"],
                               "anchorPoint1": {"left": "-100%", "top": 0, "right": None, "bottom": None},
                               "anchorPoint2": {"left": None, "top": None, "right": "100%", "bottom": 0}
                               }]]
    multi_page_res_bbox, error = thelp.get_bbox_for(
        reg_def_dict_list, ocr_obj, img_file_path=FILE_PATH, sub_reg_def_dict=sub_reg_def_dict_list)
    assert error is None
    assert multi_page_res_bbox == [[{'bbox': [0, 591, 2550, 49], 'page':2, "confidencePct": 88.8, 'scalingFactor': {'external': {'ver': 1.0, 'hor': 1.0}, 'internal': {'ver': 3.299, 'hor': 2.55}}}, {
        'bbox': [0, 682, 2550, 470], 'page':2, "confidencePct": 95.25, 'scalingFactor': {'external': {'ver': 1.0, 'hor': 1.0}, 'internal': {'ver': 3.299, 'hor': 2.55}}}]]


def test_interest_reg_inside_exclude_region_1():
    reg_def_dict_list = [{"anchorText": ["Form Number:"],
                          "anchorPoint1": {"left": "-100%", "top": 0, "right": None, "bottom": None},
                          "anchorPoint2": {"left": None, "top": None, "right": "100%", "bottom": 0}
                          }]
    sub_reg_def_dict_list = [[{"anchorText": ["This additional remarks form is a"],
                               "anchorPoint1": {"left": "-100%", "top": 0, "right": None, "bottom": None},
                               "anchorPoint2": {"left": None, "top": None, "right": "100%", "bottom": "20%"}
                               }]]
    multi_page_res_bbox, error = thelp.get_bbox_for(
        reg_def_dict_list, ocr_obj, img_file_path=FILE_PATH, sub_reg_def_dict=sub_reg_def_dict_list)
    assert error is None
    assert multi_page_res_bbox == [[]]


def test_merge_mul_img():
    out_path = thelp.__make_dirs(
        TEMP_DIR_PATH+"\\aon\\Assa Abloy America_19052015240693\\merged_images")
    start_time = time.time()
    reg_bbox = [{"bbox": [0, 2741, 2550, 558], "page": 1},
                {"bbox": [0, 0, 2550, 495], "page": 2}]
    result = thelp._merge_images_for(reg_bbox, FILE_PATH, output_path=out_path)

    print("--- completed in {} seconds ---".format(time.time() - start_time))
    assert os.path.exists(result["output"]["imagePath"])


def test_defect_fix_1():
    reg_def_dict_list = [{"anchorText": ["^Includes copyrighted material of Insurance.*", "its permission."],
                          "anchorTextMatch":{"method": "regex"},
                          "anchorPoint1": {"left": "-100%", "top": 0, "right": None, "bottom": None},
                          #   "anchorPoint2": {"left": None, "top": None, "right": "100%", "bottom": "100%"}
                          "anchorPoint2": {"left": None, "top": None, "right": "100%", "bottom": 4000}
                          }]
    sub_reg_def_dict_list = []
    multi_page_res_bbox, error = thelp.get_bbox_for(
        reg_def_dict_list, ocr_obj, img_file_path=FILE_PATH, sub_reg_def_dict=sub_reg_def_dict_list)
    assert error is None
    assert len(multi_page_res_bbox) > 0


def test_defect_fix_2():
    reg_def_dict_list = [{"anchorText": ["2011 Liberty Mutual Group of Companies. All rights reserved.", "^Includes copyrighted material of Insurance*", "its permission."],
                          "anchorTextMatch":{"method": "regex"},
                          "anchorPoint1": {"left": "-100%", "top": 0, "right": None, "bottom": None},
                          "anchorPoint2": {"left": None, "top": None, "right": "100%", "bottom": "120%"}
                          }]
    sub_reg_def_dict_list = []
    multi_page_res_bbox, error = thelp.get_bbox_for(
        reg_def_dict_list, ocr_obj, img_file_path=FILE_PATH, sub_reg_def_dict=sub_reg_def_dict_list)
    assert error is None
    assert len(multi_page_res_bbox) > 0


def test_bbox_without_anchor_txt():
    reg_def_dict_list = [{"pageNum": [2], "anchorText": [],
                          "anchorPoint1": {"left": 0, "top": 0, "right": None, "bottom": None},
                          "anchorPoint2": {"left": 1300, "top": "35%a", "right": None, "bottom": None}}]
    bbox, error = thelp.get_bbox_for(
        reg_def_dict_list, ocr_obj, img_file_path=FILE_PATH)
    assert error is None
    assert bbox[0] == [
        {"bbox": [0, 0, 3315, 1154], "page":2, "confidencePct": 92.77, "scalingFactor": {'external': {'ver': 1.0, 'hor': 1.0}, 'internal': {'ver': 3.299, 'hor': 2.55}}}]


def test_bbox_BOD_1():
    # when two anchor text provided but not anc-point, then consided left-top as a anc-point
    reg_def_dict_list = [{"anchorText": ["{{BOD}}"]},
                         {"pageNum": [":2"], "anchorText": ["Effective Date"], "anchorTextMatch":{"method": "regex"},
                          "anchorPoint1": {"left": None, "top": 0, "right": "50%", "bottom": None}}]
    bbox, error = thelp.get_bbox_for(
        reg_def_dict_list, ocr_obj, img_file_path=FILE_PATH)
    assert error is None
    assert bbox == [[{'bbox': [0, 0, 2550, 3299], 'page':1, "confidencePct": 92.43, 'scalingFactor': {'external': {'ver': 1.0, 'hor': 1.0}, 'internal': {'ver': 3.299, 'hor': 2.55}}},
                     {'bbox': [0, 0, 2550, 495], 'page':2, "confidencePct": 95.5, 'scalingFactor':{'external': {'ver': 1.0, 'hor': 1.0}, 'internal': {'ver': 3.299, 'hor': 2.55}}}]]


def test_bbox_BOD_2():
    # when two anchor text provided but not anc-point, then consided left-top as a anc-point
    reg_def_dict_list = [{"pageNum": [":2"], "anchorText": ["{{BOD}}"]},
                         {"pageNum": [":2"], "anchorText": ["Effective Date"], "anchorTextMatch":{"method": "regex"},
                          "anchorPoint1": {"left": None, "top": 0, "right": "50%", "bottom": None}}]
    bbox, error = thelp.get_bbox_for(
        reg_def_dict_list, ocr_obj, img_file_path=FILE_PATH)
    assert error is None
    assert bbox == [[{'bbox': [0, 0, 2550, 3299], 'page':1, "confidencePct": 92.43, 'scalingFactor': {'external': {'ver': 1.0, 'hor': 1.0}, 'internal': {'ver': 3.299, 'hor': 2.55}}},
                     {'bbox': [0, 0, 2550, 495], 'page':2, "confidencePct": 95.5, 'scalingFactor': {'external': {'ver': 1.0, 'hor': 1.0}, 'internal': {'ver': 3.299, 'hor': 2.55}}}]]


def test_bbox_BOD_3():
    # when two anchor text provided but not anc-point, then consided left-top as a anc-point
    reg_def_dict_list = [{"pageNum": ["2"], "anchorText": ["{{BOD}}"]},
                         {"pageNum": [":2"], "anchorText": ["Effective Date"], "anchorTextMatch":{"method": "regex"},
                          "anchorPoint1": {"left": None, "top": 0, "right": "50%", "bottom": None}}]
    bbox, error = thelp.get_bbox_for(
        reg_def_dict_list, ocr_obj, img_file_path=FILE_PATH)
    assert error is None
    assert bbox == [
        [{'bbox': [0, 0, 2010, 478], 'page':2, 'confidencePct': 94.1, 'scalingFactor': {'external': {'ver': 1.0, 'hor': 1.0}, 'internal': {'ver': 3.299, 'hor': 2.55}}}]]


def test_bbox_EOD_1():
    # when two anchor text provided but not anc-point, then consided left-top as a anc-point
    reg_def_dict_list = [{"anchorText": ["{{EOD}}"]},
                         {"pageNum": [":2"], "anchorText": ["Effective Date"], "anchorTextMatch":{"method": "regex"},
                          "anchorPoint1": {"left": None, "top": 0, "right": "50%", "bottom": None}}]
    bbox, error = thelp.get_bbox_for(
        reg_def_dict_list, ocr_obj, img_file_path=FILE_PATH)
    assert error is None
    assert bbox == [[{'bbox': [0, 0, 2550, 3299], 'page':6, "confidencePct": -1, 'scalingFactor': {'external': {'ver': 1.0, 'hor': 1.0}, 'internal': {'ver': 3.299, 'hor': 2.55}}},
                     {'bbox': [0, 0, 2550, 3299], 'page':3, "confidencePct": 92.08, 'scalingFactor': {'external': {
                         'ver': 1.0, 'hor': 1.0}, 'internal': {'ver': 3.299, 'hor': 2.55}}},
                     {'bbox': [0, 0, 2550, 3299], 'page':4, "confidencePct": 93.85, 'scalingFactor': {'external': {
                         'ver': 1.0, 'hor': 1.0}, 'internal': {'ver': 3.299, 'hor': 2.55}}},
                     {'bbox': [0, 0, 2550, 3299], 'page':5, "confidencePct": 94.73, 'scalingFactor': {'external': {
                         'ver': 1.0, 'hor': 1.0}, 'internal': {'ver': 3.299, 'hor': 2.55}}},
                     {'bbox': [0, 478, 2550, 2821], 'page':2, "confidencePct": 95.5, 'scalingFactor': {'external': {'ver': 1.0, 'hor': 1.0}, 'internal': {'ver': 3.299, 'hor': 2.55}}}]]


def test_bbox_EOD_2():
    # when two anchor text provided but not anc-point, then consided left-top as a anc-point
    reg_def_dict_list = [{"pageNum": ["3"], "anchorText": ["{{EOD}}"]},
                         {"pageNum": [":2"], "anchorText": ["Effective Date"], "anchorTextMatch":{"method": "regex"},
                          "anchorPoint1": {"left": None, "top": 0, "right": "50%", "bottom": None}}]
    bbox, error = thelp.get_bbox_for(
        reg_def_dict_list, ocr_obj, img_file_path=FILE_PATH)
    assert error is None
    assert bbox == [[{'bbox': [0, 0, 2550, 3299], 'page':3, "confidencePct": -1, 'scalingFactor': {'external': {'ver': 1.0, 'hor': 1.0}, 'internal': {'ver': 3.299, 'hor': 2.55}}},
                     {'bbox': [0, 478, 2550, 2821], 'page':2, "confidencePct": 95.5, 'scalingFactor': {'external': {'ver': 1.0, 'hor': 1.0}, 'internal': {'ver': 3.299, 'hor': 2.55}}}]]


def test_bbox_BOD_EOD_1():
    # when two anchor text provided but not anc-point, then consided left-top as a anc-point
    reg_def_dict_list = [{"pageNum": ["1"], "anchorText": ["{{EOD}}"]},
                         {"pageNum": ["1"], "anchorText": ["{{BOD}}"]}]
    bbox, error = thelp.get_bbox_for(
        reg_def_dict_list, ocr_obj, img_file_path=FILE_PATH)
    assert error is None
    assert bbox == [
        [{'bbox': [0, 0, 2550, 3299], 'page':1, 'confidencePct': 92.43, 'scalingFactor': {'external': {'ver': 1.0, 'hor': 1.0}, 'internal': {'ver': 3.299, 'hor': 2.55}}}]]


def test_bbox_BOD_EOD_2():
    # when two anchor text provided but not anc-point, then consided left-top as a anc-point
    reg_def_dict_list = [{"pageNum": ["1"], "anchorText": ["{{EOD}}"]},
                         {"pageNum": ["1"], "anchorText": ["{{BOD}}"]}]
    sub_reg_def_dict_list = [[{"anchorText": [],
                               "anchorPoint1": {"left": 0, "top": 0, "right": None, "bottom": None},
                               "anchorPoint2": {"left": None, "top": "10%a", "right": 0, "bottom": None}
                               }],
                             [{"anchorText": [],
                               "anchorPoint1": {"left": None, "top": None, "right": 0, "bottom": 0},
                               "anchorPoint2": {"left": 0, "top": "90%a", "right": None, "bottom": None}
                               }]]
    bbox, error = thelp.get_bbox_for(
        reg_def_dict_list, ocr_obj, img_file_path=FILE_PATH, sub_reg_def_dict=sub_reg_def_dict_list)
    assert error is None
    assert bbox == [
        [{'bbox': [0, 329, 2550, 2640], 'page':1, 'confidencePct': 92.43, 'scalingFactor': {'external': {'ver': 1.0, 'hor': 1.0}, 'internal': {'ver': 3.299, 'hor': 2.55}}}]]


def test_bbox_error_invalid_key():
    # when two anchor text provided but not anc-point, then consided left-top as a anc-point
    reg_def_dict_list = [{"pageNum": ["1"], "anchorText": ["{{EOD}}"]},
                         {"pageNum": ["1"], "anchorText": ["{{BOD}}"]}]
    sub_reg_def_dict_list = [[{"anchorText": [],
                               "stranger":"unrecognized parameter",
                               "anchorPoint1": {"left": 0, "top": 0, "right": None, "bottom": None},
                               "anchorPoint2": {"left": None, "top": "10%a", "right": 0, "bottom": None}
                               }],
                             [{"anchorText1": [],
                               "anchorPoint1": {"left": None, "top": None, "right": 0, "bottom": 0},
                               "anchorPoint2": {"left": 0, "top": "90%a", "right": None, "bottom": None}
                               }]]
    bbox, error = thelp.get_bbox_for(
        reg_def_dict_list, ocr_obj, img_file_path=FILE_PATH, sub_reg_def_dict=sub_reg_def_dict_list)
    assert not bbox
    assert error == "Invalid keys found in subtract_region_definition: ['stranger']. Invalid keys found in subtract_region_definition: ['anchorText1']."

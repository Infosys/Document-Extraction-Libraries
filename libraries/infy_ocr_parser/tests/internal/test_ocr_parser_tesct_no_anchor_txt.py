# ===============================================================================================================#
# Copyright 2020 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import os
import glob
import imageio
import tests.internal.test_helper as thelp
from infy_ocr_parser import ocr_parser
from infy_ocr_parser.providers.tesseract_ocr_data_service_provider import TesseractOcrDataServiceProvider

TEMP_DIR_PATH = './data/temp'

INFY_SP_ROOT_PATH = os.environ['INFY_SP_ROOT_PATH']
UNIT_TEST_DATA_LOCATION = INFY_SP_ROOT_PATH + \
    "\\workbenchlibraries - Documents\\SHARED_DATA\\unit_test_data\\ocr_parser"
img_file_path = UNIT_TEST_DATA_LOCATION + \
    "\\Assa Abloy America_19052015240546.jpg"
ocr_doc_list_psm3 = glob.glob(
    UNIT_TEST_DATA_LOCATION+"\\aon\\psm3\\Assa Abloy America_19052015240546.jpg.hocr")

tesseract_ocr_data_obj = TesseractOcrDataServiceProvider()
ocr_obj = ocr_parser.OcrParser(
    ocr_doc_list_psm3, data_service_provider=tesseract_ocr_data_obj)

img = imageio.imread(img_file_path)

# -------------------------------------------------------------------------
# Note: anchor1 - anchorPoint1, anchor2 - anchorPoint2, lt- left-top, rb-right-bottom
# -------------------------------------------------------------------------


def test_bbox_ap1_lt_ap2_lt_1():
    # anchor1: l=px, t=px
    # anchor2 : r=px, b=%
    reg_def_dict_list = [{"anchorText": [],
                          "anchorPoint1": {"left": 0, "top": 0, "right": None, "bottom": None},
                          "anchorPoint2": {"left": 1300, "top": "35%a", "right": None, "bottom": None},
                          "pageDimensions": {
        "width": 2550,
        "height": 3299
    }}]
    bbox, error = thelp.get_bbox_for(reg_def_dict_list, ocr_obj, img.copy())
    assert bbox[0] == [
        {"bbox": [0, 0, 1300, 1154], "page":1, 'confidencePct': 94.0, "scalingFactor": {'external': {'ver': 1.0, 'hor': 1.0}, 'internal': {'ver': 1.0, 'hor': 1.0}}}]


def test_bbox_ap1_lt_ap2_lt_2():
    # anchor1: l=px, t=%
    # anchor2 : r=%, b=%
    reg_def_dict_list = [{"anchorText": [],
                          "anchorPoint1": {"left": 0, "top": "17%a", "right": None, "bottom": None},
                          "anchorPoint2": {"left": "50%a", "top": "100%a", "right": None, "bottom": None},
                          "pageDimensions": {
        "width": 2550,
        "height": 3299
    }}]
    bbox, error = thelp.get_bbox_for(reg_def_dict_list, ocr_obj, img.copy())
    assert bbox[0] == [
        {"bbox": [0, 560, 1275, 2739], "page":1, 'confidencePct': 91.22, "scalingFactor": {'external': {'ver': 1.0, 'hor': 1.0}, 'internal': {'ver': 1.0, 'hor': 1.0}}}]


def test_bbox_ap1_lt_ap2_rb_1():
    # anchor1: l,t=px
    # anchor2 : r,b=%
    reg_def_dict_list = [{"anchorText": [],
                          "anchorPoint1": {"left": 0, "top": 0, "right": None, "bottom": None},
                          "anchorPoint2": {"left": None, "top": None, "right": 0, "bottom": 0},
                          "pageDimensions": {
        "width": 2550,
        "height": 3299
    }}]
    bbox, error = thelp.get_bbox_for(reg_def_dict_list, ocr_obj, img.copy())
    assert bbox[0] == [
        {"bbox": [0, 0, 2550, 3299], "page":1, 'confidencePct': 88.41, "scalingFactor":{'external': {'ver': 1.0, 'hor': 1.0}, 'internal': {'ver': 1.0, 'hor': 1.0}}}]


def test_bbox_ap1_lt_ap2_rt_3():
    # anchor1: l=px, t=%
    # anchor2 : r=%, b=%
    reg_def_dict_list = [{"anchorText": [],
                          "anchorPoint1": {"left": 0, "top": "10%a", "right": None, "bottom": None},
                          "anchorPoint2": {"left": None, "top": "17%a", "right": "-50%a", "bottom": None},
                          "pageDimensions": {
        "width": 2550,
        "height": 3299
    }}]
    bbox, error = thelp.get_bbox_for(reg_def_dict_list, ocr_obj, img.copy())
    assert bbox[0] == [
        {"bbox": [0, 329, 1275, 231], "page":1, 'confidencePct': 95.28, "scalingFactor": {'external': {'ver': 1.0, 'hor': 1.0}, 'internal': {'ver': 1.0, 'hor': 1.0}}}]


def test_bbox_ap1_rt_ap2_rb_1():
    # anchor1: r=px, t=%
    # anchor2 : l=%, b=%
    reg_def_dict_list = [{"anchorText": [],
                          "anchorPoint1": {"left": None, "top": "17%a", "right": 0, "bottom": None},
                          "anchorPoint2": {"left": None, "top": None, "right": "-50%a", "bottom": "-20%a"},
                          "pageDimensions": {
        "width": 2550,
        "height": 3299
    }}]
    bbox, error = thelp.get_bbox_for(reg_def_dict_list, ocr_obj, img.copy())
    assert bbox[0] == [
        {"bbox": [1275, 560, 1275, 2080], "page":1, 'confidencePct': 83.15, "scalingFactor": {'external': {'ver': 1.0, 'hor': 1.0}, 'internal': {'ver': 1.0, 'hor': 1.0}}}]


def test_bbox_ap1_rt_ap2_rb_2():
    # anchor1: r=%, t=%
    # anchor2 : l=%, b=%
    reg_def_dict_list = [{"anchorText": [],
                          "anchorPoint1": {"left": None, "top": "17%a", "right": "-5%a", "bottom": None},
                          "anchorPoint2": {"left": None, "top": None, "right": "-50%a", "bottom": "-20%a"},
                          "pageDimensions": {
        "width": 2550,
        "height": 3299
    }}]
    bbox, error = thelp.get_bbox_for(reg_def_dict_list, ocr_obj, img.copy())
    assert bbox[0] == [
        {"bbox": [1275, 560, 1148, 2080], "page":1, "confidencePct": 87.32, "scalingFactor": {'external': {'ver': 1.0, 'hor': 1.0}, 'internal': {'ver': 1.0, 'hor': 1.0}}}]


def test_bbox_ap1_rt_ap2_lb_3():
    # anchor1: r=%, t=px
    # anchor2 : l=%, b=%
    reg_def_dict_list = [{"anchorText": [],
                          "anchorPoint1": {"left": None, "top": 0, "right": "-5%a", "bottom": None},
                          "anchorPoint2": {"left": "50%a", "top": None, "right": None, "bottom": "-20%a"},
                          "pageDimensions": {
        "width": 2550,
        "height": 3299
    }}]
    bbox, error = thelp.get_bbox_for(reg_def_dict_list, ocr_obj, img.copy())
    assert bbox[0] == [
        {"bbox": [1275, 0, 1148, 2640], "page":1, "confidencePct": 89.10, "scalingFactor": {'external': {'ver': 1.0, 'hor': 1.0}, 'internal': {'ver': 1.0, 'hor': 1.0}}}]


def test_bbox_ap1_rb_ap2_lt_1():
    # anchor1: r=px, b=px
    # anchor2 : l=%, t=%
    reg_def_dict_list = [{"anchorText": [],
                          "anchorPoint1": {"left": None, "top": None, "right": 0, "bottom": 0},
                          "anchorPoint2": {"left": "50%a", "top": "50%a", "right": None, "bottom": None},
                          "pageDimensions": {
        "width": 2550,
        "height": 3299
    }}]
    bbox, error = thelp.get_bbox_for(reg_def_dict_list, ocr_obj, img.copy())
    assert bbox[0] == [
        {"bbox": [1275, 1649, 1275, 1650], "page":1, 'confidencePct': 78.95, "scalingFactor": {'external': {'ver': 1.0, 'hor': 1.0}, 'internal': {'ver': 1.0, 'hor': 1.0}}}]


def test_bbox_ap1_rb_ap2_lt_2():
    # anchor1: r=%, b=px
    # anchor2 : l=%, t=%
    reg_def_dict_list = [{"anchorText": [],
                          "anchorPoint1": {"left": None, "top": None, "right": "-5%a", "bottom": 0},
                          "anchorPoint2": {"left": "50%a", "top": "50%a", "right": None, "bottom": None},
                          "pageDimensions": {
        "width": 2550,
        "height": 3299
    }}]
    bbox, error = thelp.get_bbox_for(reg_def_dict_list, ocr_obj, img.copy())
    assert bbox[0] == [
        {"bbox": [1275, 1649, 1148, 1650], "page":1, 'confidencePct': 83.37, "scalingFactor": {'external': {'ver': 1.0, 'hor': 1.0}, 'internal': {'ver': 1.0, 'hor': 1.0}}}]


def test_bbox_ap1_rb_ap2_lt_3():
    # anchor1: r=%, b=%
    # anchor2 : l=%, t=%
    reg_def_dict_list = [{"anchorText": [],
                          "anchorPoint1": {"left": None, "top": None, "right": "-5%a", "bottom": "-5%a"},
                          "anchorPoint2": {"left": "50%a", "top": "50%a", "right": None, "bottom": None},
                          "pageDimensions": {
        "width": 2550,
        "height": 3299
    }}]
    bbox, error = thelp.get_bbox_for(reg_def_dict_list, ocr_obj, img.copy())
    assert bbox[0] == [
        {"bbox": [1275, 1649, 1148, 1486], "page":1, "confidencePct": 82.92, "scalingFactor": {'external': {'ver': 1.0, 'hor': 1.0}, 'internal': {'ver': 1.0, 'hor': 1.0}}}]


def test_bbox_ap1_lb_ap2_rt_1():
    # anchor1: r=px, b=px
    # anchor2 : l=%, t=%
    reg_def_dict_list = [{"anchorText": [],
                          "anchorPoint1": {"left": 0, "top": None, "right": None, "bottom": 0},
                          "anchorPoint2": {"left": None, "top": "50%a", "right": "-50%a", "bottom": None},
                          "pageDimensions": {
        "width": 2550,
        "height": 3299
    }}]
    bbox, error = thelp.get_bbox_for(reg_def_dict_list, ocr_obj, img.copy())
    assert bbox[0] == [
        {"bbox": [0, 1649, 1275, 1650], "page":1, "confidencePct": 88.76, "scalingFactor": {'external': {'ver': 1.0, 'hor': 1.0}, 'internal': {'ver': 1.0, 'hor': 1.0}}}]


def test_bbox_ap1_lb_ap2_rt_2():
    # anchor1: r=%, b=%
    # anchor2 : l=%, t=%
    reg_def_dict_list = [{"anchorText": [],
                          "anchorPoint1": {"left": "5%a", "top": None, "right": None, "bottom": 0},
                          "anchorPoint2": {"left": None, "top": "50%a", "right": "-50%a", "bottom": None},
                          "pageDimensions": {
        "width": 2550,
        "height": 3299
    }}]
    bbox, error = thelp.get_bbox_for(reg_def_dict_list, ocr_obj, img.copy())
    assert bbox[0] == [
        {"bbox": [127, 1649, 1148, 1650], "page":1, "confidencePct": 88.76, "scalingFactor": {'external': {'ver': 1.0, 'hor': 1.0}, 'internal': {'ver': 1.0, 'hor': 1.0}}}]


def test_bbox_ap1_lb_ap2_rt_3():
    # anchor1: r=%, b=%
    # anchor2 : l=%, t=%
    reg_def_dict_list = [{"anchorText": [],
                          "anchorPoint1": {"left": "5%a", "top": None, "right": None, "bottom": "-5%a"},
                          "anchorPoint2": {"left": None, "top": "50%a", "right": "-50%a", "bottom": None},
                          "pageDimensions": {
        "width": 2550,
        "height": 3299
    }}]
    bbox, error = thelp.get_bbox_for(reg_def_dict_list, ocr_obj, img.copy())
    assert bbox[0] == [
        {"bbox": [127, 1649, 1148, 1486], "page":1, "confidencePct": 88.25, "scalingFactor": {'external': {'ver': 1.0, 'hor': 1.0}, 'internal': {'ver': 1.0, 'hor': 1.0}}}]


def test_bbox_ap1_lt_ap2_lt_4():
    # which is equivalent to "{{BOP}}"
    reg_def_dict_list = [{"anchorText": [],
                          "anchorPoint1": {"left": "10%a", "top": "5%a", "right": None, "bottom": None},
                          "anchorPoint2": {"left": "50%a", "top": "10%a", "right": None, "bottom": None},
                          "pageDimensions": {
        "width": 2550,
        "height": 3299
    }}]
    bbox, error = thelp.get_bbox_for(reg_def_dict_list, ocr_obj, img.copy())
    assert bbox == [
        [{"bbox": [255, 164, 1020, 165], "page":1, "confidencePct": 91.27, "scalingFactor": {'external': {'ver': 1.0, 'hor': 1.0}, 'internal': {'ver': 1.0, 'hor': 1.0}}}]]


def test_bbox_ap1_rb_ap2_rb_5():
    # which is equivalent to "{{EOP}}"
    reg_def_dict_list = [{"anchorText": [],
                          "anchorPoint1": {"left": None, "top": None, "right": "-10%a", "bottom": "-5%a"},
                          "anchorPoint2": {"left": None, "top": None, "right": "-50%a", "bottom": "-10%a"},
                          "pageDimensions": {
        "width": 2550,
        "height": 3299
    }}]
    bbox, error = thelp.get_bbox_for(reg_def_dict_list, ocr_obj, img.copy())
    assert bbox == [
        [{'bbox': [1275, 2970, 1020, 165], "page":1, "confidencePct": 94.4, "scalingFactor": {'external': {'ver': 1.0, 'hor': 1.0}, 'internal': {'ver': 1.0, 'hor': 1.0}}}]]


def test_bbox_exception_2():
    reg_def_dict_list = [{"anchorText": [],
                          "anchorPoint1": {"left": "0", "top": 0, "right": None, "bottom": None}},
                         {"anchorText": [],
                          "anchorPoint1": {"left": "0", "top": 0, "right": None, "bottom": None}}]
    bbox, error = thelp.get_bbox_for(reg_def_dict_list, ocr_obj, img.copy())
    assert error == "Two anchorText are required."


def test_bbox_exception_3():
    reg_def_dict_list = [{"anchorText": [""],
                          "anchorPoint1": {"left": "0", "top": 0, "right": None, "bottom": None}},
                         {"anchorText": [""],
                          "anchorPoint1": {"left": "0", "top": 0, "right": None, "bottom": None}}]
    bbox, error = thelp.get_bbox_for(reg_def_dict_list, ocr_obj, img.copy())
    assert error == "Two anchorText are required."


def test_bbox_exception_4():
    reg_def_dict_list = [{"anchorText": [],
                          "anchorPoint1": {"left": "abc%a", "top": 0, "right": None, "bottom": None},
                          "anchorPoint2": {"left": None, "top": None, "right": "30%a", "bottom": "35%a"}}]
    bbox, error = thelp.get_bbox_for(reg_def_dict_list, ocr_obj, img.copy())
    assert error == "Please correct the anchor1/anchor2 Points. Valid values are null, (-/+)numbers, strings containing (-/+)numbers or num(px) or (-/+)% or (-/+)%r or (+)%a or (-/+)t."


def test_bbox_exception_5():
    reg_def_dict_list = [{"anchorText": [""],
                          "anchorPoint1": {"left": "abc%a", "top": 0, "right": None, "bottom": None}},
                         {"anchorText": [""],
                          "anchorPoint1": {"left": "0", "top": 0, "right": None, "bottom": None}}]
    bbox, error = thelp.get_bbox_for(reg_def_dict_list, ocr_obj, img.copy())
    assert error == "Two anchorText are required."


def test_bbox_exception_6():
    reg_def_dict_list = [{"anchorText": [],
                          "anchorPoint1": {"left": "-1", "top": 0, "right": None, "bottom": None},
                          "anchorPoint2": {"left": None, "top": None, "right": "30%a", "bottom": "35%a"}}]
    bbox, error = thelp.get_bbox_for(reg_def_dict_list, ocr_obj, img.copy())
    assert error == "Left-Top negative points or Right-Bottom positive points of anchorPoint1/anchorPoint2 are not allowed when (-/+)%a or anchorText not provided."


def test_bbox_exception_7():
    reg_def_dict_list = [{"anchorText": [],
                          "anchorPoint1": {"left": "-1%a", "top": 0, "right": None, "bottom": None},
                          "anchorPoint2": {"left": None, "top": None, "right": "30%a", "bottom": "35%a"}}]
    bbox, error = thelp.get_bbox_for(reg_def_dict_list, ocr_obj, img.copy())
    assert error == "Left-Top negative points or Right-Bottom positive points of anchorPoint1/anchorPoint2 are not allowed when (-/+)%a or anchorText not provided."


def test_bbox_exception_8():
    reg_def_dict_list = [{"anchorText": [],
                          "anchorPoint1": {"left": 0, "top": 0, "right": 0, "bottom": 0},
                          "anchorPoint2": {"left": None, "top": None, "right": "30%a", "bottom": "35%a"}}]
    bbox, error = thelp.get_bbox_for(reg_def_dict_list, ocr_obj, img.copy())
    assert error == "Provide only two value for anchor1 and anchor2 points. The values provided cannot be for both left and right or top and bottom."


def test_bbox_exception_9():
    reg_def_dict_list = [{"anchorText": [],
                          "anchorPoint1": {"left": 0, "top": 0, "right": None, "bottom": None},
                          "anchorPoint2": {"left": 0, "top": 0, "right": 0, "bottom": 0}}]
    bbox, error = thelp.get_bbox_for(reg_def_dict_list, ocr_obj, img.copy())
    assert error == "Provide only two value for anchor1 and anchor2 points. The values provided cannot be for both left and right or top and bottom."


def test_bbox_exception_10():
    reg_def_dict_list = [{"anchorText": [],
                          "anchorPoint1": {"left": 0, "top": 0, "right": None, "bottom": None},
                          "anchorPoint2": {"left": 0, "top": None, "right": 0, "bottom": None}}]
    bbox, error = thelp.get_bbox_for(reg_def_dict_list, ocr_obj, img.copy())
    assert error == "Provide only two value for anchor1 and anchor2 points. The values provided cannot be for both left and right or top and bottom."


def test_bbox_exception_11():
    reg_def_dict_list = [{"anchorText": [],
                          "anchorPoint1": {"left": None, "top": 0, "right": None, "bottom": 0},
                          "anchorPoint2": {"left": 0, "top": 0, "right": None, "bottom": None}}]
    bbox, error = thelp.get_bbox_for(reg_def_dict_list, ocr_obj, img.copy())
    assert error == "Provide only two value for anchor1 and anchor2 points. The values provided cannot be for both left and right or top and bottom."


def test_bbox_exception_12():
    # anchor1: l,t=px
    # anchor2 : r,b=%
    reg_def_dict_list = [{"anchorText": [],
                          "anchorPoint1": {"left": 0, "top": 0, "right": None, "bottom": None},
                          "anchorPoint2": {"left": None, "top": None, "right": "30%a", "bottom": "35%a"}}]
    bbox, error = thelp.get_bbox_for(reg_def_dict_list, ocr_obj, img.copy())
    assert error == "Left-Top negative points or Right-Bottom positive points of anchorPoint1/anchorPoint2 are not allowed when (-/+)%a or anchorText not provided."

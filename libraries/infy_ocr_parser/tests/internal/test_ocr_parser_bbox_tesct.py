# ===============================================================================================================#
# Copyright 2020 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import os
import glob
from shutil import copyfile

import imageio
import pytest
from infy_ocr_parser import ocr_parser
from infy_ocr_parser.providers.tesseract_ocr_data_service_provider import TesseractOcrDataServiceProvider
import tests.internal.test_helper as thelp

INFY_SP_ROOT_PATH = os.environ['INFY_SP_ROOT_PATH']
UNIT_TEST_DATA_LOCATION = INFY_SP_ROOT_PATH + \
    "\\workbenchlibraries - Documents\\SHARED_DATA\\unit_test_data\\ocr_parser"
img_file_path = UNIT_TEST_DATA_LOCATION + \
    "\\Assa Abloy America_19052015240546.jpg"
ocr_doc_list_psm3 = glob.glob(
    UNIT_TEST_DATA_LOCATION+"\\aon\\psm3\\Assa Abloy America_19052015240546.jpg.hocr")
ocr_doc_list_psm11 = glob.glob(
    UNIT_TEST_DATA_LOCATION+"\\aon\\psm11\\Assa Abloy America_19052015240546.jpg.hocr")

config_params_dict_2 = {'match_method': 'regex', 'similarity_score': 1}

tesseract_ocr_data_obj = TesseractOcrDataServiceProvider()
ocr_obj = ocr_parser.OcrParser(
    ocr_doc_list_psm3, data_service_provider=tesseract_ocr_data_obj,
    config_params_dict=config_params_dict_2)

img = imageio.imread(img_file_path)


def test_get_bbox_with_no_anchor_points_1():
    reg_def_dict_list = [{"anchorText": ["E-{0,1}mail"],
                          "pageDimensions":{
        "width": 2550,
        "height": 3299
    }}]
    ap_bbox, error = thelp.get_bbox_for(
        reg_def_dict_list, ocr_obj, img.copy())
    assert ap_bbox == [
        [{"bbox": [1281, 682, 75, 17], "page":1, "confidencePct": 96.0, "scalingFactor": {'internal': {'ver': 1.0, 'hor': 1.0}, 'external': {'ver': 1.0, 'hor': 1.0}}}]]


def test_get_bbox_with_no_anchor_points_2():
    ocr_obj = ocr_parser.OcrParser(ocr_doc_list_psm11, tesseract_ocr_data_obj, config_params_dict={
        'match_method': 'regex', 'similarity_score': 1})

    reg_def_dict_list = [{"anchorText": ["SCHEDULED", "AUTOS"],
                          "pageDimensions":{
        "width": 2550,
        "height": 3299
    }}]
    bbox, error = thelp.get_bbox_for(
        reg_def_dict_list, ocr_obj, img.copy())
    assert bbox == [
        [{"bbox": [527, 1761, 139, 44], "page":1, "confidencePct": 95.0, "scalingFactor": {'internal': {'ver': 1.0, 'hor': 1.0}, 'external': {'ver': 1.0, 'hor': 1.0}}}]]
    reg_def_dict_list = [{"anchorText": ["NON-OWNED", "AUTOS ONLY"],
                          "pageDimensions":{
        "width": 2550,
        "height": 3299
    }}]
    bbox, error = thelp.get_bbox_for(reg_def_dict_list, ocr_obj, img.copy())
    assert bbox == [
        [{"bbox": [529, 1817, 146, 44], "page":1, "confidencePct": 96.0, "scalingFactor": {'internal': {'ver': 1.0, 'hor': 1.0}, 'external': {'ver': 1.0, 'hor': 1.0}}}]]


def test_get_bbox_with_no_anchor_points_2_synonym():
    ocr_obj = ocr_parser.OcrParser(ocr_doc_list_psm11, tesseract_ocr_data_obj, config_params_dict={
        'match_method': 'regex', 'similarity_score': 1})
    reg_def_dict_list = [
        {"anchorText": [["SCHEDULED", "NON-OWNED"], ["AUTOS", "AUTOS ONLY"]],
         "pageDimensions":{
            "width": 2550,
            "height": 3299
        }}]
    bbox, error = thelp.get_bbox_for(
        reg_def_dict_list, ocr_obj, img.copy())
    assert bbox == [[{'bbox': [527, 1761, 139, 44], 'page': 1, 'confidencePct': 95.0, 'scalingFactor': {
        'external': {'ver': 1.0, 'hor': 1.0}, 'internal': {'ver': 1.0, 'hor': 1.0}}}],
        [{'bbox': [529, 1817, 146, 44], 'page': 1, 'confidencePct': 96.0, 'scalingFactor': {
            'external': {'ver': 1.0, 'hor': 1.0}, 'internal': {'ver': 1.0, 'hor': 1.0}}}]]


def test_get_bbox_with_no_anchor_points_3():
    reg_def_dict_list = [{"anchorText": ["E-mail"],
                          "anchorPoint1": {"left": None, "top": None, "right": None, "bottom": None},
                          "anchorPoint2": {"left": None, "top": None, "right": None, "bottom": None},
                          "pageDimensions": {
        "width": 2550,
        "height": 3299
    }}]
    ap_bbox, error = thelp.get_bbox_for(
        reg_def_dict_list, ocr_obj, img.copy())
    assert ap_bbox == [
        [{"bbox": [1281, 682, 75, 17], "page":1, "confidencePct": 96.0, "scalingFactor": {'internal': {'ver': 1.0, 'hor': 1.0}, 'external': {'ver': 1.0, 'hor': 1.0}}}]]


def test_get_bbox_with_no_anchor_points_4():
    reg_def_dict_list = [{"anchorText": ["E-mail"],
                          "anchorPoint1": {"left": None, "top": None, "right": None, "bottom": None},
                          "pageDimensions": {
        "width": 2550,
        "height": 3299
    }}]
    ap_bbox, error = thelp.get_bbox_for(
        reg_def_dict_list, ocr_obj, img.copy())
    assert ap_bbox == [
        [{"bbox": [1281, 682, 75, 17], "page":1, "confidencePct": 96.0, "scalingFactor": {'internal': {'ver': 1.0, 'hor': 1.0}, 'external': {'ver': 1.0, 'hor': 1.0}}}]]


def test_get_bbox_with_no_anchor_points_5():
    reg_def_dict_list = [{"anchorText": ["E-mail"],
                          "anchorPoint1": {},
                          "anchorPoint2": {},
                          "pageDimensions": {
        "width": 2550,
        "height": 3299
    }}]
    ap_bbox, error = thelp.get_bbox_for(
        reg_def_dict_list, ocr_obj, img.copy())
    assert ap_bbox == [
        [{"bbox": [1281, 682, 75, 17], "page":1, "confidencePct": 96.0, "scalingFactor": {'internal': {'ver': 1.0, 'hor': 1.0}, 'external': {'ver': 1.0, 'hor': 1.0}}}]]


def test_get_bbox_with_no_anchor_points_6():
    reg_def_dict_list = [{"anchorText": ["E-mail"],
                          "anchorPoint1": None,
                          "anchorPoint2": None,
                          "pageDimensions":{
        "width": 2550,
        "height": 3299
    }}]
    ap_bbox, error = thelp.get_bbox_for(
        reg_def_dict_list, ocr_obj, img.copy())
    assert ap_bbox == [
        [{"bbox": [1281, 682, 75, 17], "page":1, "confidencePct": 96.0, "scalingFactor": {'internal': {'ver': 1.0, 'hor': 1.0}, 'external': {'ver': 1.0, 'hor': 1.0}}}]]


def test_get_bbox_for_1anc():
    reg_def_dict_list = [{"anchorText": ["phone"],
                          "anchorPoint1": {"left": 0, "top": -30, "right": None, "bottom": None},
                          "anchorPoint2": {"left": None, "top": None, "right": 1000, "bottom": 150},
                          "pageDimensions": {
        "width": 2550,
        "height": 3299
    }}]
    ap_bbox, error = thelp.get_bbox_for(
        reg_def_dict_list, ocr_obj, img.copy())
    assert ap_bbox == [
        [{"bbox": [1275, 582, 1078, 209], "page":1, "confidencePct": 78.85, "scalingFactor": {'internal': {'ver': 1.0, 'hor': 1.0}, 'external': {'ver': 1.0, 'hor': 1.0}}}]]


def test_get_bbox_for_1anc_1():
    reg_def_dict_list = [{"anchorText": ["phone"],
                          "anchorPoint1": {"left": None, "top": 0, "right": 0, "bottom": None},
                          "anchorPoint2": {"left": None, "top": None, "right": "600", "bottom": "50px"},
                          "pageDimensions": {
        "width": 2550,
        "height": 3299
    }}]
    ap_bbox, error = thelp.get_bbox_for(
        reg_def_dict_list, ocr_obj, img.copy())
    assert ap_bbox == [
        [{"bbox": [1353, 612, 600, 79], "page":1, "confidencePct": 83.25, "scalingFactor": {'internal': {'ver': 1.0, 'hor': 1.0}, 'external': {'ver': 1.0, 'hor': 1.0}}}]]


def test_get_bbox_for_1anc_2():
    reg_def_dict_list = [{"anchorText": ["phone"],
                          "anchorPoint1": {"left": 0, "top": 0, "right": None, "bottom": None},
                          "anchorPoint2": {"left": -1200, "top": None, "right": None, "bottom": 150},
                          "pageDimensions": {
        "width": 2550,
        "height": 3299
    }}]
    ap_bbox, error = thelp.get_bbox_for(
        reg_def_dict_list, ocr_obj, img.copy())
    assert len(ap_bbox) > 0


def test_get_bbox_for_1anc_3():
    reg_def_dict_list = [{"anchorText": ["phone", "\\(AIC.No."],
                          "anchorPoint1": {"left": 0, "top": 0, "right": None, "bottom": None},
                          "anchorPoint2": {"left": None, "top": None, "right": "99%", "bottom": "30%"},
                          "pageDimensions": {
        "width": 2550,
        "height": 3299
    }}]
    ap_bbox, error = thelp.get_bbox_for(
        reg_def_dict_list, ocr_obj, img.copy())
    assert len(ap_bbox) > 0


def test_get_bbox_for_1anc_percentage():
    reg_def_dict_list = [{"anchorText": ["phone"],
                          "anchorPoint1": {"left": 0, "top": "-10%", "right": None, "bottom": None},
                          "anchorPoint2": {"left": None, "top": None, "right": "90%r", "bottom": "2%"},
                          "pageDimensions": {
        "width": 2550,
        "height": 3299
    }}]
    ap_bbox, error = thelp.get_bbox_for(
        reg_def_dict_list, ocr_obj, img.copy())
    assert ap_bbox == [
        [{'bbox': [1275, 551, 1155, 143], 'page':1, "confidencePct": 68.75,
          'scalingFactor': {'internal': {'ver': 1.0, 'hor': 1.0}, 'external': {'ver': 1.0, 'hor': 1.0}}}]]


def test_get_bbox_for_1anc_percentage_1():
    reg_def_dict_list = [{"anchorText": ["phone"],
                          "anchorPoint1": {"left": "-5%r", "top": "-10%", "right": None, "bottom": None},
                          "anchorPoint2": {"left": "90%", "top": None, "right": None, "bottom": "30%"},
                          "pageDimensions": {
        "width": 2550,
        "height": 3299
    }}]
    ap_bbox, error = thelp.get_bbox_for(
        reg_def_dict_list, ocr_obj, img.copy())
    assert ap_bbox == [
        [{"bbox": [1212, 551, 1210, 887], "page":1, "confidencePct": 88.40, "scalingFactor": {'internal': {'ver': 1.0, 'hor': 1.0}, 'external': {'ver': 1.0, 'hor': 1.0}}}]]


def test_get_bbox_for_1anc_percentage_1_1():
    reg_def_dict_list = [{"anchorText": ["phone"],
                          "anchorPoint1": {"left": 0, "top": 0, "right": None, "bottom": None},
                          "anchorPoint2": {"left": "99%", "top": None, "right": None, "bottom": "30%"},
                          "pageDimensions": {
        "width": 2550,
        "height": 3299
    }}]
    ap_bbox, error = thelp.get_bbox_for(
        reg_def_dict_list, ocr_obj, img.copy())
    assert ap_bbox == [
        [{"bbox": [1275, 612, 1262, 826], "page":1, "confidencePct": 88.06, "scalingFactor": {'internal': {'ver': 1.0, 'hor': 1.0}, 'external': {'ver': 1.0, 'hor': 1.0}}}]]


def test_get_bbox_for_1anc_percentage_2():
    reg_def_dict_list = [{"anchorText": ["Number"],
                          "anchorPoint1": {"left": None, "top": 0, "right": 0, "bottom": None},
                          "anchorPoint2": {"left": None, "top": None, "right": "100%", "bottom": "30%"},
                          "pageDimensions": {
        "width": 2550,
        "height": 3299
    }}]
    ap_bbox, error = thelp.get_bbox_for(
        reg_def_dict_list, ocr_obj, img.copy())
    assert ap_bbox == [[{"bbox": [1056, 1093, 1494, 678], "page":1, "confidencePct": 90.81, "scalingFactor": {'internal': {'ver': 1.0, 'hor': 1.0}, 'external': {'ver': 1.0, 'hor': 1.0}}}], [
        {"bbox": [2014, 1093, 536, 678], "page":1, "confidencePct": 82.04, "scalingFactor": {'internal': {'ver': 1.0, 'hor': 1.0}, 'external': {'ver': 1.0, 'hor': 1.0}}}]]


def test_get_bbox_for_1anc_percentage_3():
    reg_def_dict_list = [{"anchorText": ["Number"],
                          "anchorPoint1": {"left": None, "top": "-100%", "right": 0, "bottom": None},
                          "anchorPoint2": {"left": None, "top": None, "right": "100%", "bottom": "30%"},
                          "pageDimensions": {
        "width": 2550,
        "height": 3299
    }}]
    ap_bbox, error = thelp.get_bbox_for(
        reg_def_dict_list, ocr_obj, img.copy())
    assert ap_bbox == [[{"bbox": [1056, 0, 1494, 1771], "page":1, "confidencePct": 88.39, "scalingFactor": {'internal': {'ver': 1.0, 'hor': 1.0}, 'external': {'ver': 1.0, 'hor': 1.0}}}], [
        {"bbox": [2014, 0, 536, 1771], "page":1, "confidencePct": 79.63, "scalingFactor": {'internal': {'ver': 1.0, 'hor': 1.0}, 'external': {'ver': 1.0, 'hor': 1.0}}}]]


def test_get_bbox_for_1anc_percentage_4():
    reg_def_dict_list = [{"anchorText": ["EACH OCCURRENCE"],
                          "anchorPoint1": {"left": None, "top": -9, "right": 0, "bottom": None},
                          "anchorPoint2": {"left": None, "top": None, "right": "70%", "bottom": 5},
                          "pageDimensions": {
        "width": 2550,
        "height": 3299
    }}]
    ap_bbox, error = thelp.get_bbox_for(
        reg_def_dict_list, ocr_obj, img.copy())
    assert len(ap_bbox) == 2


def test_get_bbox_for_2anc():
    reg_def_dict_list = [{"anchorText": ["insurer"],
                          "anchorPoint1": {"left": None, "top": 0, "right": 0, "bottom": None},
                          "pageDimensions": {
        "width": 2550,
        "height": 3299
    }
    },
        {"anchorText": ["insurer b:"],
         "anchorPoint1": {"left": None, "top": 0, "right": "50%", "bottom": None},
         "pageDimensions": {
            "width": 2550,
            "height": 3299
        }
    }]
    ap_bbox, error = thelp.get_bbox_for(
        reg_def_dict_list, ocr_obj, img.copy())
    assert ap_bbox == [[{"bbox": [1374, 823, 602, 42], "page": 1, "confidencePct": 96.0, "scalingFactor": {'internal': {'ver': 1.0, 'hor': 1.0}, 'external': {'ver': 1.0, 'hor': 1.0}}}], [
        {"bbox": [1374, 865, 602, 47], "page":1, "confidencePct": 92.0, "scalingFactor": {'internal': {'ver': 1.0, 'hor': 1.0}, 'external': {'ver': 1.0, 'hor': 1.0}}}]]


def test_get_bbox_for_2anc_1_1():
    reg_def_dict_list = [{"anchorText": ["insurer a:", "insurer b:"],
                          "anchorPoint1": {"left": None, "top": 0, "right": 0, "bottom": None},
                          "pageDimensions": {
        "width": 2550,
        "height": 3299
    }
    },
        {"anchorText": ["insurer c:"],
         "anchorPoint1": {"left": None, "top": 0, "right": "50%", "bottom": None},
         "pageDimensions": {
            "width": 2550,
            "height": 3299
        }
    }]
    ap_bbox, error = thelp.get_bbox_for(
        reg_def_dict_list, ocr_obj, img.copy())
    assert ap_bbox == [
        [{"bbox": [1403, 823, 573, 89], "page":1, "confidencePct":-1, "scalingFactor": {'internal': {'ver': 1.0, 'hor': 1.0}, 'external': {'ver': 1.0, 'hor': 1.0}}}]]


def test_get_bbox_for_2anc_1_2():
    reg_def_dict_list = [{"anchorText": ["insurer"],
                          "anchorPoint1": {"left": None, "top": 0, "right": 0, "bottom": None},
                          "anchorPoint2": {"left": None, "top": None, "right": "15%", "bottom": "5%"},
                          "pageDimensions": {
        "width": 2550,
        "height": 3299
    }
    }]
    ap_bbox, error = thelp.get_bbox_for(
        reg_def_dict_list, ocr_obj, img.copy())
    assert len(ap_bbox) > 4


def test_get_bbox_for_2anc_1():
    reg_def_dict_list = [{"anchorText": ["^PHONE"],
                          "anchorPoint1": {"left": None, "top": 0, "right": 0, "bottom": None},
                          "pageDimensions": {
        "width": 2550,
        "height": 3299
    }
    },
        {"anchorText": ["^E-MAIL"],
         "anchorPoint1": {"left": None, "top": 0, "right": "30%", "bottom": None},
         "pageDimensions": {
            "width": 2550,
            "height": 3299
        }
    }]
    ap_bbox, error = thelp.get_bbox_for(
        reg_def_dict_list, ocr_obj, img.copy())
    assert ap_bbox == [
        [{"bbox": [1353, 612, 361, 70], "page":1, "confidencePct": 89.33, "scalingFactor": {'internal': {'ver': 1.0, 'hor': 1.0}, 'external': {'ver': 1.0, 'hor': 1.0}}}]]


def test_get_bbox_for_2anc_2():
    reg_def_dict_list = [{"anchorText": ["PHONE"],
                          "anchorPoint1": {"left": None, "top": "2%", "right": 0, "bottom": None},
                          "pageDimensions": {
        "width": 2550,
        "height": 3299
    }
    },
        {"anchorText": ["E-MAIL"],
         "anchorPoint1": {"left": None, "top": 0, "right": "30%", "bottom": None},
         "pageDimensions": {
            "width": 2550,
            "height": 3299
        }
    }]
    ap_bbox, error = thelp.get_bbox_for(
        reg_def_dict_list, ocr_obj, img.copy())
    assert ap_bbox == [
        [{"bbox": [1353, 665, 361, 17], "page":1, "confidencePct": -1, "scalingFactor": {'internal': {'ver': 1.0, 'hor': 1.0}, 'external': {'ver': 1.0, 'hor': 1.0}}}]]


def test_get_bbox_for_2anc_2_1():
    reg_def_dict_list = [{"anchorText": ["PHONE"],
                          "pageDimensions":{
        "width": 2550,
        "height": 3299
    }}]
    ap_bbox, error = thelp.get_bbox_for(
        reg_def_dict_list, ocr_obj, img.copy())
    assert ap_bbox == [
        [{"bbox": [1275, 612, 78, 29], "page":1, "confidencePct": 95.0, "scalingFactor": {'internal': {'ver': 1.0, 'hor': 1.0}, 'external': {'ver': 1.0, 'hor': 1.0}}}]]


def test_get_bbox_for_2anc_3():
    reg_def_dict_list = [{"anchorText": ["PHONE"],
                          "anchorPoint1": {"left": None, "top": "2%", "right": "2%", "bottom": None},
                          "pageDimensions": {
        "width": 2550,
        "height": 3299
    }
    },
        {"anchorText": ["E-MAIL"],
         "anchorPoint1": {"left": None, "top": 0, "right": "30%", "bottom": None},
         "pageDimensions": {
            "width": 2550,
            "height": 3299
        }
    }]
    ap_bbox, error = thelp.get_bbox_for(
        reg_def_dict_list, ocr_obj, img.copy())
    assert ap_bbox == [
        [{"bbox": [1376, 665, 338, 17], "page":1, "confidencePct":-1, "scalingFactor": {'internal': {'ver': 1.0, 'hor': 1.0}, 'external': {'ver': 1.0, 'hor': 1.0}}}]]


def test_get_bbox_for_2anc_4():
    reg_def_dict_list = [{"anchorText": ["PHONE"],
                          "anchorPoint1": {"left": None, "top": "2%", "right": "2%", "bottom": None},
                          "anchorPoint2": {},
                          "pageDimensions": {
        "width": 2550,
        "height": 3299
    }
    },
        {"anchorText": ["E-MAIL"],
         "anchorPoint1": {"left": None, "top": 0, "right": "30%", "bottom": None},
         "anchorPoint2": {"left": None, "top": None, "right": None, "bottom": None},
         "pageDimensions": {
            "width": 2550,
            "height": 3299
        }
    }]
    ap_bbox, error = thelp.get_bbox_for(
        reg_def_dict_list, ocr_obj, img.copy())
    assert ap_bbox == [
        [{"bbox": [1376, 665, 338, 17], "page":1, "confidencePct":-1, "scalingFactor": {'internal': {'ver': 1.0, 'hor': 1.0}, 'external': {'ver': 1.0, 'hor': 1.0}}}]]


def test_get_bbox_for_2anc_5():
    reg_def_dict_list = [{"anchorText": ["PHONE"],
                          "anchorPoint1": {"left": None, "top": "2%", "right": "2%", "bottom": None},
                          "anchorPoint2": {},
                          "pageDimensions": {
        "width": 2550,
        "height": 3299
    }
    },
        {"anchorText": ["E-MAIL"],
         "anchorPoint1": {"left": None, "top": 0, "right": "30%", "bottom": None},
         "anchorPoint2": None,
         "pageDimensions": {
            "width": 2550,
            "height": 3299
        }
    }]
    ap_bbox, error = thelp.get_bbox_for(
        reg_def_dict_list, ocr_obj, img.copy())
    assert ap_bbox == [
        [{"bbox": [1376, 665, 338, 17], "page":1, "confidencePct":-1, "scalingFactor": {'internal': {'ver': 1.0, 'hor': 1.0}, 'external': {'ver': 1.0, 'hor': 1.0}}}]]


def test_get_bbox_for_2anc_6():
    reg_def_dict_list = [{"anchorText": ["PHONE"],
                          "anchorPoint1": {"left": None, "top": "2%", "right": "2%", "bottom": None},
                          "anchorPoint2": {},
                          "pageDimensions": {
        "width": 2550,
        "height": 3299
    }
    },
        {"anchorText": ["E-MAIL"],
         "anchorPoint1": {"left": None, "top": None, "right": None, "bottom": None},
         "anchorPoint2": {"left": None, "top": None, "right": None, "bottom": None},
         "pageDimensions": {
            "width": 2550,
            "height": 3299
        }
    }]
    ap_bbox, error = thelp.get_bbox_for(
        reg_def_dict_list, ocr_obj, img.copy())
    assert ap_bbox == [
        [{'bbox': [1281, 665, 95, 17], 'page':1, "confidencePct":-1, 'scalingFactor': {'internal': {'ver': 1.0, 'hor': 1.0}, 'external': {'ver': 1.0, 'hor': 1.0}}}]]


def test_get_bbox_for_2anc_7():
    reg_def_dict_list = [{"anchorText": ["PHONE"],
                          "anchorPoint1": {"left": None, "top": None, "right": None, "bottom": None},
                          "anchorPoint2": {},
                          "pageDimensions": {
        "width": 2550,
        "height": 3299
    }
    },
        {"anchorText": ["E-MAIL"],
         "anchorPoint1": {"left": None, "top": None, "right": None, "bottom": None},
         "anchorPoint2": {"left": None, "top": None, "right": None, "bottom": None},
         "pageDimensions": {
            "width": 2550,
            "height": 3299
        }
    }]
    ap_bbox, error = thelp.get_bbox_for(
        reg_def_dict_list, ocr_obj, img.copy())
    assert ap_bbox == [
        [{'bbox': [1275, 612, 6, 70], 'page':1, "confidencePct":-1, 'scalingFactor': {'internal': {'ver': 1.0, 'hor': 1.0}, 'external': {'ver': 1.0, 'hor': 1.0}}}]]


def test_get_bbox_for_2anc_8():
    reg_def_dict_list = [{"anchorText": ["PHONE"],
                          "anchorPoint1": {"left": None, "top": None, "right": None, "bottom": None},
                          "anchorPoint2": {"left": None, "top": None, "right": None, "bottom": None},
                          "pageDimensions": {
        "width": 2550,
        "height": 3299
    }
    },
        {"anchorText": ["E-MAIL"],
         "anchorPoint1": {"left": None, "top": None, "right": None, "bottom": None},
         "anchorPoint2": {"left": None, "top": None, "right": None, "bottom": None},
         "pageDimensions": {
            "width": 2550,
            "height": 3299
        }
    }]
    ap_bbox, error = thelp.get_bbox_for(
        reg_def_dict_list, ocr_obj, img.copy())
    assert ap_bbox == [
        [{'bbox': [1275, 612, 6, 70], 'page':1, "confidencePct":-1, 'scalingFactor': {'internal': {'ver': 1.0, 'hor': 1.0}, 'external': {'ver': 1.0, 'hor': 1.0}}}]]


def test_get_bbox_for_2anc_9():
    reg_def_dict_list = [{"anchorText": ["LOC"],
                          "anchorPoint1": {"left": None, "top": 0, "right": 0, "bottom": None},
                          "pageDimensions": {
        "width": 2550,
        "height": 3299
    }
    },
        {"anchorText": ["MAY HAVE BEEN"],
         "anchorPoint1": {"left": 0, "top": None, "right": None, "bottom": 0},
         "pageDimensions": {
            "width": 2550,
            "height": 3299
        }
    }]
    ap_bbox, error = thelp.get_bbox_for(
        reg_def_dict_list, ocr_obj, img.copy())
    assert ap_bbox == [
        [{"bbox": [659, 1249, 475, 306], "page":1, "confidencePct":-1, "scalingFactor": {'internal': {'ver': 1.0, 'hor': 1.0}, 'external': {'ver': 1.0, 'hor': 1.0}}}]]


def test_get_bbox_for_2anc_10():
    reg_def_dict_list = [{"anchorText": ["LOC"],
                          "anchorPoint1": {"left": None, "top": 0, "right": 0, "bottom": None},
                          "pageDimensions": {
        "width": 2550,
        "height": 3299
    }
    },
        {"anchorText": ["policy"],
         "anchorPoint1": {"left": 0, "top": None, "right": None, "bottom": 0},
         "pageDimensions": {
            "width": 2550,
            "height": 3299
        }
    }]
    ap_bbox, error = thelp.get_bbox_for(
        reg_def_dict_list, ocr_obj, img.copy())
    assert ap_bbox == [[{"bbox": [651, 2369, 948, 62], "page":1, "confidencePct": 95.32, "scalingFactor": {'internal': {'ver': 1.0, 'hor': 1.0}, 'external': {'ver': 1.0, 'hor': 1.0}}}],
                       [{"bbox": [659, 1555, 1123, 672], "page":1, "confidencePct": 82.33, "scalingFactor": {
                           'internal': {'ver': 1.0, 'hor': 1.0}, 'external': {'ver': 1.0, 'hor': 1.0}}}],
                       [{"bbox": [651, 2227, 1131, 142], "page":1, "confidencePct": -1, "scalingFactor": {
                           'internal': {'ver': 1.0, 'hor': 1.0}, 'external': {'ver': 1.0, 'hor': 1.0}}}],
                       [{"bbox": [276, 1555, 383, 25], "page":1, "confidencePct": 94.0, "scalingFactor": {'internal': {'ver': 1.0, 'hor': 1.0}, 'external': {'ver': 1.0, 'hor': 1.0}}}]]


def test_get_bbox_for_1anc_2_words():
    reg_def_dict_list = [{"anchorText": ["aon risk"],
                          "pageDimensions":{
        "width": 2550,
        "height": 3299
    }
    }]
    ap_bbox, error = thelp.get_bbox_for(
        reg_def_dict_list, ocr_obj, img.copy())
    assert ap_bbox == [
        [{"bbox": [147, 612, 138, 23], "page":1, "confidencePct": 96.0, "scalingFactor": {'internal': {'ver': 1.0, 'hor': 1.0}, 'external': {'ver': 1.0, 'hor': 1.0}}}]]


def test_get_bbox_for_1anc_error_1():
    reg_def_dict_list = [{"anchorText": ["scheduled"],
                          "pageDimensions":{
        "width": 2550,
        "height": 3299
    }
    }]
    ap_bbox, error = thelp.get_bbox_for(
        reg_def_dict_list, ocr_obj, img.copy())
    assert error == "Key: scheduled not found"


def test_get_bbox_for_1anc_error_2():
    reg_def_dict_list = [{"anchorText": ["automobile"],
                          "pageDimensions":{
        "width": 2550,
        "height": 3299
    }
    }]
    ap_bbox, error = thelp.get_bbox_for(
        reg_def_dict_list, ocr_obj, img.copy())
    assert error == "Key: automobile not found"


def test_get_bbox_for_1anc_synonyms():
    reg_def_dict_list = [{"anchorText": [["NON-OWNED", "AUTOS ONLY"]],
                          "pageDimensions":{
        "width": 2550,
        "height": 3299
    }
    }]
    ap_bbox, error = thelp.get_bbox_for(
        reg_def_dict_list, ocr_obj, img.copy())
    assert ap_bbox == [
        [{"bbox": [529, 1844, 146, 17], "page":1, "confidencePct": 96.0, "scalingFactor": {'internal': {'ver': 1.0, 'hor': 1.0}, 'external': {'ver': 1.0, 'hor': 1.0}}}]]


def test_get_bbox_for_occurrence_1():
    """test method"""
    ocr_obj = ocr_parser.OcrParser(
        ocr_doc_list_psm3, data_service_provider=tesseract_ocr_data_obj,
        config_params_dict=config_params_dict_2)

    img = imageio.imread(img_file_path)

    reg_def_dict_list = [{"anchorText": ["INSURER"],
                          "anchorTextMatch":{"occurrenceNums": [2]},
                          "anchorPoint1": {"left": None, "top": '-0.4t', "right": 15, "bottom": None},
                          "anchorPoint2": {"left": None, "top": None, "right": "7t", "bottom": "0.3t"}}]

    ap_bbox, error = thelp.get_bbox_for(
        reg_def_dict_list, ocr_obj, img.copy())

    assert ap_bbox == [
        [{'bbox': [1412, 816, 662, 29], 'page': 1, 'confidencePct': 96.0, 'scalingFactor': {'external': {'ver': 1.0, 'hor': 1.0}, 'internal': {'ver': 3.299, 'hor': 2.55}}}]]


def test_get_bbox_for_occurrence_2():
    """test method"""
    ocr_obj = ocr_parser.OcrParser(
        ocr_doc_list_psm3, data_service_provider=tesseract_ocr_data_obj,
        config_params_dict=config_params_dict_2)

    img = imageio.imread(img_file_path)

    reg_def_dict_list = [{"anchorText": ["INSURER"],
                          "anchorTextMatch":{"occurrenceNums": [2, 4]},
                          "anchorPoint1": {"left": None, "top": '-0.4t', "right": 15, "bottom": None},
                          "anchorPoint2": {"left": None, "top": None, "right": "7t", "bottom": "0.3t"}}]

    ap_bbox, error = thelp.get_bbox_for(
        reg_def_dict_list, ocr_obj, img.copy())

    assert ap_bbox == [[{"bbox": [1412, 816, 662, 29], "page": 1, "confidencePct": 96.0, "scalingFactor": {
        "external": {"ver": 1.0, "hor": 1.0}, "internal": {"ver": 3.299, "hor": 2.55}}}],
        [{"bbox": [1412, 905, 662, 29], "page": 1, "confidencePct": -1, "scalingFactor": {
            "external": {"ver": 1.0, "hor": 1.0}, "internal": {"ver": 3.299, "hor": 2.55}}}]]

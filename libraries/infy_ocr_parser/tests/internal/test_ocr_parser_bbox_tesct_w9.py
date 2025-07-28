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

INFY_SP_ROOT_PATH = os.environ['INFY_SP_ROOT_PATH']
UNIT_TEST_DATA_LOCATION = INFY_SP_ROOT_PATH + \
    "\\workbenchlibraries - Documents\\SHARED_DATA\\unit_test_data\\ocr_parser"
# img_file_path = SHARED_TEMPLATE_LOCATION + \
#     "\\citi-w9-docs\\911-Remediation-W9.jpg"
img_file_path = UNIT_TEST_DATA_LOCATION + \
    "\\citi-w9-docs\\911-Remediation-W9.jpg"
doc_list_psm3 = glob.glob(UNIT_TEST_DATA_LOCATION +
                          "\\citi-w9\\psm3\\911-Remediation-W9.jpg.hocr")

config_params_dict_2 = {'match_method': 'regex', 'similarity_score': 1}

tesseract_ocr_data_obj = TesseractOcrDataServiceProvider()

ocr_obj = ocr_parser.OcrParser(
    doc_list_psm3, tesseract_ocr_data_obj, config_params_dict=config_params_dict_2)
img = imageio.imread(img_file_path)
img_copy = img.copy()


def test_get_bbox_with_1_anc_1():
    reg_def_dict_list = [{"anchorText": ["Check appropriate box"],
                          "anchorPoint1": {"left": -5, "top": -8, "right": None, "bottom": None},
                          "anchorPoint2": {"left": None, "top": None, "right": "70%", "bottom": "5%"}}]
    bbox, error = thelp.get_bbox_for(reg_def_dict_list, ocr_obj, img.copy())
    assert len(bbox) > 0


def test_get_bbox_with_1_anc_2():
    reg_def_dict_list = [{"anchorText": ["Taxpayer identification"],
                          "anchorPoint1": {"left": "-1t", "top": "-1t", "right": None, "bottom": None},
                          "anchorPoint2": {"left": None, "top": None, "right": "1.0000t", "bottom": "1t"}}]
    bbox, error = thelp.get_bbox_for(reg_def_dict_list, ocr_obj, img.copy())
    # anchor text - bbox [639, 2234, 334, 31]
    assert bbox == [[{'bbox': [305, 2201, 1002, 96], 'page': 1, "confidencePct": 95.43, 'scalingFactor': {'external': {'ver': 1.0, 'hor': 1.0}, 'internal': {'ver': 3.229, 'hor': 2.48}}}],
                    [{'bbox': [602, 1426, 945, 90], 'page': 1, "confidencePct": 95.1, 'scalingFactor': {'external': {
                        'ver': 1.0, 'hor': 1.0}, 'internal': {'ver': 3.229, 'hor': 2.48}}}],
                    [{'bbox': [0, 963, 1260, 111], 'page': 1, "confidencePct": 92.67, 'scalingFactor': {'external': {'ver': 1.0, 'hor': 1.0}, 'internal': {'ver': 3.229, 'hor': 2.48}}}]]


def test_get_bbox_with_1_anc_3():
    reg_def_dict_list = [{"anchorText": ["Taxpayer identification"],
                          "anchorPoint1": {"left": "-1.5t", "top": "-1.5t", "right": None, "bottom": None},
                          "anchorPoint2": {"left": None, "top": None, "right": "1.5t", "bottom": "1.5t"}}]
    bbox, error = thelp.get_bbox_for(reg_def_dict_list, ocr_obj, img.copy())
    # anchor text - bbox [639, 2234, 334, 31]
    assert bbox == [[{'bbox': [138, 2185, 1336, 128], 'page': 1, "confidencePct": 94.30, 'scalingFactor': {'external': {'ver': 1.0, 'hor': 1.0}, 'internal': {'ver': 3.229, 'hor': 2.48}}}],
                    [{'bbox': [444, 1411, 1260, 120], 'page': 1, "confidencePct": 95.1, 'scalingFactor': {'external': {
                        'ver': 1.0, 'hor': 1.0}, 'internal': {'ver': 3.229, 'hor': 2.48}}}],
                    [{'bbox': [0, 944, 1478, 148], 'page': 1, "confidencePct": 92.67, 'scalingFactor': {'external': {'ver': 1.0, 'hor': 1.0}, 'internal': {'ver': 3.229, 'hor': 2.48}}}]]


def test_bbox_with_2_anc_without_point_1():
    # when two anchor text provided but not anc-point, then consided left-top as a direction point
    reg_def_dict_list = [{"anchorText": ["Taxpayer identification"]},
                         {"anchorText": ["Taxpayer identification"],
                          "anchorPoint1": {"left": "0", "top": "0", "right": None, "bottom": None}}]  # top value changed from 0.0 to 0
    bbox, error = thelp.get_bbox_for(reg_def_dict_list, ocr_obj, img.copy())
    assert bbox == [[{'bbox': [639, 1456, 278, 777], 'page': 1, "confidencePct": 95.62, 'scalingFactor': {'external': {'ver': 1.0, 'hor': 1.0}, 'internal': {'ver': 3.229, 'hor': 2.48}}}], [
        {'bbox': [390, 1000, 527, 456], 'page': 1, "confidencePct": 95.74, 'scalingFactor': {'external': {'ver': 1.0, 'hor': 1.0}, 'internal': {'ver': 3.229, 'hor': 2.48}}}]]


def test_bbox_with_2_anc_without_point_2():
    # when two anchor text provided but not anc-point, then consided left-top as a anc-point
    reg_def_dict_list = [{"anchorText": ["{{BOD}}"]},
                         {"anchorText": ["Taxpayer identification"],
                          "anchorPoint1": {"left": "0", "top": "0", "right": None, "bottom": None}}]
    bbox, error = thelp.get_bbox_for(reg_def_dict_list, ocr_obj, img.copy())
    assert bbox == [
        [{'bbox': [0, 0, 390, 1000], 'page': 1, "confidencePct": 89.68, 'scalingFactor': {'external': {'ver': 1.0, 'hor': 1.0}, 'internal': {'ver': 3.229, 'hor': 2.48}}}]]


def test_bbox_with_2_anc_without_point_3():
    # when two anchor text provided but not anc-point, then consided left-top as a anc-point
    reg_def_dict_list = [{"anchorText": ["{{EOD}}"]},
                         {"anchorText": ["Taxpayer identification"],
                          "anchorPoint1": {"left": "0", "top": "0",
                                           "right": None, "bottom": None}}]
    bbox, error = thelp.get_bbox_for(reg_def_dict_list, ocr_obj, img.copy())
    assert bbox == [
        [{'bbox': [639, 2233, 1841, 996], 'page': 1, "confidencePct": 95.17, 'scalingFactor': {'external': {'ver': 1.0, 'hor': 1.0}, 'internal': {'ver': 3.229, 'hor': 2.48}}}]]


def test_get_bbox_with_1_anc_excp_1():
    reg_def_dict_list = [{"anchorText": ["Check appropriate box"],
                          "anchorPoint1": {"left": "-5px", "top": "-1t", "right": None, "bottom": None},
                          "anchorPoint2": {"left": None, "top": None, "right": "-70%a", "bottom": "5%r"}}]
    bbox, error = thelp.get_bbox_for(reg_def_dict_list, ocr_obj, img.copy())
    assert bbox == [
        [{'bbox': [293, 557, 1443, 184], 'page': 1, "confidencePct": 85.53, 'scalingFactor': {'external': {'ver': 1.0, 'hor': 1.0}, 'internal': {'ver': 3.229, 'hor': 2.48}}}]]

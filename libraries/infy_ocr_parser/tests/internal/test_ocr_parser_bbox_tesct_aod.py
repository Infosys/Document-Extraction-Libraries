# ===============================================================================================================#
# Copyright 2020 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import pytest
import os
import glob
import imageio
import tests.internal.test_helper as thelp
from infy_ocr_parser import ocr_parser
from shutil import copyfile
from infy_ocr_parser.providers.tesseract_ocr_data_service_provider import TesseractOcrDataServiceProvider
INFY_SP_ROOT_PATH = os.environ['INFY_SP_ROOT_PATH']
UNIT_TEST_DATA_LOCATION = INFY_SP_ROOT_PATH + \
    "\\workbenchlibraries - Documents\\SHARED_DATA\\unit_test_data\\ocr_parser"
# img_file_path = SHARED_TEMPLATE_LOCATION + \
#     "\\art-of-dissolution-general-prior\\Art of Dissolution General Prior - ABC Corporation\\2.jpg"
img_file_path = UNIT_TEST_DATA_LOCATION + \
    "\\art-of-dissolution-general-prior\\Art of Dissolution General Prior - ABC Corporation\\2.jpg"
doc_list_psm3 = glob.glob(UNIT_TEST_DATA_LOCATION +
                          "\\aod\\psm3\\2.jpg.hocr")
config_params_dict_2 = {'match_method': 'regex', 'similarity_score': 1}

tesseract_ocr_data_obj = TesseractOcrDataServiceProvider()
ocr_obj = ocr_parser.OcrParser(
    doc_list_psm3, tesseract_ocr_data_obj, config_params_dict=config_params_dict_2)
img = imageio.imread(img_file_path)
img_copy = img.copy()


def test_get_bbox_with_no_anchor_points_1():
    reg_def_dict_list = [
        {"anchorText": ["450 N. 4th Street", "PO Box 83720"]}]
    bbox, error = thelp.get_bbox_for(reg_def_dict_list, ocr_obj, img.copy())
    assert bbox == [[
        {"bbox": [2997, 6020, 770, 198], "page": 2, "confidencePct": 94.0,
         'scalingFactor': {'external': {'ver': 1.0, 'hor': 1.0}, 'internal': {'ver': 7.7, 'hor': 5.95}}}]]


def test_get_bbox_with_no_anchor_points_2():
    # regex key contains check
    reg_def_dict_list = [
        {"anchorText": ["450 N. 4th Stre", "PO Box 83720"]}]
    ap_bbox, error = thelp.get_bbox_for(
        reg_def_dict_list, ocr_obj, img.copy())
    assert ap_bbox == [
        [{"bbox": [2997, 6020, 770, 198], "page": 2, "confidencePct": 94.0, 'scalingFactor': {'external': {'ver': 1.0, 'hor': 1.0}, 'internal': {'ver': 7.7, 'hor': 5.95}}}]]


def test_get_bbox_with_no_anchor_points_error():
    # regex key ends with 'Stre' check
    reg_def_dict_list = [
        {"anchorText": ["450 N. 4th Stre$", "PO Box 83720"]}]
    ap_bbox, error = thelp.get_bbox_for(
        reg_def_dict_list, ocr_obj, img.copy())
    assert error == "Key: 450 N. 4th Stre$ not found"


def test_get_bbox_with_no_anchor_points_error_1():
    reg_def_dict_list = [
        {"anchorText": ["Stre", "PO Box 83720"]}]
    bbox, error = thelp.get_bbox_for(reg_def_dict_list, ocr_obj, img.copy())
    assert bbox == [
        [{'bbox': [3004, 6020, 763, 198], 'page': 2, "confidencePct": 94.83, 'scalingFactor':  {'external': {'ver': 1.0, 'hor': 1.0}, 'internal': {'ver': 7.7, 'hor': 5.95}}}]]


def test_get_bbox_with_no_anchor_points_error_2():
    reg_def_dict_list = [
        {"anchorText": ["450 N. 4th Street", "Mail or deliver to:"]}]
    bbox, error = thelp.get_bbox_for(reg_def_dict_list, ocr_obj, img.copy())
    assert error == "All the key-list elements are not aligned in the same column"


def test_get_bbox_with_no_anchor_points_error_3():
    reg_def_dict_list = [
        {"anchorText1": ["450 N. 4th Street", "Mail or deliver to:"]}]
    bbox, error = thelp.get_bbox_for(reg_def_dict_list, ocr_obj, img.copy())
    assert bbox == []
    assert error == "Invalid keys found in region_definition: ['anchorText1']."


def test_get_bbox_key_error_1():
    reg_def_dict_list = [
        {"anchorText": [["foo", "poo"]]}]
    _, error = thelp.get_bbox_for(reg_def_dict_list, ocr_obj, img.copy())
    ERROR_EXPECTED = 'No region found with the given keys'
    assert error == ERROR_EXPECTED


def test_get_bbox_key_error_2():
    reg_def_dict_list = [
        {"anchorText": [["foo1", "poo1"], ["foo2", "poo2"]]}]
    _, error = thelp.get_bbox_for(reg_def_dict_list, ocr_obj, img.copy())
    ERROR_EXPECTED = 'No region found with the given keys'
    assert error == ERROR_EXPECTED

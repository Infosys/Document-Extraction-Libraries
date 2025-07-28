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

img_file_path = UNIT_TEST_DATA_LOCATION + \
    "\\Assa Abloy America_19052015240546.jpg"
ocr_doc_list_psm3 = glob.glob(
    UNIT_TEST_DATA_LOCATION+"\\aon\\psm3\\Assa Abloy America_19052015240546.jpg.hocr")
ocr_doc_list_psm11 = glob.glob(
    UNIT_TEST_DATA_LOCATION+"\\aon\\psm11\\Assa Abloy America_19052015240546.jpg.hocr")

tesseract_ocr_data_obj = TesseractOcrDataServiceProvider()
ocr_obj = ocr_parser.OcrParser(
    ocr_doc_list_psm3, data_service_provider=tesseract_ocr_data_obj)
img = imageio.imread(img_file_path)


def test_get_bbox_with_no_anchor_points_1():
    reg_def_dict_list = [{"anchorText": ["E-mail"]}]
    ap_bbox, error = thelp.get_bbox_for(
        reg_def_dict_list, ocr_obj, img.copy())
    assert ap_bbox == [
        [{'bbox': [1281, 682, 75, 17], 'page':1, 'confidencePct': 96.0, "scalingFactor": {'external': {'ver': 1.0, 'hor': 1.0}, 'internal': {'ver': 3.299, 'hor': 2.55}}}]]


def test_get_bbox_with_no_anchor_points_2():
    ocr_obj = ocr_parser.OcrParser(ocr_doc_list_psm11, data_service_provider=tesseract_ocr_data_obj,
                                   config_params_dict={
                                       'match_method': 'normal', 'similarity_score': 0.95})
    reg_def_dict_list = [{"anchorText": ["SCHEDULED", "AUTOS"]}]
    bbox, error = thelp.get_bbox_for(
        reg_def_dict_list, ocr_obj, img.copy())
    assert bbox == [
        [{'bbox': [527, 1761, 139, 44], 'page':1, 'confidencePct': 95.0, "scalingFactor": {'external': {'ver': 1.0, 'hor': 1.0}, 'internal': {'ver': 3.299, 'hor': 2.55}}}]]
    reg_def_dict_list = [{"anchorText": ["NON-OWNED", "AUTOS ONLY"]}]
    bbox, error = thelp.get_bbox_for(reg_def_dict_list, ocr_obj, img.copy())
    assert bbox == [
        [{'bbox': [529, 1817, 146, 44], 'page':1, 'confidencePct': 96.0, "scalingFactor": {'external': {'ver': 1.0, 'hor': 1.0}, 'internal': {'ver': 3.299, 'hor': 2.55}}}]]


def test_get_bbox_with_no_anchor_points_3():
    ocr_obj = ocr_parser.OcrParser(ocr_doc_list_psm11, data_service_provider=tesseract_ocr_data_obj,
                                   config_params_dict={
                                       'match_method': 'normal', 'similarity_score': 0.95})
    reg_def_dict_list = [
        {"anchorText": ["compensation", "liability", "partner"]}]
    bbox, error = thelp.get_bbox_for(
        reg_def_dict_list, ocr_obj, img.copy())
    assert bbox == [
        [{'bbox': [357, 2062, 187, 73], 'page': 1, 'confidencePct': 94.33, "scalingFactor": {'external': {'ver': 1.0, 'hor': 1.0}, 'internal': {'ver': 3.299, 'hor': 2.55}}}]]


def test_get_bbox_with_no_anchor_points_4():
    ocr_obj = ocr_parser.OcrParser(ocr_doc_list_psm11, data_service_provider=tesseract_ocr_data_obj,
                                   config_params_dict={
                                       'match_method': 'normal', 'similarity_score': 0.93})
    reg_def_dict_list = [
        {"anchorText": ["mandatory", "describe", "description"]}]
    bbox, error = thelp.get_bbox_for(
        reg_def_dict_list, ocr_obj, img.copy())
    assert bbox == [
        [{'bbox': [231, 2166, 153, 66], 'page': 1, 'confidencePct': 95.5, "scalingFactor": {'external': {'ver': 1.0, 'hor': 1.0}, 'internal': {'ver': 3.299, 'hor': 2.55}}}]]


def test_get_bbox_with_no_anchor_points_5():
    ocr_obj = ocr_parser.OcrParser(
        ocr_doc_list_psm11, data_service_provider=tesseract_ocr_data_obj)
    reg_def_dict_list = [
        {"anchorText": ["as additional insured in", "policy evidenced", "in accordance with"]}]
    bbox, error = thelp.get_bbox_for(
        reg_def_dict_list, ocr_obj, img.copy())
    assert bbox == [
        [{'bbox': [462, 2403, 765, 80], 'page': 1, 'confidencePct': 95.2, "scalingFactor": {'external': {'ver': 1.0, 'hor': 1.0}, 'internal': {'ver': 3.299, 'hor': 2.55}}}]]


def test_get_bbox_with_no_anchor_points_6():
    ocr_obj = ocr_parser.OcrParser(ocr_doc_list_psm11, data_service_provider=tesseract_ocr_data_obj,
                                   config_params_dict={
                                       'match_method': 'regex', 'similarity_score': 0.95})
    reg_def_dict_list = [
        {"anchorText": ["this certificate is issued", "does not affirmatively", "of insurance does not", "representative or"]}]
    bbox, error = thelp.get_bbox_for(
        reg_def_dict_list, ocr_obj, img.copy())
    assert bbox == [
        [{'bbox': [176, 300, 886, 135], 'page': 1, 'confidencePct': 95.4, "scalingFactor": {'external': {'ver': 1.0, 'hor': 1.0}, 'internal': {'ver': 3.299, 'hor': 2.55}}}]]


def test_get_bbox_with_no_anchor_points_2_synonym():
    ocr_obj = ocr_parser.OcrParser(ocr_doc_list_psm11, data_service_provider=tesseract_ocr_data_obj,
                                   config_params_dict={
                                       'match_method': 'normal', 'similarity_score': 0.93})
    reg_def_dict_list = [
        {"anchorText": [["SCHEDULED", "NON-OWNED"], ["AUTOS", "AUTOS ONLY"]]}]
    bbox, error = thelp.get_bbox_for(
        reg_def_dict_list, ocr_obj, img.copy())
    assert bbox == [[{'bbox': [527, 1761, 139, 44], 'page': 1, 'confidencePct': 95.0, 'scalingFactor':
                      {'external': {'ver': 1.0, 'hor': 1.0}, 'internal': {'ver': 3.299, 'hor': 2.55}}}],
                    [{'bbox': [529, 1817, 146, 44], 'page': 1, 'confidencePct': 96.0, 'scalingFactor':
                      {'external': {'ver': 1.0, 'hor': 1.0}, 'internal': {'ver': 3.299, 'hor': 2.55}}}]]


def test_anchor_text_structure_error_1():
    reg_def_dict_list = [{"anchorText": ["E-mail", ["Phone"]]}]
    ap_bbox, error = thelp.get_bbox_for(
        reg_def_dict_list, ocr_obj, img.copy())
    assert error == "anchorText should either be 1d or 2d array"


def test_anchor_text_structure_error_2():
    reg_def_dict_list = [{"anchorText": [[["Phone"]]]}]
    ap_bbox, error = thelp.get_bbox_for(
        reg_def_dict_list, ocr_obj, img.copy())
    assert error == "anchorText should either be 1d or 2d array"


def test_anchor_text_structure_error_3():
    reg_def_dict_list = [{"anchorText": [["Phone"], ["E-mail", ["Contact"]]]}]
    ap_bbox, error = thelp.get_bbox_for(
        reg_def_dict_list, ocr_obj, img.copy())
    assert error == "anchorText should either be 1d or 2d array"

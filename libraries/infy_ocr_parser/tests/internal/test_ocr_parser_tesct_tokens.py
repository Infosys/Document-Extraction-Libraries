# ===============================================================================================================#
# Copyright 2020 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import os
import glob
import copy
import pytest
from infy_ocr_parser import ocr_parser
from infy_ocr_parser.providers.tesseract_ocr_data_service_provider import TesseractOcrDataServiceProvider
import tests.internal.test_helper as thelp

TEMP_DIR_PATH = './data/temp'

# Create temp directory
if not os.path.exists(TEMP_DIR_PATH):
    os.makedirs(TEMP_DIR_PATH)

INFY_SP_ROOT_PATH = os.environ['INFY_SP_ROOT_PATH']
UNIT_TEST_DATA_LOCATION = INFY_SP_ROOT_PATH + \
    "\\workbenchlibraries - Documents\\SHARED_DATA\\unit_test_data\\ocr_parser"

tesseract_ocr_data_obj = TesseractOcrDataServiceProvider()


def test_get_tokens():
    doc_list_psm3 = glob.glob(
        UNIT_TEST_DATA_LOCATION + "\\aod\\psm3\\1.jpg.hocr")

    ocr_obj = ocr_parser.OcrParser(doc_list_psm3, data_service_provider=tesseract_ocr_data_obj,
                                   config_params_dict={
                                       'match_method': 'regex', 'similarity_score': 1})

    word_tokens = ocr_obj.get_tokens_from_ocr(
        token_type_value=1, pages=[1])
    assert (type(word_tokens) is list)
    # Verify one item from list
    word_tok_1 = [word_tok for word_tok in word_tokens if word_tok["bbox"] == [
        264, 3883, 78, 76]]
    # New Id created everytime hence deleting it
    thelp.__delete_id_from_dict(word_tok_1[0])
    assert (word_tok_1[0] == {
            'bbox': [264, 3883, 78, 76], 'conf': '96', 'page': 1, 'text': '4.', 'scalingFactor':  {'hor': 1, 'ver': 1}})

    phrase_tokens = ocr_obj.get_tokens_from_ocr(
        token_type_value=3)
    assert (type(phrase_tokens) is list)
    # Verify one item from list
    assert (len(phrase_tokens) > 0)

    line_tokens = ocr_obj.get_tokens_from_ocr(
        token_type_value=2)
    assert (type(line_tokens) is list)
    # Verify one item from list
    # New Id created everytime hence deleting it
    thelp.__delete_id_from_dict(line_tokens[18])
    assert (line_tokens[18] == {
            'bbox': [276, 6723, 431, 92], 'page': 1, 'text': 'Signature:', 'scalingFactor': {'hor': 1, 'ver': 1},
            'words': [{
                'bbox': [276, 6723, 431, 92], 'conf': '96', 'page': 1, 'text': 'Signature:', 'scalingFactor': {'hor': 1, 'ver': 1}}]})


def test_get_tokens_2():
    doc_list_psm3 = glob.glob(
        UNIT_TEST_DATA_LOCATION + "\\aod\\psm3\\1.jpg.hocr")
    ocr_obj = ocr_parser.OcrParser(doc_list_psm3, data_service_provider=tesseract_ocr_data_obj,
                                   config_params_dict={
                                       'match_method': 'regex', 'similarity_score': 1})
    word_tokens_2 = ocr_obj.get_tokens_from_ocr(
        token_type_value=1, pages=[1], scaling_factor={'hor': 2, 'ver': 2})
    word_tokens_1 = ocr_obj.get_tokens_from_ocr(
        token_type_value=1, pages=[1], scaling_factor={'hor': 1, 'ver': 1})
    word_tok_1 = [
        word_tok for word_tok in word_tokens_1 if word_tok["text"] == "assets"]
    word_tok_2 = [
        word_tok for word_tok in word_tokens_2 if word_tok["text"] == "assets"]
    wt_bbox_1 = copy.copy(word_tok_1[0]["bbox"])
    wt_bbox_2 = [int(i*2) for i in wt_bbox_1]
    assert (word_tok_2[0]["bbox"] == wt_bbox_2)

    phrase_tokens_2 = ocr_obj.get_tokens_from_ocr(
        token_type_value=3, pages=[1], scaling_factor={'hor': 2, 'ver': 2})
    phrase_tokens_1 = ocr_obj.get_tokens_from_ocr(
        token_type_value=3, pages=[1], scaling_factor={'hor': 1, 'ver': 1})
    phrase_tok_1 = [
        phrase_tok for phrase_tok in phrase_tokens_1 if phrase_tok["text"] == "ARTICLES OF DISSOLUTION"]
    phrase_tok_2 = [
        phrase_tok for phrase_tok in phrase_tokens_2 if phrase_tok["text"] == "ARTICLES OF DISSOLUTION"]
    ph_bbox_2 = [int(i*2) for i in copy.copy(phrase_tok_1[0]["bbox"])]
    assert (phrase_tok_2[0]["bbox"] == ph_bbox_2)

    line_tokens_2 = ocr_obj.get_tokens_from_ocr(
        token_type_value=2, pages=[1], scaling_factor={'hor': 2, 'ver': 2})
    line_tokens_1 = ocr_obj.get_tokens_from_ocr(
        token_type_value=2, pages=[1], scaling_factor={'hor': 1, 'ver': 1})
    line_tok_1 = [
        line_tok for line_tok in line_tokens_1 if line_tok["text"] == "Signature:"]
    line_tok_2 = [
        line_tok for line_tok in line_tokens_2 if line_tok["text"] == "Signature:"]
    # New Id created everytime hence deleting it
    thelp.__delete_id_from_dict(line_tok_1[0])
    thelp.__delete_id_from_dict(line_tok_2[0])
    assert (line_tok_1[0] == {
            'bbox': [276, 6723, 431, 92], 'page': 1, 'text': 'Signature:', 'scalingFactor': {'ver': 1.0, 'hor': 1.0},
            'words': [{
                'bbox': [276, 6723, 431, 92], 'conf': '96', 'page': 1, 'text': 'Signature:', 'scalingFactor': {'ver': 1.0, 'hor': 1.0}}]})
    assert (line_tok_2[0] == {
            'bbox': [552, 13446, 862, 184], 'page': 1, 'text': 'Signature:', 'scalingFactor': {'ver': 2.0, 'hor': 2.0},
            'words': [{
                'bbox': [552, 13446, 862, 184], 'conf': '96', 'page': 1, 'text': 'Signature:', 'scalingFactor': {'ver': 2.0, 'hor': 2.0}}]})


def test_get_phrases_from_words():
    doc_list_psm3 = glob.glob(
        UNIT_TEST_DATA_LOCATION + "\\aod\\psm3\\2.jpg.hocr")
    ocr_obj = ocr_parser.OcrParser(doc_list_psm3, data_service_provider=tesseract_ocr_data_obj,
                                   config_params_dict={
                                       'match_method': 'regex', 'similarity_score': 1})

    phrases_dict_list = ocr_obj.get_tokens_from_ocr(
        3, within_bbox=[2961, 5981, 1253, 417], pages=[2])
    thelp.__delete_id_from_dict(phrases_dict_list[0])
    assert phrases_dict_list[0] == {
        'page': 2, 'text': '450 N. 4th Street', 'bbox': [2997, 6020, 770, 75], 'scalingFactor': {'ver': 1.0, 'hor': 1.0},
        'words': [
            {'page': 2, 'text': '450', 'bbox': [2997, 6021, 165, 74], 'scalingFactor': {
                'ver': 1.0, 'hor': 1.0}, 'conf': '89'},
            {'page': 2, 'text': 'N.', 'bbox': [3202, 6021, 86, 73], 'scalingFactor': {
                'ver': 1.0, 'hor': 1.0}, 'conf': '89'},
            {'page': 2, 'text': '4th', 'bbox': [3326, 6021, 134, 74], 'scalingFactor': {
                'ver': 1.0, 'hor': 1.0}, 'conf': '96'},
            {'page': 2, 'text': 'Street', 'bbox': [3500, 6020, 267, 75], 'scalingFactor': {'ver': 1.0, 'hor': 1.0}, 'conf': '96'}]}
    # != {'bbox': [2997, 6020, 788, 75], 'text': '450 N. 4th Street'}


def test_get_phrases_from_words_exception():
    doc_list_psm3 = glob.glob(
        UNIT_TEST_DATA_LOCATION + "\\aod\\psm3\\2.jpg.hocr")
    ocr_obj = ocr_parser.OcrParser(
        doc_list_psm3, data_service_provider=tesseract_ocr_data_obj)
    with pytest.raises(Exception):
        phrases_dict_list = ocr_obj.get_tokens_from_ocr(3, within_bbox=[2961, 5981, 1253, 417],
                                                        ocr_word_list=[{'bbox': [2997, 6020, 788, 75], 'text': '450 N. 4th Street'}])


def test_different_psm():
    '''
    Page segmentation modes:
    0    Orientation and script detection (OSD) only.
    1    Automatic page segmentation with OSD.
    2    Automatic page segmentation, but no OSD, or OCR.
    3    Fully automatic page segmentation, but no OSD. (Default)
    4    Assume a single column of text of variable sizes.
    5    Assume a single uniform block of vertically aligned text.
    6    Assume a single uniform block of text.
    7    Treat the image as a single text line.
    8    Treat the image as a single word.
    9    Treat the image as a single word in a circle.
    10    Treat the image as a single character.
    11    Sparse text. Find as much text as possible in no particular order.
    12    Sparse text with OSD.
    13    Raw line. Treat the image as a single text line,
                            bypassing hacks that are Tesseract-specific.
    '''
    # change the file path and text to be found in the image
    img_file_path = UNIT_TEST_DATA_LOCATION + \
        "\\Assa Abloy America_19052015240546.jpg"
    match_txt = "SCHEDULED"

    psm_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]
    result = []
    obj_list = []
    for i in psm_list:
        res = {}
        is_found = False
        try:
            ocr_psm_list = glob.glob(UNIT_TEST_DATA_LOCATION+"\\aon\\psm"+str(
                i)+"\\Assa Abloy America_19052015240546.jpg.hocr")
            ocr_obj = ocr_parser.OcrParser(ocr_psm_list, data_service_provider=tesseract_ocr_data_obj,
                                           config_params_dict={
                                               'match_method': 'regex', 'similarity_score': 1})
            # bboxes_text = ocr_obj.get_word_dict_from_ocr()
            bboxes_text = ocr_obj.get_tokens_from_ocr(
                token_type_value=1)
            for b in bboxes_text:
                if (b["text"] == match_txt):
                    is_found = True
                    break
        except Exception as ex:
            print(ex)
            res[f"ex {i}"] = ex

        res[f"psm {i}"] = is_found
        result.append(res)
    print(result)
    assert len(result) > 0


def __delete_file_if_present(file_name):
    '''
    Deletes file if present.

    Parameters:
        file_name (string): Relative or absolute path of the file
    '''
    file_path = file_name
    if not os.path.isabs(file_path):
        file_path = os.path.abspath(file_path)
    if os.path.isfile(file_path):
        print('Deleting file =>' + file_path)
        os.remove(file_path)

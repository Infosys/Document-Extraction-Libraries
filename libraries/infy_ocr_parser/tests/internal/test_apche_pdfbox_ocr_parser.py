# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import os
import glob

import imageio

from infy_ocr_parser import ocr_parser
from infy_ocr_parser.providers.apache_pdfbox_data_service_provider\
    import ApachePdfboxDataServiceProvider
import tests.internal.test_helper as thelp

IMAGE_WIDTH = 2550
IMAGE_HEIGHT = 3299

INFY_SP_ROOT_PATH = os.environ['INFY_SP_ROOT_PATH']
UNIT_TEST_DATA_LOCATION = INFY_SP_ROOT_PATH + \
    "\\workbenchlibraries - Documents\\SHARED_DATA\\unit_test_data\\ocr_parser"
img_file_path = UNIT_TEST_DATA_LOCATION + "\\sop\\1.jpg"

apache_pdfbox_ocr_data_obj = ApachePdfboxDataServiceProvider()


def test_get_tokens():
    """test method"""
    ocr_obj = __create_new_instance()

    word_tokens = ocr_obj.get_tokens_from_ocr(
        token_type_value=1, pages=[1])
    assert isinstance(word_tokens, list)
    assert __validate_bbox([token['bbox'] for token in word_tokens]) is True
    assert len(word_tokens) == 0

    phrase_tokens = ocr_obj.get_tokens_from_ocr(token_type_value=3)
    assert isinstance(phrase_tokens, list)
    assert __validate_bbox([token['bbox'] for token in phrase_tokens]) is True
    assert len(phrase_tokens) == 0

    line_tokens = ocr_obj.get_tokens_from_ocr(token_type_value=2)
    assert isinstance(line_tokens, list)
    assert __validate_bbox([token['bbox'] for token in line_tokens]) is True
    assert len(line_tokens) > 0


def test_apache_pdfbox_plot_bbox():
    """test method 2:
       Plotting bbox and saving bbox plotted image
    """
    plot_image_data_dict = {
        'token_type_value': 2,
        'images': [{
            'image_page_num': 1,
            'image_file_path': img_file_path
        }]
    }
    ocr_obj = __create_new_instance()
    # image_file_path, image_page_num , output_image_file_path should be included

    expected_bbox_file_list = __get_expected_ocr_file_path_list(
        [x['image_file_path'] for x in plot_image_data_dict['images']])
    _ = [__delete_file_if_present(x) for x in expected_bbox_file_list]
    response = ocr_obj.plot(plot_image_data_dict)
    output_img_path = response[0]['output_image_file_path']
    assert os.path.basename(output_img_path) == '1.jpg_bbox.jpg'
    # base_line_image_bbox_path = output_img_path+'_baseline.jpg'
    # assert thelp.validate_file_contents(
    #     base_line_image_bbox_path, output_img_path)


def test_apche_pdfbox_with_anchor_text():
    """test aws api with input image"""
    ocr_obj = __create_new_instance()

    reg_def_dict_list = [{"anchorText": ["STATEMENT OF WORK"],
                          "anchorPoint1": {"left": 0, "top": 0, "right": None, "bottom": None},
                          "anchorPoint2": {"left": None, "top": None, "right": 0, "bottom": 0}}]
    img = imageio.imread(img_file_path)

    ap_bbox, error = thelp.get_bbox_for(
        reg_def_dict_list, ocr_obj, img.copy())
    assert not ap_bbox and error == 'list index out of range'


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


def __create_new_instance():
    config_params_dict = {'match_method': 'regex', 'similarity_score': 1}
    ocr_doc_list = glob.glob(
        UNIT_TEST_DATA_LOCATION+"\\sop\\1.jpg_pdfbox.json")
    ocr_obj = ocr_parser.OcrParser(
        ocr_doc_list, data_service_provider=apache_pdfbox_ocr_data_obj,
        config_params_dict=config_params_dict)

    return ocr_obj


def __get_expected_ocr_file_path_list(doc_file_path_list: list):
    expected_file_path_list = []
    for doc_file_path in doc_file_path_list:
        expected_file_path = doc_file_path + "_bbox.jpg"
        expected_file_path_list.append(expected_file_path)
    return expected_file_path_list


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

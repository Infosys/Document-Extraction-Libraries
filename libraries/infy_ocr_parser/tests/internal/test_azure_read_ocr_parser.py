# ===============================================================================================================#
# Copyright 2020 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import os
import imageio
import tests.internal.test_helper as thelp
from infy_ocr_parser import ocr_parser
from infy_ocr_parser.providers.azure_read_ocr_data_service_provider import AzureReadOcrDataServiceProvider

# start: config section
INFY_SP_ROOT_PATH = os.environ['INFY_SP_ROOT_PATH']
UNIT_TEST_DATA_LOCATION = INFY_SP_ROOT_PATH + \
    "\\workbenchlibraries - Documents\\SHARED_DATA\\unit_test_data\\ocr_parser"
img_file_path = UNIT_TEST_DATA_LOCATION + \
    "\\Assa Abloy America_19052015240546.jpg"
config_params_dict_2 = {'match_method': 'regex', 'similarity_score': 1}
# end: config section

# start: init
azure_service_provider_obj = AzureReadOcrDataServiceProvider()

img = imageio.imread(img_file_path)
# end: init


def test_get_bbox_for_1anc_synonyms():
    """test azure read api with input image"""
    ocr_doc_list = [UNIT_TEST_DATA_LOCATION +
                    "\\aon\\azure\\Assa Abloy America_19052015240546.jpg_azure_read.json"]
    ocr_obj = ocr_parser.OcrParser(ocr_doc_list, config_params_dict=config_params_dict_2,
                                   data_service_provider=azure_service_provider_obj)

    reg_def_dict_list = [{"anchorText": [["NON-OWNED", "AUTOS ONLY"]]
                          }]
    ap_bbox, _ = thelp.get_bbox_for(
        reg_def_dict_list, ocr_obj, img.copy())
    assert ap_bbox == [[{'bbox': [528, 1815, 140, 20], 'page': 1, 'confidencePct': 99.4,
                         'scalingFactor': {'external': {'ver': 1.0, 'hor': 1.0}, 'internal': {'ver': 3.299, 'hor': 2.55}}}],
                       [{'bbox': [276, 1798, 142, 21], 'page': 1, 'confidencePct': 98.95,
                         'scalingFactor': {'external': {'ver': 1.0, 'hor': 1.0}, 'internal': {'ver': 3.299, 'hor': 2.55}}}],
                       [{'bbox': [529, 1842, 143, 21], 'page': 1, 'confidencePct': 99.35,
                         'scalingFactor': {'external': {'ver': 1.0, 'hor': 1.0}, 'internal': {'ver': 3.299, 'hor': 2.55}}}]]


def test_get_bbox_for_1anc_synonyms_2():
    """test azure read api with input pdf"""
    # TODO Code chnage by Raj.
    ocr_doc_list_1 = [UNIT_TEST_DATA_LOCATION +
                      "\\aon\\azure\\Assa Abloy America_19052015240546.pdf[1-2]_azure_read.json"]

    ocr_obj = ocr_parser.OcrParser(ocr_doc_list_1, config_params_dict=config_params_dict_2,
                                   data_service_provider=azure_service_provider_obj)

    reg_def_dict_list = [{"anchorText": [["NON-OWNED", "AUTOS ONLY"]]
                          }]
    ap_bbox, _ = thelp.get_bbox_for(
        reg_def_dict_list, ocr_obj, img.copy())
    # bbox value returned as per the PDF dimension in OCR file
    assert ap_bbox == [[{'bbox': [170, 581, 46, 5], 'page': 1, 'confidencePct': 100.0, 'scalingFactor': {'external': {'ver': 1.0, 'hor': 1.0}, 'internal': {'ver': 1.056, 'hor': 0.816}}}],
                       [{'bbox': [88, 576, 47, 5], 'page': 1, 'confidencePct': 100.0, 'scalingFactor': {'external': {
                           'ver': 1.0, 'hor': 1.0}, 'internal': {'ver': 1.056, 'hor': 0.816}}}],
                       [{'bbox': [169, 590, 47, 5], 'page': 1, 'confidencePct': 100.0, 'scalingFactor': {'external': {'ver': 1.0, 'hor': 1.0}, 'internal': {'ver': 1.056, 'hor': 0.816}}}]]


def test_get_tokens_within_bbox():
    """test azure read api with input pdf"""
    ocr_doc_list_1 = [UNIT_TEST_DATA_LOCATION +
                      "\\aon\\azure\\Assa Abloy America_19052015240546.jpg_azure_read.json"]

    ocr_obj = ocr_parser.OcrParser(ocr_doc_list_1, config_params_dict=config_params_dict_2,
                                   data_service_provider=azure_service_provider_obj)

    phrases_dict_list = ocr_obj.get_tokens_from_ocr(
        3, within_bbox=[500, 200, 1500, 100], pages=[1])
    # print(json.dumps(phrases_dict_list, indent=4))
    print(phrases_dict_list)
    assert (phrases_dict_list[0]['text'] ==
            "CERTIFICATE OF LIABILITY INSURANCE")


def test_get_bbox_for_1anc_synonyms_multipage_1():
    """test azure read api with input pdf"""
    mulpage_ocr_doc_list = [UNIT_TEST_DATA_LOCATION + "\\general\\multipage\\1.jpg_azure_ocr.json",
                            UNIT_TEST_DATA_LOCATION + "\\general\\multipage\\2.jpg_azure_ocr.json"]

    ocr_obj = ocr_parser.OcrParser(mulpage_ocr_doc_list, config_params_dict=config_params_dict_2,
                                   data_service_provider=azure_service_provider_obj)

    reg_def_dict_list = [{"anchorText": [["NON-OWNED", "AUTOS ONLY"]]}]
    ap_bbox, _ = thelp.get_bbox_for(
        reg_def_dict_list, ocr_obj, img.copy())
    assert ap_bbox == [
        [{'bbox': [528, 1815, 140, 20], 'page': 1, 'confidencePct': 99.4,
          'scalingFactor': {'external': {'ver': 1.0, 'hor': 1.0}, 'internal': {'ver': 3.299, 'hor': 2.55}}}],
        [{'bbox': [528, 1815, 140, 20], 'page': 2, 'confidencePct': 99.4,
          'scalingFactor': {'external': {'ver': 1.0, 'hor': 1.0}, 'internal': {'ver': 3.299, 'hor': 2.55}}}],
        [{'bbox': [276, 1798, 142, 21], 'page': 1, 'confidencePct': 98.95,
          'scalingFactor': {'external': {'ver': 1.0, 'hor': 1.0}, 'internal': {'ver': 3.299, 'hor': 2.55}}}],
        [{'bbox': [276, 1798, 142, 21], 'page': 2, 'confidencePct': 98.95,
          'scalingFactor': {'external': {'ver': 1.0, 'hor': 1.0}, 'internal': {'ver': 3.299, 'hor': 2.55}}}],
        [{'bbox': [529, 1842, 143, 21], 'page': 1, 'confidencePct': 99.35,
          'scalingFactor': {'external': {'ver': 1.0, 'hor': 1.0}, 'internal': {'ver': 3.299, 'hor': 2.55}}}],
        [{'bbox': [529, 1842, 143, 21], 'page': 2, 'confidencePct': 99.35,
          'scalingFactor': {'external': {'ver': 1.0, 'hor': 1.0}, 'internal': {'ver': 3.299, 'hor': 2.55}}}]]

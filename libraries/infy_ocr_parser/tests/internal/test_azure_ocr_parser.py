# ===============================================================================================================#
# Copyright 2020 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import os
import imageio
import tests.internal.test_helper as thelp
from infy_ocr_parser import ocr_parser
from infy_ocr_parser.providers.azure_ocr_data_service_provider import AzureOcrDataServiceProvider

# start: config section
INFY_SP_ROOT_PATH = os.environ['INFY_SP_ROOT_PATH']
UNIT_TEST_DATA_LOCATION = INFY_SP_ROOT_PATH + \
    "\\workbenchlibraries - Documents\\SHARED_DATA\\unit_test_data\\ocr_parser"
img_file_path = UNIT_TEST_DATA_LOCATION + \
    "\\Assa Abloy America_19052015240546.jpg"
ocr_doc_list = [UNIT_TEST_DATA_LOCATION +
                "\\aon\\azure\\Assa Abloy America_19052015240546.jpg_azure_ocr.json"]
config_params_dict_2 = {'match_method': 'regex', 'similarity_score': 1}
# end: config section

# start: init
azure_service_provider_obj = AzureOcrDataServiceProvider()
img = imageio.imread(img_file_path)
# end: init


def test_get_bbox_for_1anc_synonyms():
    """test azure read api with input image"""
    ocr_obj = ocr_parser.OcrParser(ocr_doc_list, config_params_dict=config_params_dict_2,
                                   data_service_provider=azure_service_provider_obj)

    reg_def_dict_list = [{"anchorText": [["NON-OWNED", "AUTOS ONLY"]]
                          }]
    ap_bbox, _ = thelp.get_bbox_for(
        reg_def_dict_list, ocr_obj, img.copy())
    assert ap_bbox == [[{'bbox': [530, 1816, 146, 18], 'page': 1, 'confidencePct':-1,
                         'scalingFactor': {'external': {'ver': 1.0, 'hor': 1.0}, 'internal': {'ver': 3.299, 'hor': 2.55}}}],
                       [{'bbox': [275, 1800, 147, 18], 'page': 1, 'confidencePct':-1,
                         'scalingFactor': {'external': {'ver': 1.0, 'hor': 1.0}, 'internal': {'ver': 3.299, 'hor': 2.55}}}],
                       [{'bbox': [528, 1843, 147, 18], 'page': 1, 'confidencePct':-1,
                         'scalingFactor': {'external': {'ver': 1.0, 'hor': 1.0}, 'internal': {'ver': 3.299, 'hor': 2.55}}}]]

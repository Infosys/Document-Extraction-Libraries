# ===============================================================================================================#
#
# Copyright 2021 Infosys Ltd.
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at
# http://www.apache.org/licenses/
#
# ===============================================================================================================#

import os
from infy_ocr_generator.ocr_generator import OcrGenerator
from infy_ocr_generator.providers.azure_ocr_data_service_provider import AzureOcrDataServiceProvider


def test_azure_ocr_generator():
    """AZURE OCR test method"""
    # Enable this to run for AZURE
    CONFIG_PARAMS_DICT = {
        'azure': {
            'computer_vision': {
                'subscription_key': '<Enter your subscription key>',
                'api_ocr': {
                    'url': 'https://southeastasia.api.cognitive.microsoft.com/vision/v3.1/ocr',
                }
            }
        }
    }
    azure_service_provider_obj = AzureOcrDataServiceProvider(
        config_params_dict=CONFIG_PARAMS_DICT)
    ocr_generator_obj = OcrGenerator(
        data_service_provider=azure_service_provider_obj)
    image_file_path = os.path.abspath('./data/sample_1.png')

    ocr_result_list = ocr_generator_obj.generate(
        doc_data_list=[{
            "doc_path": image_file_path, "pages": '1'}])
    assert os.path.exists(ocr_result_list[0]['output_doc'])

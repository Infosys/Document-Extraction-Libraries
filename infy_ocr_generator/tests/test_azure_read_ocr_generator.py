# ===============================================================================================================#
#
# Copyright 2021 Infosys Ltd.
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at
# http://www.apache.org/licenses/
#
# ===============================================================================================================#

import os
import time
from infy_ocr_generator.ocr_generator import OcrGenerator
from infy_ocr_generator.providers.azure_read_ocr_data_service_provider import \
    AzureReadOcrDataServiceProvider


def test_azure_read_ocr_generator():
    """AZURE OCR test method"""
    CONFIG_PARAMS_DICT = {
        'azure': {
            'computer_vision': {
                'subscription_key': '<Enter your subscription key>',
                'api_read': {
                    'url': '<Enter the branch URL>'
                }
            }
        }
    }

    image_file_path = os.path.abspath('./data/sample_1.png')
    doc_data_list = [{"doc_path": image_file_path, "pages": "1"}]

    azure_read_provider_obj = AzureReadOcrDataServiceProvider(
        config_params_dict=CONFIG_PARAMS_DICT
    )
    ocr_generator_obj = OcrGenerator(
        data_service_provider=azure_read_provider_obj)

    submit_req_result = ocr_generator_obj.submit_request(doc_data_list)
    time.sleep(6)
    re_res_result = ocr_generator_obj.receive_response(
        submit_req_result)
    ocr_result_list = ocr_generator_obj.generate(
        api_response_list=re_res_result
    )

    assert os.path.exists(ocr_result_list[0]['output_doc'])

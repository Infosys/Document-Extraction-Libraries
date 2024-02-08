# ===============================================================================================================#
#
# Copyright 2023 Infosys Ltd.
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at
# http://www.apache.org/licenses/
#
# ===============================================================================================================#

import os
import time
from infy_ocr_generator.ocr_generator import OcrGenerator
from infy_ocr_generator.providers.azure_form_recognizer_ocr_data_service_provider import AzureFormRecognizerOcrDataServiceProvider

CONFIG_PARAMS_DICT = {
    'azure_form_recognizer': {
        'key': '<Enter your subscription key>',
        'endpoint': '<Enter the branch URL>'
    }
}


def test_azure_form_recognizer_ocr_generator():
    """Azure Form Recognizer OCR test method"""
    image_file_path = os.path.abspath('./data/sample_1.png')
    doc_data_list = [{"doc_path": image_file_path, "pages": "1"}]

    azure_form_recognizer_provider_obj = AzureFormRecognizerOcrDataServiceProvider(
        config_params_dict=CONFIG_PARAMS_DICT
    )
    ocr_generator_obj = OcrGenerator(
        data_service_provider=azure_form_recognizer_provider_obj)

    submit_req_result = ocr_generator_obj.submit_request(doc_data_list)
    time.sleep(7)

    re_res_result = ocr_generator_obj.receive_response(
        submit_req_result)

    ocr_result_list = ocr_generator_obj.generate(
        api_response_list=re_res_result
    )

    assert os.path.exists(ocr_result_list[0]['output_doc'])

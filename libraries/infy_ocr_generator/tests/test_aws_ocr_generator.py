# ===============================================================================================================#
# Copyright 2021 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import os
import time
import pytest
from infy_ocr_generator.ocr_generator import OcrGenerator
from infy_ocr_generator.providers.aws_detect_doc_txt_ocr_data_service_provider \
    import AwsDetectDocumentTextDataServiceProvider

CONFIG_PARAMS_DICT = {
    'aws': {
        'region_name': '<Enter your region name>',
        'aws_access_key_id': '<Enter your access key>',
        'aws_secret_access_key': '<Enter your secret access key>'
    }
}


@pytest.mark.skip(reason="Please uncomment when software is available")
def test_aws_ocr_generator():
    """AWS DETECTDOCUMENTTEXT OCR test method"""
    image_file_path = os.path.abspath('./data/sample_1.png')
    doc_data_list = [{"doc_path": image_file_path, "pages": "1"}]

    aws_detect_document_text_provider_obj = AwsDetectDocumentTextDataServiceProvider(
        config_params_dict=CONFIG_PARAMS_DICT
    )
    ocr_generator_obj = OcrGenerator(
        data_service_provider=aws_detect_document_text_provider_obj)

    submit_req_result = ocr_generator_obj.submit_request(doc_data_list)
    time.sleep(7)

    re_res_result = ocr_generator_obj.receive_response(
        submit_req_result)

    ocr_result_list = ocr_generator_obj.generate(
        api_response_list=re_res_result
    )

    assert os.path.exists(ocr_result_list[0]['output_doc'])

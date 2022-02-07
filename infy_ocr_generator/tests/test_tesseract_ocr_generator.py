# ===============================================================================================================#
#
# Copyright 2021 Infosys Ltd.
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at
# http://www.apache.org/licenses/
#
# ===============================================================================================================#
import os
import logging
from infy_ocr_generator.ocr_generator import OcrGenerator
from infy_ocr_generator.providers.tesseract_ocr_data_service_provider import TesseractOcrDataServiceProvider


def test_tesseract_ocr_generator():
    """Test method"""
    # Logging configuration
    if not os.path.exists("./logs"):
        os.makedirs("./logs")
    logging.basicConfig(filename=("./logs" + "/app_log.log"),
                        format="%(asctime)s- %(levelname)s- %(message)s", level=logging.INFO,
                        datefmt="%d-%b-%y %H:%M:%S",)
    logger = logging.getLogger()
    logger.info('Initialization Completed')

    CONFIG_PARAMS_DICT = {
        "tesseract": {
            "pytesseract_path": os.environ['PYTESSERACT_PATH']
        }
    }
    output_path = './data'

    tesseract_ocr_provider = TesseractOcrDataServiceProvider(
        config_params_dict=CONFIG_PARAMS_DICT,
        logger=logger,
        output_dir=output_path
    )

    ocr_generator_obj = OcrGenerator(
        data_service_provider=tesseract_ocr_provider)
    img_file_path = './data/sample_1.png'

    ocr_result_list = ocr_generator_obj.generate(
        doc_data_list=[{'doc_path': img_file_path, 'pages': '1'}]
    )

    assert os.path.exists(ocr_result_list[0]['output_doc'])


def test_tesseract_not_found_error():
    """Test method"""
    try:
        CONFIG_PARAMS_DICT = {
            "tesseract": {
                "pytesseract_path": " "
            }
        }
        output_path = './data'
        TesseractOcrDataServiceProvider(
            config_params_dict=CONFIG_PARAMS_DICT,
            output_dir=output_path
        )

    except Exception as ex:
        assert ex.__class__.__name__ == 'TesseractNotFoundError'

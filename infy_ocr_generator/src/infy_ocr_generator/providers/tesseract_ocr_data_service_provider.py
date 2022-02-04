# ===============================================================================================================#
#
# Copyright 2021 Infosys Ltd.
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at
# http://www.apache.org/licenses/
#
# ===============================================================================================================#

import os
import traceback
import logging
import copy
import imageio
import pytesseract
from infy_ocr_generator.interface.data_service_provider_interface import (
    GENERATE_API_RES_STRUCTURE, DataServiceProviderInterface,
    DOC_DATA)


class OcrConstants():
    """Constant class"""
    MAX_INT16 = 32767


CONFIG_PARAMS_DICT = {
    'tesseract': {
        'pytesseract_path': '',
        'psm': 3,
    }
}


class TesseractOcrDataServiceProvider(DataServiceProviderInterface):
    """Implementation of DataServiceProvider for Tesseract 5"""

    def __init__(self, config_params_dict: CONFIG_PARAMS_DICT,
                 output_dir: str = None,
                 output_to_supporting_folder: bool = False,
                 overwrite: bool = False,
                 logger: logging.Logger = None,
                 log_level: int = None):
        """Creates an instance of Tesseract Ocr Data Service Provider

        Args:
            config_params_dict (CONFIG_PARAMS_DICT): Provider CONFIG values.
            output_dir (str, optional): Directory to generate OCR file,
                if not given will generate into same file location. Defaults to None.
            output_to_supporting_folder (bool, optional): If True, OCR file will be generated to
                same file location but into supporting folder named `* _files`. Defaults to False.
            overwrite (bool, optional): If True, existing OCR file will be overwritten. Defaults to False.
            logger (logging.Logger, optional): logger object. Defaults to None.
            log_level (int, optional):log level. Defaults to None.

        Raises:
            FileNotFoundError: Raises an error if the file is not found.
        """
        super(TesseractOcrDataServiceProvider,
              self).__init__(logger, log_level)
        self.config_params_dict = self.get_updated_config_dict(
            config_params_dict['tesseract'], CONFIG_PARAMS_DICT['tesseract'])
        if output_dir and not os.path.exists(output_dir):
            raise FileNotFoundError(f"{output_dir} not found")
        self.output_dir = output_dir
        self.output_to_supporting_folder = output_to_supporting_folder
        self.overwrite = overwrite

        if self.config_params_dict["pytesseract_path"]:
            pytesseract.pytesseract.tesseract_cmd = self.config_params_dict["pytesseract_path"]
        # This will validate and throw error if tesseract not configured properly
        tesseract_version = pytesseract.get_tesseract_version()
        self.logger.info("Tesseract version = %s", tesseract_version)

    def submit_request(self, doc_data_list: [DOC_DATA]) -> list:
        """API to submit tesseract ocr data service request for asynchorouns call

        Args:
            doc_data_list ([DOC_DATA]): List of input documents. e.g, ['c:/1.jpg','c:/1.pdf']

        Raises:
            NotImplementedError: Raises an error if the method is not implemented

        Returns:
            list: [SUB_RE_API_STRUCTURE]
        """
        raise NotImplementedError

    def receive_response(self, submit_req_response_list: list, rerun_unsucceeded_mode: bool = False) -> list:
        """API of tesseract ocr data service to Received response of asynchorouns call submit request.

        Args:
            submit_req_response_list (list): Response structure of `submit_request` api
            rerun_unsucceeded_mode (bool, optional): Enabling this mode and passing same request
             -will rerun for unsuccessful call. Defaults to False.

        Raises:
            NotImplementedError: Raises an error if the method is not implemented.

        Returns:
            list: [SUB_RE_API_STRUCTURE]
        """
        raise NotImplementedError

    def generate(self, doc_data_list: [DOC_DATA] = None, api_response_list: list = None) -> list:
        """API to generate OCR based on OCR provider given

        Args:
            doc_data_list ([DOC_DATA], optional): Use these input files to
                -implement technique and generate output files. Defaults to None.
            api_response_list (list, optional): API response will be generated into output file. Defaults to None.

        Returns:
            list: List of generated ocr file path.
        """
        def _call_tesseract(in_doc_obj):
            gen_res_dict = copy.deepcopy(GENERATE_API_RES_STRUCTURE)
            img_file = in_doc_obj['doc_path']
            gen_res_dict['input_doc'] = img_file
            _image = imageio.imread(img_file)

            if (_image.shape[0] > OcrConstants.MAX_INT16 or _image.shape[1] > OcrConstants.MAX_INT16):
                gen_res_dict['error'] = ("Image too large: ({},{}). The max width and"
                                         "height of image size should be ({},{})".
                                         format(_image.shape[1], _image.shape[0],
                                                OcrConstants.MAX_INT16, OcrConstants.MAX_INT16))
                return gen_res_dict

            output_doc = self.get_output_file(
                img_file, self.output_dir, self.output_to_supporting_folder,
                suffix='.hocr')

            gen_res_dict['output_doc'] = output_doc
            if not self.overwrite and os.path.exists(output_doc):
                return gen_res_dict

            ocr_data = pytesseract.image_to_pdf_or_hocr(
                img_file, extension='hocr', config='--psm '+str(self.config_params_dict['psm']))
            ocr_data = ocr_data.decode('utf-8').strip()
            ocr_data = ocr_data.replace(
                "id='page_1'", f"id='page_{in_doc_obj['pages']}'")
            ocr_data = ocr_data.encode('utf-8').strip()
            with open(output_doc, "wb") as f:
                f.write(ocr_data)
            return gen_res_dict

        if len(doc_data_list) == 0:
            raise Exception("Valid doc_data_list arg is required")
        ocr_list = []

        for in_doc_obj in doc_data_list:
            try:
                ocr_list.append(_call_tesseract(in_doc_obj))
            except Exception:
                full_trace_error = traceback.format_exc()
                self.logger.error(full_trace_error)

        return ocr_list

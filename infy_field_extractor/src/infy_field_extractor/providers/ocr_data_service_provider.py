# ===============================================================================================================#
# Copyright 2021 Infosys Ltd.
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at
# http://www.apache.org/licenses/                                                  #
# ===============================================================================================================#


import logging
import numpy as np
from infy_ocr_parser import ocr_parser
from infy_field_extractor.interface.data_service_provider_interface import DataServiceProviderInterface, \
    FILE_DATA_LIST, ADDITIONAL_INFO, GET_TOKENS_OUTPUT, TEXT_MATCH_METHOD, BBOX, GET_BBOX_FOR_OUTPUT, TEXT


class OcrDataServiceProvider(DataServiceProviderInterface):
    """Tesseract Data Service Provider"""

    def __init__(self, ocr_parser_object: ocr_parser.OcrParser,
                 logger: logging.Logger = None, log_level: int = None):
        """Creates a Tesseract Data Service Provider

        Args:
            ocr_parser_object (ocr_parser.OcrParser): ocr parser
            logger (logging.Logger, optional): Logger object. Defaults to None.
            log_level (int, optional): Logging Level. Defaults to None.

        Raises:
            Exception: Raises an error if property ocr_parser_object not found
            Exception: Raises an error if ocr_parser_object is invalid
        """
        super(OcrDataServiceProvider, self).__init__(logger, log_level)
        # validate ocr_parser_object
        self.ocr_parser_object = ocr_parser_object
        if ocr_parser_object is None:
            raise Exception("property ocr_parser_object not found")
        elif not isinstance(ocr_parser_object, ocr_parser.OcrParser):
            raise Exception("Provide valid ocr_parser_object")

    def get_tokens(
            self, token_type_value: int, img: np.array, text_bbox: BBOX,
            file_data_list: FILE_DATA_LIST = None,
            additional_info: ADDITIONAL_INFO = None,
            temp_folderpath: str = None) -> GET_TOKENS_OUTPUT:
        """Method to return the text from the
            image from the text_bbox as a list of dictionary.

        Args:
            token_type_value (int): Type of text to be returned.
            img (np.array): Read image as np array of the original image.
            text_bbox (BBOX): Text bbox
            file_data_list (FILE_DATA_LIST, optional): List of all file datas.
                Each file data has the path to supporting document and page numbers, if applicable.
                When multiple files are passed, provider has to pick the right file
                based on the image dimensions or type of file extension.
                Defaults to None.
            additional_info (ADDITIONAL_INFO, optional): Additional info. Defaults to None.
            temp_folderpath (str, optional): Path to temp folder. Defaults to None.

        Returns:
            GET_TOKENS_OUTPUT: list of dict containing text and its bbox.
        """

        pages = additional_info['pages']
        scaling_factor = additional_info['scaling_factor']
        ocr_word_list = additional_info.get('word_bbox_list')
        if token_type_value == 1:
            bboxes_text = self.ocr_parser_object.get_tokens_from_ocr(
                token_type_value=1, within_bbox=text_bbox, pages=pages, scaling_factor=scaling_factor)
        elif token_type_value == 3:
            if ocr_word_list is None:
                bboxes_text = self.ocr_parser_object.get_tokens_from_ocr(
                    token_type_value=3, within_bbox=text_bbox, pages=pages, scaling_factor=scaling_factor)
            else:
                bboxes_text = self.ocr_parser_object.get_tokens_from_ocr(
                    token_type_value=3, ocr_word_list=ocr_word_list,
                    pages=pages, scaling_factor=scaling_factor)

        return bboxes_text

    def get_bbox_for(self, img: np.array, text: TEXT,
                     text_match_method: TEXT_MATCH_METHOD,
                     file_data_list: FILE_DATA_LIST = None,
                     additional_info: ADDITIONAL_INFO = None,
                     temp_folderpath: str = None) -> GET_BBOX_FOR_OUTPUT:
        """Method to return the text from the
        image from the text_bbox as a list of dictionary.

        Args:
            img (np.array): Read image as np array of the original images
            text (TEXT): Text
            text_match_method (TEXT_MATCH_METHOD): Method (`normal` or `regex`) used to match the text.
            file_data_list (FILE_DATA_LIST, optional): List of all file datas. Each file data has the path to
                supporting document and page numbers, if applicable.
                When multiple files are passed, provider has to pick the right file
                based on the image dimensions or type of file extension. Defaults to None.
            additional_info (ADDITIONAL_INFO, optional): Additional info. Defaults to None.
            temp_folderpath (str, optional): Path to temp folder. Defaults to None.

        Returns:
            BBOX: list of dict containing text and its bbox.
        """

        return self.ocr_parser_object.get_bbox_for(
            [
                {"anchorText": text,
                 "anchorTextMatch": text_match_method,
                 "pageNum": additional_info['pages']}
            ],
            scaling_factor=additional_info['scaling_factor'])

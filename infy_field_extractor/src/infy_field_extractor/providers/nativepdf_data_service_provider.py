# ===============================================================================================================#
# Copyright 2021 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import logging
import os
import numpy as np
from infy_common_utils.format_converter import ConvertAction
import infy_common_utils.format_converter as format_converter
from infy_field_extractor.interface.data_service_provider_interface import DataServiceProviderInterface, \
    FILE_DATA_LIST, ADDITIONAL_INFO, GET_TOKENS_OUTPUT, TEXT_MATCH_METHOD, BBOX, TEXT, GET_BBOX_FOR_OUTPUT


class NativePdfDataServiceProvider(DataServiceProviderInterface):
    """Native pdf Data Service Provider"""

    def __init__(self, logger: logging.Logger = None, log_level: int = None):
        """Creates an instance of Native pdf Data Service Provider.

        Args:
            logger (logging.Logger, optional): Logger object. Defaults to None.
            log_level (int, optional): Logging Level. Defaults to None.
        """
        super(NativePdfDataServiceProvider, self).__init__(logger, log_level)
        format_converter.format_converter_jar_home = os.environ['FORMAT_CONVERTER_HOME']
        self.logger.info("Initialized successfully")

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
                based on the image dimensions or type of file extension. Defaults to None.
            additional_info (ADDITIONAL_INFO, optional): Additional info. Defaults to None.
            temp_folderpath (str, optional): Path to temp folder. Defaults to None.

        Raises:
            Exception: Raises an error if the method is not implemented

        Returns:
            GET_TOKENS_OUTPUT: list of dict containing text and its bbox.
        """
        if not file_data_list:
            raise Exception("Please provide file_data_list")
        pdf_data = self._get_pdf_data(file_data_list)
        pages = [pdf_data['pages'][0]]
        config_param_dict = {
            "pages": pages,
            "bboxes": [text_bbox],
            "page_dimension": {"width": img.shape[1], "height": img.shape[0]}}
        convert_action = ConvertAction.PDF_TO_JSON
        output = format_converter.FormatConverter.execute(
            pdf_data['path'], convert_action, config_param_dict)

        return output[0][0]['regions']

    def get_bbox_for(self, img: np.array, text: TEXT,
                     text_match_method: TEXT_MATCH_METHOD,
                     file_data_list: FILE_DATA_LIST = None,
                     additional_info: ADDITIONAL_INFO = None,
                     temp_folderpath: str = None) -> GET_BBOX_FOR_OUTPUT:
        """Method to return the text from the
            image from the text_bbox as a list of dictionary.

        Args:
            img (np.array): Read image as np array of the original image.
            text (TEXT): Text
            text_match_method (TEXT_MATCH_METHOD): Method (`normal` or `regex`) used to match the text.
            file_data_list (FILE_DATA_LIST, optional): List of all file datas. Each file data
                has the path to supporting document and page numbers, if applicable.
                When multiple files are passed, provider has to pick the right file
                based on the image dimensions or type of file extension.. Defaults to None.
            additional_info (ADDITIONAL_INFO, optional):  Additional info. Defaults to None.
            temp_folderpath (str, optional): Path to temp folder. Defaults to None.

        Raises:
            NotImplementedError: Raises an error if the method is not implemented

        Returns:
            BBOX: list of dict containing text and its bbox.
        """
        raise NotImplementedError

    def _get_pdf_data(self, file_data_list):
        for file_data in file_data_list:
            if file_data['path']:
                if file_data['path'].lower().endswith('pdf'):
                    return file_data
        raise Exception("Pdf file not found")

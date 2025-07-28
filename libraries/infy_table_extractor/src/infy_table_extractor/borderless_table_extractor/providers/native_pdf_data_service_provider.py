# ===============================================================================================================#
# Copyright 2020 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import os

import cv2
import infy_common_utils.format_converter as format_converter
from infy_table_extractor.borderless_table_extractor.interface.data_service_provider_interface import \
    DataServiceProviderInterface


class NativePdfDataServiceProvider(DataServiceProviderInterface):
    """Data Service Provider to extract from NativePdf document."""

    def __init__(self, logger=None, log_level=None):
        """Creates an instance of NativePdfDataServiceProvider

        Args:
            logger (logging.Logger, optional): Logger object. Defaults to None.
            log_level (int, optional): Logging Level. Defaults to None.
        Example:
            >>> import logging
            >>> logging.disable(logging.CRITICAL)
            >>> provider = NativePdfDataServiceProvider()
            >>> isinstance(provider, NativePdfDataServiceProvider)
            True
            >>> logging.disable(logging.NOTSET)
        """
        super(NativePdfDataServiceProvider, self).__init__(logger, log_level)
        format_converter.format_converter_jar_home = os.environ['FORMAT_CONVERTER_HOME']
        self.logger.info("Initialized successfully")

    def get_enhanced_tokens(self, token_data_list: list,
                            image_file_path: str = None,
                            within_bbox: list = None,
                            file_data_list: list = None,) -> list:
        """Uses FormatConverter (wrapper to `java pdfbox` tool) to extract text based on token's bbox
        and then enhances it.

        Args:
            token_data_list (list): List of token data with bounding boxes.
            image_file_path (str, optional): Path to the image file. Defaults to None.
            within_bbox (list, optional): Bounding box within which to extract tokens. Defaults to None.
            file_data_list (list, optional): List of file data. Each file data has the path to supporting document and page numbers, if applicable. Defaults to None.

        Returns:
            list: Enhanced token data list.

        Raises:
            FileNotFoundError: If no PDF file is found in 'file_data_list'.
        Example:
            >>> import logging
            >>> logging.disable(logging.CRITICAL)
            >>> provider = NativePdfDataServiceProvider()
            >>> token_data_list = [{'bbox': [0, 0, 100, 100], 'text': ''}]
            >>> image_file_path = './data/samples/infosys_q1-2022.pdf_files/1.jpg'
            >>> file_data_list = [{'path': './data/samples/infosys_q1-2022.pdf', 'pages': [1]}]
            >>> result = provider.get_enhanced_tokens(token_data_list, image_file_path, file_data_list=file_data_list)
            >>> isinstance(result, list)
            True
            >>> logging.disable(logging.NOTSET)
        """
        im_h, im_w = cv2.imread(image_file_path).shape[:2]
        pdf_file_list = None
        if file_data_list:
            pdf_file_list = [pdf_file_data for pdf_file_data in file_data_list if pdf_file_data["path"] and str(
                pdf_file_data["path"]).lower().endswith(".pdf")]
        if not pdf_file_list:
            raise FileNotFoundError("PDF file not found in 'file_data_list'")
        page_bboxes = []
        for item in token_data_list:
            startx, starty, endx, endy = item['bbox']
            startx = startx-20
            width = endx - startx
            height = endy - starty
            page_bboxes.append([startx, starty, width, height])

        config_param_dict = {
            "pages": pdf_file_list[0]['pages'],
            "bboxes": page_bboxes,
            "page_dimension": {"width": im_w, "height": im_h}
        }
        # PDF_TO_JSON
        extracted_fields, std_err = format_converter.FormatConverter.execute(
            pdf_file_list[0]["path"],
            convert_action=format_converter.ConvertAction.PDF_TO_JSON,
            config_param_dict=config_param_dict
        )

        if not std_err and extracted_fields:
            for region_data in extracted_fields[0]['regions']:
                new_value = region_data['text']
                if new_value != "":
                    startx, starty, width, height = region_data['bbox']
                    startx = startx+20
                    endx = width + startx
                    endy = height + starty
                    for item in token_data_list:
                        if item['bbox'] == [startx, starty, endx, endy]:
                            item['text'] = new_value
                            break
        return token_data_list

    def get_tokens(self, image_file_path: str,
                   token_type_value: int,
                   file_data_list: list = None,
                   additional_info: dict = None,
                   config_params_dict: dict = None) -> list:
        """Method to get all tokens (word, phrase or line) and its bounding box as x, y, width and height from an image as a list of dictionary.
        Currently word token is only required.

        Args:
            image_file_path (str): Path to the image file.
            token_type_value (int): 1(WORD), 2(LINE), 3(PHRASE)
            file_data_list (list, optional): List of all file data. Each file data has the path to supporting document and page numbers, if applicable. Defaults to None.
            additional_info (dict, optional): Additional information for token extraction. Defaults to None.
            config_params_dict (dict, optional): Configuration parameters. Defaults to None.

        Raises:
            NotImplementedError: Raises an error if the method is not implemented
        Example:
            >>> import logging
            >>> logging.disable(logging.CRITICAL)
            >>> provider = NativePdfDataServiceProvider()
            >>> provider.get_tokens('sample.jpg', 1)
            Traceback (most recent call last):
            ...
            NotImplementedError
            >>> logging.disable(logging.NOTSET)
        """
        raise NotImplementedError

    def get_rows_cols(self, image_file_path: str,
                      token_type_value: int,
                      file_data_list: list = None,
                      additional_info: dict = None,
                      config_params_dict: dict = None) -> dict:
        """Method to get rows and columns from an image.

        Args:
            image_file_path (str): Path to the image file.
            token_type_value (int): 1(WORD), 2(LINE), 3(PHRASE)
            file_data_list (list, optional): List of all file data. Each file data has the path to supporting document and page numbers, if applicable. Defaults to None.
            additional_info (dict, optional): Additional information for row and column extraction. Defaults to None.
            config_params_dict (dict, optional): Configuration parameters. Defaults to None.

        Raises:
            NotImplementedError: Raises an error if the method is not implemented
        Example:
            >>> import logging
            >>> logging.disable(logging.CRITICAL)
            >>> provider = NativePdfDataServiceProvider()
            >>> provider.get_rows_cols('sample.jpg', 1)
            Traceback (most recent call last):
            ...
            NotImplementedError
            >>> logging.disable(logging.NOTSET)
        """
        raise NotImplementedError

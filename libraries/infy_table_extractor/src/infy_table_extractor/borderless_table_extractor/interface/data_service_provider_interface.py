# ===============================================================================================================#
# Copyright 2020 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import abc
import logging
import sys

FILE_DATA = {
    'path': '',
    'pages': []
}

CONFIG_PARAMS_DICT = ADDITIONAL_INFO = {
    'tesseract': {
        'psm': ''
    }
}

TOKEN_DATA = GET_TOKENS_OUTPUT = GET_ENHANCED_TOKENS_OUTPUT = {
    'text': '',
    'bbox': []
}

ROWS_COLS_OUTPUT = {
    'rows': [{'bbox': []}],
    'cols': [{'bbox': []}]
}


class DataServiceProviderInterface(metaclass=abc.ABCMeta):
    """Data Service Provider Interface"""
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'get_tokens') and
                callable(subclass.get_tokens) and
                hasattr(subclass, 'get_enhanced_tokens') and
                callable(subclass.get_enhanced_tokens) and
                hasattr(subclass, 'detect_hv_line_from_tokens') and
                callable(subclass.detect_hv_line_from_tokens) or
                NotImplemented)

    def __init__(self, logger: logging.Logger = None, log_level: int = None):
        self.__set_logger(logger, log_level)

    @abc.abstractmethod
    def get_tokens(self, image_file_path: str,
                   token_type_value: int,
                   within_bbox: list = None,
                   file_data_list: [FILE_DATA] = None,
                   additional_info: ADDITIONAL_INFO = None,
                   config_params_dict: CONFIG_PARAMS_DICT = None) -> [GET_TOKENS_OUTPUT]:
        """Return the tokens extracted from ocr file as per the expected `token_type_value`.

        Args:
            image_file_path (str): Full file path of the image file.
                -To detect horizontal and vertical lines.
                -To detect tokens.
            token_type_value (int): 1 (words), 2 (lines)
                -1 - Return list of all words and its bbox value contain dict.
                -2 - Return list of all lines and its bbox value contain dict.
            file_data_list ([FILE_DATA], optional): Supporting files. Defaults to None.
                Each file data has the path to supporting document and page numbers, if applicable.
                When multiple files are passed, provider has to pick the right file
                -based on the image dimensions or type of file extension.
            additional_info (ADDITIONAL_INFO, optional):
                Dictionary contains additional info about actual input provided. Defaults to None.
                For examples, `{'tesseract':'psm':''}` is about the *.hocr file psm of
                -input provided in `file_data_list`.
            config_params_dict (CONFIG_PARAMS_DICT, optional):
                Dictionary contains info about expected token returns as per psm. Defaults to None.

        Raises:
            NotImplementedError: Error raised when calling the unimplemented method of provider.

        Returns:
            [GET_TOKENS_OUTPUT]: Return expected `token_type_value` tokens
             -in the structure of `[{'text': '','bbox': []}]`
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_enhanced_tokens(self, token_data_list: [TOKEN_DATA],
                            image_file_path: str = None,
                            within_bbox: list = None,
                            file_data_list: [FILE_DATA] = None) -> [GET_ENHANCED_TOKENS_OUTPUT]:
        """Return the enhanced tokens of given `tokens`.
         -For example, Tokens from OCR may not be 100% accurate when extracting all text from full page of document.
         -So provider can use this method to enhance each text based on its's bbox position.

        Args:
            tokens ([TOKEN]): List of tokens contains `[{'text':'','bbox':''}]`.
             -It can be the token type of word or line.
            image_file_path (str, optional): Full file path of the image file. Defaults to None.
            file_data_list ([FILE_DATA], optional): Supporting files. Defaults to None.
                Each file data has the path to supporting document and page numbers, if applicable.
                When multiple files are passed, provider has to pick the right file
                -based on the image dimensions or type of file extension.

        Raises:
            NotImplementedError: Error raised when calling the unimplemented method of provider.

        Returns:
            [GET_ENHANCED_TOKENS_OUTPUT]: Enhance and Return the tokens in the structure of `[{'text': '','bbox': []}]`
        """
        raise NotImplementedError

    # line detect from ocr not from image
    @abc.abstractmethod
    def get_rows_cols(self, image_file_path: str,
                      token_type_value: int,
                      within_bbox: list = None,
                      file_data_list: [FILE_DATA] = None,
                      additional_info: ADDITIONAL_INFO = None,
                      config_params_dict: CONFIG_PARAMS_DICT = None) -> ROWS_COLS_OUTPUT:
        """Return the line's bbox of horizontal and vertical detected from ocr as per expected `token_type_value`.

        Args:
            image_file_path (str): Full file path of the image file.
                -To detect horizontal and vertical lines.
                -To detect tokens.
            token_type_value (int): 1 (words), 2 (lines)
                -1 - Return list of all words and its bbox value contain dict.
                -2 - Return list of all lines and its bbox value contain dict.
            file_data_list ([FILE_DATA], optional): Supporting files. Defaults to None.
                Each file data has the path to supporting document and page numbers, if applicable.
                When multiple files are passed, provider has to pick the right file
                -based on the image dimensions or type of file extension.
            additional_info (ADDITIONAL_INFO, optional): Defaults to None.
                Dictionary contains additional info about actual input provided.
                For examples, `{'tesseract':'psm':''}` is about the *.hocr file psm
                 -of input provided in `file_data_list`.
            config_params_dict (CONFIG_PARAMS_DICT, optional):
                Dictionary contains info about expected token returns as per psm. Defaults to None.

        Raises:
            NotImplementedError: Error raised when calling the unimplemented method of provider.

        Returns:
            ROWS_COLS_OUTPUT: Return the dictionary value of ocr detected rows and columns
             -in structure of `{'rows': [{'bbox':[]}],'cols': [{'bbox':[]}]}`
        """
        raise NotImplementedError

    def __set_logger(self, logger, log_level):
        self.logger = logger
        LOG_FORMAT = logging.Formatter(
            '%(asctime)s.%(msecs)03d %(levelname)s [%(threadName)s] [%(module)s] [%(funcName)s:%(lineno)d] %(message)s')
        if logger is None:
            log_level = logging.INFO if log_level is None else log_level
            self.logger = logging.getLogger(__name__)
            self.logger.setLevel(log_level)
            # Add sysout hander
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(log_level)
            console_handler.setFormatter(LOG_FORMAT)
            self.logger.addHandler(console_handler)
            self.logger.info('log initialized')
        else:
            hndlr = self.logger.handlers[0]
            hndlr.setFormatter(LOG_FORMAT)
            self.logger.info('Formatter updated')

# ===============================================================================================================#
# Copyright 2021 Infosys Ltd.
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at
# http://www.apache.org/licenses/                                                  #
# ===============================================================================================================#

import abc
import logging
import sys
import numpy as np


FILE_DATA_LIST = [
    {
        'path': str,
        'pages': list
    }
]


ADDITIONAL_INFO = {
    'scaling_factor': {
        'hor': 1,
        'ver': 1
    },
    'pages': list
}


GET_TOKENS_OUTPUT = [
    {
        'text': str,
        'bbox': list
    }
]


TEXT_MATCH_METHOD = {
    'method': str,
    'similarityScore': float,
    'maxWordSpace': str
}

GET_BBOX_FOR_OUTPUT = [
    {
        'text': str,
        'bbox': list
    }
]

BBOX = [0, 0, 0, 0]
TEXT = ['']


class DataServiceProviderInterface(metaclass=abc.ABCMeta):
    """Interface for Data Service Provider"""
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'generate') and
                callable(subclass.generate) or
                NotImplemented)

    def __init__(self, logger: logging.Logger = None, log_level: int = None):
        """Creates an instance of Data Service Provider.

        Args:
            logger (logging.Logger, optional): Logger object. Defaults to None.
            log_level (int, optional): Logging Level. Defaults to None.
        """
        self.__set_logger(logger, log_level)

    @abc.abstractmethod
    def get_tokens(self, token_type_value: int,
                   img: np.array, text_bbox: BBOX,
                   file_data_list: FILE_DATA_LIST = None,
                   additional_info: ADDITIONAL_INFO = None,
                   temp_folderpath: str = None) -> GET_TOKENS_OUTPUT:
        """Abstract method to be implemented to return data(text and its bbox)
        of token_type_value as a list of dictionary.

        Args:
            token_type_value (int): Type of text to be returned. 1(WORD), 2(LINE), 3(PHRASE)
            img (np.array): Read image as np array of the original image.
            text_bbox (list): Text bbox
            file_data_list (FILE_DATA_LIST, optional): List of all file datas. Each file data has
                the path to supporting document and page numbers, if applicable.
                When multiple files are passed, provider has to pick the right file
                based on the image dimensions or type of file extension.
                Defaults to None.
            additional_info (ADDITIONAL_INFO, optional): Additional info. Defaults to None.
                Dictionary contains info like scaling_factor and pages.
            temp_folderpath (str, optional): Path to temp folder. Defaults to None.

        Raises:
            NotImplementedError: Raises an error if the method is not implemented

        Returns:
            GET_TOKENS_OUTPUT: list of dict containing text and its bbox.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_bbox_for(self, img: np.array, text: TEXT,
                     text_match_method: TEXT_MATCH_METHOD,
                     file_data_list: FILE_DATA_LIST = None,
                     additional_info: ADDITIONAL_INFO = None,
                     temp_folderpath: str = None) -> GET_BBOX_FOR_OUTPUT:
        """Abstract method to be implemented to return the bbox for a text in the
        given image as a list of dictionary.

        Args:
            img (np.array): Read image as np array of the original image.
            text(TEXT): Text to search for in the image.
            text_match_method(TEXT_MATCH_METHOD): Method (`normal` or `regex`) used to match the text.
            file_data_list (FILE_DATA_LIST, optional): List of all file datas. Each file data
                has the path to supporting document and page numbers, if applicable.
                When multiple files are passed, provider has to pick the right file
                based on the image dimensions or type of file extension.
                Defaults to None.
            additional_info (ADDITIONAL_INFO, optional): Additional info. Defaults to None.
                Dictionary contains info like scaling_factor and pages.
            temp_folderpath (str, optional): Path to temp folder. Defaults to None.

        Raises:
            NotImplementedError: Raises an error if the method is not implemented

        Returns:
            BBOX: list of dict containing text and its bbox.
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

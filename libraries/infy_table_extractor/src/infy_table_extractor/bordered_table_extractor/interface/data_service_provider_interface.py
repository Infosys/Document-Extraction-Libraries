# ===============================================================================================================#
# Copyright 2021 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import abc
import logging
import sys
import numpy as np


FILE_DATA = {
    'path': '',
    'pages': []
}

IMG_CELL_BBOX = {
    'cell_id': '',
    'cell_bbox': []
}

ADDITIONAL_INFO = {
    'cell_info': [
        {
            'cell_id': '',
            'cell_img_path': '',
            'cell_bbox': [],
            'cell_img': np.array

        }
    ]
}

GET_TEXT_OUTPUT = {
    'cell_id': '',
    'cell_text': '',
    'cell_bbox': []
}

GET_TOKENS_OUTPUT = {
    'text': '',
    'bbox': [],
    'conf': int
}


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
                   img: np.array,
                   file_data_list: [FILE_DATA] = None) -> [GET_TOKENS_OUTPUT]:
        """Abstract method to be implemented to get all tokens (word, phrase or line) and its 
            bounding box as x, y, width and height from an image as a list of dictionary.
            Currently word token is only required.

        Args:
            token_type_value (int): 1(WORD), 2(LINE), 3(PHRASE)
            img (np.array): Read image as np array of the original image.
            file_data_list (FILE_DATA, optional): List of all file datas. Each file data has
                the path to supporting document and page numbers, if applicable.
                When multiple files are passed, provider has to pick the right file based 
                on the image dimensions or type of file extension.
                Defaults to None.

        Raises:
            NotImplementedError: Raises an error if the method is not implemented

        Returns:
            [GET_TOKENS_OUTPUT]: list of dict containing text and its bbox.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_text(self, img: np.array, img_cell_bbox_list: [IMG_CELL_BBOX],
                 file_data_list: [FILE_DATA] = None,
                 additional_info: ADDITIONAL_INFO = None,
                 temp_folderpath: str = None) -> [GET_TEXT_OUTPUT]:
        """Abstract method to be implemented to return the text from the list of
        cell images or bbox of the original image as a list of dictionary.
        (Eg. [{'cell_id': str,'cell_text':'{{extracted_text}}', 'cell_bbox':[x, y, w, h]}]

        Args:
            img (np.array): Read image as np array of the original image.
            img_cell_bbox_list ([IMG_CELL_BBOX]): List of all cell bbox
            file_data_list ([FILE_DATA], optional): List of all file datas. Each file data
                has the path to supporting document and page numbers, if applicable.
                Defaults to None.
            additional_info (ADDITIONAL_INFO, optional): Additional info. Defaults to None.
            temp_folderpath (str, optional): Path to temp folder. Defaults to None.

        Raises:
            NotImplementedError: Raises an error if the method is not implemented

        Returns:
            [GET_TEXT_OUTPUT]: list of dict containing text and its bbox.
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

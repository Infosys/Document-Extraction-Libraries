# ===============================================================================================================#
# Copyright 2021 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import abc
import logging
import sys


class DataServiceProviderInterface(metaclass=abc.ABCMeta):
    """Provider Interface Class"""
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'get_word_dict_from') and
                callable(subclass.get_word_dict_from) and
                hasattr(subclass, 'get_line_dict_from') and
                callable(subclass.get_line_dict_from) and
                hasattr(subclass, 'get_page_bbox_dict') and
                callable(subclass.get_page_bbox_dict) or
                NotImplemented)

    def __init__(self, logger: logging.Logger = None, log_level: int = None):
        """Creates an instance of Provider Interface

        Args:
            logger (logging.Logger, optional): logger object. Defaults to None.
            log_level (int, optional): log level. Defaults to None.
        """
        self.__set_logger(logger, log_level)

    @abc.abstractmethod
    def init_provider_inputs(self, doc_list: list):
        """Method used to load the list input ocr files to given provider.

        Args:
            doc_list (list): OCR file list

        Raises:
            NotImplementedError: Raises an error if the method is not implemented
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_line_dict_from(self, pages: list = None,
                           line_dict_list: list = None, scaling_factors: list = None) -> list:
        """Returns list of line dictionary containing text and bbox values.

        Args:
            pages (list, optional): Page to filter from given `doc_list`. Defaults to None.
            line_dict_list (list, optional):  Existing line dictonary to filter certain page(s).
                - Defaults to None.
            scaling_factors (list, optional): value to scale up/down the bbox. First element is for
                vertical scaling factor and second is for horizontal scaling factor.
                - Defaults to [1.0, 1.0]

        Raises:
            NotImplementedError: Raises an error if the method is not implemented.

        Returns:
            list: List of line dictionary containing the text, words and respective bbox values.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_word_dict_from(self, pages: list = None,
                           word_dict_list: list = None, scaling_factors: list = None) -> list:
        """Returns list of word dictionary containing text and bbox values.

        Args:
            pages (list, optional): Page to filter from given `doc_list`. Defaults to None.
            word_dict_list (list, optional): Existing word dictonary to filter certain page(s).
                - Defaults to None.
            scaling_factors (list, optional): value to scale up/down the bbox. First element is for
                vertical scaling factor and second is for horizontal scaling factor.
                - Defaults to [1.0, 1.0]

        Raises:
            NotImplementedError: Raises an error if the method is not implemented.

        Returns:
            list: List of word dictionary containing the text, bbox and conf values.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_page_bbox_dict(self) -> list:
        """Returns pages wise bbox list

        Raises:
            NotImplementedError: Raises an error if the method is not implemented

        Returns:
            list: List of dictionary containing page num and its bbox values.
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

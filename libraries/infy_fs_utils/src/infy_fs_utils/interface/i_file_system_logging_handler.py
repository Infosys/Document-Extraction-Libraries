# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

"""Module containing IFileSystemLoggingHandler class"""

from abc import abstractmethod
import logging
from ..data import LoggingConfigData
from ..interface import IFileSystemHandler


class IFileSystemLoggingHandler(logging.Handler):
    """Interface for abstracting file system logging operations."""

    def __init__(self, logging_config_data: LoggingConfigData, file_sys_handler: IFileSystemHandler):
        super().__init__()
        __logging_config_data = logging_config_data.copy()
        if not __logging_config_data.logger_group_name:
            __logging_config_data.logger_group_name = __name__
        self.__logging_config_data = __logging_config_data
        # Create logger object and store at class level
        self.__logger = logging.getLogger(
            self.__logging_config_data.logger_group_name)
        self.__file_sys_handler = file_sys_handler

    def set_handler(self):
        """Set handler"""
        self.get_logger().addHandler(self)

    def unset_handler(self):
        """Unset handler"""
        self.get_logger().removeHandler(self)

    @abstractmethod
    def emit(self, record):
        """Logs a record"""
        raise NotImplementedError

    def get_logger(self) -> logging.Logger:
        """Returns an instance of logger object"""
        return self.__logger

    def get_logging_config_data(self) -> LoggingConfigData:
        """Returns an instance of LoggingConfigData"""
        return self.__logging_config_data

    def get_file_system_handler(self) -> IFileSystemHandler:
        """Returns an instance of IFileSystemHandler"""
        return self.__file_sys_handler

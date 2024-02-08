# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

"""Module containing FileSystemLoggingHandler class"""

import logging

from infy_dpp_core.common.file_system_manager import FileSystemManager


class FileSystemLoggingHandler(logging.Handler):
    """Class for logging handler based on FileSystemHandler"""

    def __init__(self, log_file_path):
        logging.Handler.__init__(self=self)
        self.__log_file_path = log_file_path
        self.__file_sys_handler = FileSystemManager().get_file_system_handler()

    def emit(self, record):
        msg = self.format(record) + '\n'
        # print('emit()', msg)
        self.__file_sys_handler.append_file(
            self.__log_file_path, msg)

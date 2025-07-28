# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

"""Module containing LoggerFactory"""

import logging
import sys
import socket
from infy_content_generator.common.singleton import Singleton
from infy_content_generator.common.app_config_manager import AppConfigManager

class LoggerFactory(metaclass=Singleton):
    """Factory class to get singleton logger object at application level"""

    __LOG_FORMAT = '%(asctime)s.%(msecs)03d %(levelname)s [%(threadName)s] '
    __LOG_FORMAT += '[%(module)s] [%(funcName)s:%(lineno)d] %(message)s'
    __TIMESTAMP_FORMAT = '%Y-%m-%d %H:%M:%S'

    def __init__(self):
        self.__app_config = AppConfigManager().get_app_config()
        # self.__file_sys_handler = infy_fs_utils.manager.FileSystemManager().get_fs_handler()
        log_level = int(self.__app_config['STORAGE']['logging_level'])
        log_to_console = self.__app_config['STORAGE']['log_to_console'] == 'true'
        # log_to_file = self.__app_config['STORAGE']['log_to_file'] == 'true'

        formatter = logging.Formatter(
            self.__LOG_FORMAT, datefmt=self.__TIMESTAMP_FORMAT)

        # Create logger object and store at class level
        self.__logger = logging.getLogger(__name__)
        # Set level at overall level
        self.__logger.setLevel(log_level)

        # Add sysout hander
        if log_to_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(formatter)
            self.__logger.addHandler(console_handler)

        # Add File System Logging Handlder
        # if log_to_file:
        #     log_file_path = self.__get_log_file_path()
        #     file_system_logging_handler = FileSystemLoggingHandler(
        #         log_file_path)
        #     file_system_logging_handler.setFormatter(formatter)
        #     self.__logger.addHandler(file_system_logging_handler)

        # NullHandler to avoid any low level library issue when Console handler also turned off.
        handler = logging.NullHandler()
        self.__logger.addHandler(handler)

        self.__logger.info("Logging module initialized")
        self.__logger.info("HOSTNAME : %s", socket.gethostname())

    def get_logger(self):
        """Returns an instance of logger object"""
        return self.__logger

    # def __get_log_file_path(self):
    #     log_file_path = os.getenv("GEN_AI_SDK_LOG_FILE_PATH", None)
    #     if not log_file_path:
    #         log_dir_path = self.__app_config['STORAGE']['log_dir_path']
    #         log_file_prefix = self.__app_config['STORAGE']['log_file_prefix']
    #         timestr = time.strftime("%Y%m%d")
    #         log_file_name = f'{log_file_prefix}{socket.gethostname()}_{timestr}.log'
    #         log_file_path = log_dir_path+'//'+log_file_name

    #     # Create parent folders of logfile if doesn't exist
    #     log_dir_path = os.path.dirname(log_file_path)
    #     self.__file_sys_handler.create_folders(log_dir_path)

    #    return log_file_path

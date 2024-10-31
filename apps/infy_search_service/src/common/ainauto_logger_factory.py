# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#
import logging
import time
import sys
import socket
from common.file_util import FileUtil
from common.singleton import Singleton
from common.app_config_manager import AppConfigManager

app_config = AppConfigManager().get_app_config()


class AinautoLoggerFactory(metaclass=Singleton):
    __LOG_FORMAT = '%(asctime)s.%(msecs)03d %(levelname)s [%(threadName)s] [%(module)s] [%(funcName)s:%(lineno)d] %(message)s'

    def __init__(self):
        log_file_path = app_config['DEFAULT']['log_file_path']
        log_file_prefix = app_config['DEFAULT']['log_file_prefix']
        log_level = int(app_config['DEFAULT']['logging_level'])
        if app_config['DEFAULT']['log_to_console'] == 'false':
            log_to_console = False
        else:
            log_to_console = True

        FileUtil.create_dirs_if_absent(log_file_path)

        timestr = time.strftime("%Y%m%d")
        log_file_name = f'{log_file_prefix}{socket.gethostname()}_{timestr}.log'

        logging.basicConfig(filename=(log_file_path+'//'+log_file_name),
                            format=self.__LOG_FORMAT,
                            level=log_level,
                            datefmt='%Y-%m-%d %H:%M:%S')

        # Create logger object and store at class level
        self.__logger = logging.getLogger(__name__)

        # Add sysout hander
        if log_to_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(log_level)
            console_handler.setFormatter(logging.Formatter(self.__LOG_FORMAT))
            self.__logger.addHandler(console_handler)

        # NullHandler to avoid any low level library issue when Console handler also turned off.
        handler = logging.NullHandler()
        handler.setLevel(log_level)
        self.__logger.addHandler(handler)

        self.__logger.info("Logging module initialized")
        self.__logger.info(f"HOSTNAME : {socket.gethostname()}")

    def get_logger(self):
        return self.__logger

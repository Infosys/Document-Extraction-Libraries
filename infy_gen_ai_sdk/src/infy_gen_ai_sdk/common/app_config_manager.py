# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                   #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

"""Module containing AppConfigManager class"""

import os
import configparser
from infy_gen_ai_sdk.common.singleton import Singleton


class AppConfigManager(metaclass=Singleton):
    """Application configuration manager"""

    def __init__(self):
        config_files = [self.__find_config_file_path()]
        self.__app_config = self.__get_config_parser(config_files)

    def __get_config_parser(self, config_file):
        config_parser = configparser.ConfigParser()
        config_parser.read(config_file)
        return config_parser

    def get_app_config(self):
        """Returns instance of app config parser"""
        return self.__app_config

    def __find_config_file_path(self):
        """Returns config file path searching recursively from current directory"""
        config_file_path = ''
        module_dir = os.path.dirname(os.path.abspath(__file__))
        while not os.path.exists(config_file_path):
            module_dir = os.path.dirname(module_dir)
            config_file_path = os.path.abspath(
                module_dir + '/config/config.ini')
        return config_file_path

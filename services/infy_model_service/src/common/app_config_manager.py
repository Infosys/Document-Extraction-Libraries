# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import os
import configparser
from common.singleton import Singleton


class AppConfigManager(metaclass=Singleton):
    def __init__(self):
        config_files = [self.__find_config_file_path()]
        self.__app_config = self.__get_config_parser(config_files)

    def __get_config_parser(self, config_file):
        config_parser = configparser.ConfigParser()
        config_parser.read(config_file)
        return config_parser

    def get_app_config(self):
        return self.__app_config

    def get_about_app(self):
        return {
            "service_name": self.__app_config["DEFAULT"]["service_name"],
            "service_version": self.__app_config["DEFAULT"]["service_version"]
        }

    def __find_config_file_path(self):
        """Returns config file path searching recursively from current directory"""
        config_file_path = ''
        module_dir = os.path.dirname(os.path.abspath(__file__))
        while not os.path.exists(config_file_path):
            module_dir = os.path.dirname(module_dir)
            config_file_path = os.path.abspath(
                module_dir + '/config/config.ini')
        return config_file_path

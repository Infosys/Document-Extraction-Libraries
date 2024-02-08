# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import json


class ConfigDataFactory:
    def __init__(self, filepath) -> None:
        self.__file_path = filepath
        self.__data_source_config = None

    def get_config_data(self, config_name: str = None):
        data = self.__load_data_source()
        return data.get(config_name, None) if config_name else data

    def __load_data_source(self) -> dict:
        if self.__data_source_config:
            return self.__data_source_config
        self.__data_source_config = self.__load_json(self.__file_path)
        return self.__data_source_config

    def __load_json(self, file_path):
        data = None
        with open(file_path) as file:
            data = json.load(file)
        if (not data):
            raise Exception('error is template dictionary json load')
        return data

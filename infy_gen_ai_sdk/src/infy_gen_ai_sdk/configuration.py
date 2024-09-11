# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                   #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

"""Module for SDK configuration"""

from pydantic import BaseModel

from .common.app_config_manager import AppConfigManager
from .common.data_type_util import DataTypeUtil
from .common.singleton import Singleton


class ContainerData(BaseModel):
    """Container data"""
    container_root_path: str


class ClientConfigData(BaseModel):
    """Environment configuration data"""
    container_data: ContainerData = None


class ClientConfigManager(metaclass=Singleton):
    """Class used to manage client configuration mainly to set the environment 
    before start of execution."""

    def __init__(self):
        self.__app_config = AppConfigManager().get_app_config()
        self.__client_config_data = None

    def load(self, client_config_data: ClientConfigData):
        """Load properties"""
        self.__client_config_data = client_config_data
        self.__update_app_config()

    def get(self):
        """Return configuration set"""
        return self.__client_config_data

    # --- Private methods --- ###
    def __update_app_config(self):
        APP_CONFIG_KEY_TO_CLIENT_CONFIG_KEY = {
            "CONTAINER.CONTAINER_ROOT_PATH": "container_data.container_root_path",
        }
        app_config = self.__app_config
        client_config_data_dict = self.__client_config_data.dict()
        for key, val in APP_CONFIG_KEY_TO_CLIENT_CONFIG_KEY.items():
            client_var_val = DataTypeUtil.get_by_key_path(
                client_config_data_dict, val)
            if client_var_val:
                ini_key_parts = key.split('.')  # Expect only 2 values
                app_config[ini_key_parts[0]][ini_key_parts[1]] = client_var_val

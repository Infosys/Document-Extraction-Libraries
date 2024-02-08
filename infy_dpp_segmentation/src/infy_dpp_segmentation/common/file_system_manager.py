# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#


"""Module containing FileSystemManager"""

from urllib.parse import urlparse
from infy_dpp_segmentation.common.app_config_manager import AppConfigManager
from infy_dpp_segmentation.common.singleton import Singleton
from infy_dpp_segmentation.common.file_system_handler import FileSystemHandler


class FileSystemManager(metaclass=Singleton):
    """Class for creating a singleton instance of FileSystemHandler at application level."""

    def __init__(self) -> None:
        self.__app_config = AppConfigManager().get_app_config()
        storage_uri = self.__app_config['STORAGE']['STORAGE_URI']
        parsed_url = urlparse(storage_uri)
        __config_data = {}
        if not parsed_url.scheme == FileSystemHandler.SCHEME_TYPE_FILE:
            __config_data = {"endpoint_url": self.__app_config['STORAGE']['STORAGE_SERVER_URL'],
                             "key": self.__app_config['STORAGE']['STORAGE_ACCESS_KEY'],
                             "secret": self.__app_config['STORAGE']['STORAGE_SECRET_KEY']}
        file_sys_handler = FileSystemHandler(
            storage_uri, config=__config_data)
        self.__file_sys_handler = file_sys_handler

    def get_file_system_handler(self):
        """Returns instance of FileSystemHandler"""
        return self.__file_sys_handler

# FileSystemManager
# LocalFileSystemManager

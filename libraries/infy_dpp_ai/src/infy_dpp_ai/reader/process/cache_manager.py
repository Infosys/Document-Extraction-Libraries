# ===============================================================================================================#
# Copyright 2021 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#
import hashlib
import os
from infy_dpp_ai.common.singleton import Singleton
# from infy_gen_ai_sdk.common.logger_factory import LoggerFactory


class CacheManager(metaclass=Singleton):
    """Class that provides basic caching framework for all internal purposes"""

    def __init__(self, config_params: dict, file_sys_handler, logger, app_config):
        self.__logger = logger
        self.__app_config = app_config
        self.__file_sys_handler = file_sys_handler

        self.__cache_enabled = config_params.get('cache_enabled', False)
        self.__cache_root_path = os.path.expandvars(
            config_params.get('cache_path_root', ''))
        self.__logger.info(f"Is cache enabled : {self.__cache_enabled}")
        if self.__cache_enabled:
            cache_dir = self.__file_sys_handler.create_folders(
                self.__cache_root_path)
            self.__logger.info(f"folder name - {cache_dir}")

    def add(self, key_file_path: str, file_path_list: list, bucket: str):
        """Adds a list of files to a specified bucket using key_file as identity

        Args:
            key_file_path (str): Path of key file to be used to generate ID folder
            file_path_list (list): The list of files to add to the bucket
            bucket (str): The name of the bucket
        """
        if not self.__cache_enabled:
            self.__logger .debug("Cache is disabled. No items will be added")
            return

        # Get hash value of key file
        hash_value = self.__get_file_hash_value(key_file_path)

        # Create bucket folder
        bucket_folder_path = f"{self.__cache_root_path}/{hash_value}/{bucket}"
        self.__file_sys_handler.create_folders(bucket_folder_path)

        # Copy key file to root
        self.__file_sys_handler.copy_file(
            key_file_path, os.path.dirname(bucket_folder_path))

        # Copy other files to bucket folder
        for file_path in file_path_list:
            self.__file_sys_handler.copy_file(file_path, bucket_folder_path)

        self.__logger .debug(
            (f"For key file [{key_file_path}], created bucket folder [{bucket_folder_path}] ",
             " and added files {file_path_list}"))

    def get(self, key_file_path: str, bucket: str) -> str:
        """Returns the path of the bucket folder corresponding to provided key_file

        Args:
            key_file_path (str): Path of key file used to calculate ID folder
            bucket (str): The name of the bucket

        Returns:
            str: The full path of a valid bucket folder
        """
        if not self.__cache_enabled:
            self.__logger .debug("Cache is disabled. Returning None")
            return None

        # Get hash value of key file
        hash_value = self.__get_file_hash_value(key_file_path)
        # Create bucket folder path
        bucket_folder_path = f"{self.__cache_root_path}/{hash_value}/{bucket}"
        if self.__file_sys_handler.exists(bucket_folder_path):
            self.__logger .debug(
                f"For key file [{key_file_path}], retrieved bucket folder [{bucket_folder_path}]")
            return bucket_folder_path
        return None

    def __get_file_hash_value(self, file_path: str) -> str:
        file_content = self.__file_sys_handler.read_file(file_path)
        hash_lib = hashlib.sha1()
        hash_lib.update(file_content.encode())
        hash_value = hash_lib.hexdigest()
        return hash_value

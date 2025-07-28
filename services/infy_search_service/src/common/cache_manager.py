# ===============================================================================================================#
# Copyright 2021 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import os
from common.file_util import FileUtil
from common.singleton import Singleton
from common.ainauto_logger_factory import AinautoLoggerFactory
logger = AinautoLoggerFactory().get_logger()


class CacheManager(metaclass=Singleton):
    """Class that provides basic caching framework for all internal purposes"""

    def __init__(self, config_params: dict):
        self.__cache_enabled = config_params.get('cache_enabled', False)
        self.__cache_root_path = os.path.expandvars(
            config_params.get('cache_path_root', ''))
        logger.info(f"Is cache enabled : {self.__cache_enabled}")
        if self.__cache_enabled:
            cache_dir = FileUtil.create_dirs_if_absent(
                self.__cache_root_path)
            logger.info(f"folder name - {cache_dir}")

    def add(self, key_file_path: str, file_path_list: list, bucket: str):
        """Adds a list of files to a specified bucket using key_file as identity

        Args:
            key_file_path (str): Path of key file to be used to generate ID folder
            file_path_list (list): The list of files to add to the bucket
            bucket (str): The name of the bucket
        """
        if not self.__cache_enabled:
            logger.debug("Cache is disabled. No items will be added")
            return

        # Get hash value of key file
        hash_value = FileUtil.get_file_hash_value(key_file_path)
        # Create bucket folder
        bucket_folder_path = f"{self.__cache_root_path}/{hash_value}/{bucket}"
        FileUtil.create_dirs_if_absent(bucket_folder_path)

        # Copy key file to root
        FileUtil.copy_file(
            key_file_path, os.path.dirname(bucket_folder_path))

        # Copy other files to bucket folder
        for file_path in file_path_list:
            FileUtil.copy_file(file_path, bucket_folder_path)

        logger.debug(
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
            logger.debug("Cache is disabled. Returning None")
            return None

        # Get hash value of key file
        hash_value = FileUtil.get_file_hash_value(key_file_path)
        # Create bucket folder path
        bucket_folder_path = f"{self.__cache_root_path}/{hash_value}/{bucket}"
        if os.path.exists(bucket_folder_path):
            logger.debug(
                f"For key file [{key_file_path}], retrieved bucket folder [{bucket_folder_path}]")
            return bucket_folder_path
        return None

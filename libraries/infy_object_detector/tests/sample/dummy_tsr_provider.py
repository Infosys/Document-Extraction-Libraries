"""Module to extract table data using Dummy TSR Provider"""
# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import logging
import json
import infy_fs_utils

from infy_object_detector.schema.table_data import BaseTableConfigData, BaseTableRequestData, BaseTableResponseData
from infy_object_detector.structure_recogniser.interface import ITableStructureRecogniserProvider
from infy_object_detector.common.constants import Constants


class DummyTsrProviderConfigData(BaseTableConfigData):
    """Dummy TSR Provider Config Data class"""


class DummyTsrProvider(ITableStructureRecogniserProvider):
    """Dummy TSR Provider class"""

    def __init__(self, config_data: DummyTsrProviderConfigData) -> None:

        if infy_fs_utils.manager.FileSystemLoggingManager().has_fs_logging_handler():
            self.__logger = infy_fs_utils.manager.FileSystemLoggingManager(
            ).get_fs_logging_handler().get_logger()
        else:
            self.__logger = logging.getLogger(__name__)

        if infy_fs_utils.manager.FileSystemManager().has_fs_handler():
            self.__fs_handler = infy_fs_utils.manager.FileSystemManager(
            ).get_fs_handler()
        self.__config_data = config_data

    def extract_table_data(self, table_request_data: BaseTableRequestData) -> BaseTableResponseData:
        """Extract table data from the input image file"""
        image_file_path = table_request_data.image_file_path
        try:
            self.__logger.info(
                "Extraction started for file : %s", image_file_path)
            file_path = './data/input/tsr_table_data_sample.json'
            data = self.__fs_handler.read_file(file_path, encoding='utf8')
            json_data = json.loads(data)
            response = BaseTableResponseData(**json_data)
            self.__logger.info(
                "Extraction completed for file : %s", image_file_path)
        except Exception as e:
            self.__logger.error("Error : %s", str(e))
            raise e
        return response

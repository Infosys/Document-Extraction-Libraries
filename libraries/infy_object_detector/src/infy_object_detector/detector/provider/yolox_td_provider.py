# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import logging
import requests
import infy_fs_utils
from ..interface.i_table_detector_provider import ITableDetectorProvider
from ...schema.table_data import BaseTableConfigData, BaseTableRequestData, BaseTableResponseData

DETECT_ENDPOINT = "/detect"


class YoloxTdProviderConfigData(BaseTableConfigData):
    """Yolox table provider config data class"""
    model_service_url: str = None


class YoloxTdRequestData(BaseTableRequestData):
    """Yolox table request data class"""


class YoloxTdResponseData(BaseTableResponseData):
    """Yolox table response data class"""
    image_width: int = None
    image_height: int = None


class YoloxTdProvider(ITableDetectorProvider):
    """Yolox table provider class"""

    def __init__(self, config_data: YoloxTdProviderConfigData) -> None:
        if infy_fs_utils.manager.FileSystemLoggingManager().has_fs_logging_handler():
            self.__logger = infy_fs_utils.manager.FileSystemLoggingManager(
            ).get_fs_logging_handler().get_logger()
        else:
            self.__logger = logging.getLogger(__name__)

        self.__fs_handler = infy_fs_utils.manager.FileSystemManager(
        ).get_fs_handler()
        self.__model_yolox_td_service_url = config_data.model_service_url+DETECT_ENDPOINT

    def detect_table(self, request_data: YoloxTdRequestData) -> YoloxTdResponseData:
        """Detect Table for the provided image"""
        td_response = self.__call_model(request_data.image_file_path)
        return td_response

    def __call_model(self, image_file_path: str) -> YoloxTdResponseData:
        with open(image_file_path, "rb") as file:
            response_obj = requests.post(
                self.__model_yolox_td_service_url, files={"file": file}, timeout=400)
        return YoloxTdResponseData(**response_obj.json())

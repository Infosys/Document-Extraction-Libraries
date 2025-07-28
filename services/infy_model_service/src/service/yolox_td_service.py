# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import logging
# import infy_fs_utils
from common.singleton import Singleton
import unstructured_inference.models.base as models
from unstructured_inference.inference.layout import DocumentLayout
from unstructured_inference.models.yolox import UnstructuredYoloXModel, MODEL_TYPES, YOLOX_LABEL_MAP
from unstructured_inference.utils import (
    LazyDict,
    LazyEvaluateInfo,
    download_if_needed_and_get_local_path,
)
from schema.yolox_data import YoloxTdRequestData, YoloxTdResponseData
# from ..interface.i_table_detector_provider import ITableDetectorProvider
# from ...schema.table_data import BaseTableConfigData, BaseTableRequestData, BaseTableResponseData


# class YoloxTdProviderConfigData(BaseTableConfigData):
#     """Yolox table provider config data class"""


# class YoloxTdRequestData(BaseTableRequestData):
#     """Yolox table request data class"""


# class YoloxTdResponseData(BaseTableResponseData):
#     """Yolox table response data class"""
#     image_width: int = None
#     image_height: int = None

# class YoloxTdService(ITableDetectorProvider):


class YoloxTdService(metaclass=Singleton):
    """Yolox table provider class"""

    def __init__(self, model_name: str, model_home_path: str) -> None:
        # if infy_fs_utils.manager.FileSystemLoggingManager().has_fs_logging_handler():
        #     self.__logger = infy_fs_utils.manager.FileSystemLoggingManager(
        #     ).get_fs_logging_handler().get_logger()
        # else:
        #     self.__logger = logging.getLogger(__name__)

        # self.__fs_handler = infy_fs_utils.manager.FileSystemManager(
        # ).get_fs_handler()
        self.__model_path = model_home_path
        self.__model_name = model_name
        if self.__model_name not in MODEL_TYPES:
            self.__register_local_model()
        self.__model = self.__get_model()

    def detect_table_yolox(self, request_data: YoloxTdRequestData) -> YoloxTdResponseData:
        """Detect Table for the provided image"""
        td_response = self.__call_model(
            request_data.image_file_path)
        return td_response

    def __call_model(self, image_file_path: str) -> YoloxTdResponseData:
        layout = DocumentLayout.from_image_file(
            image_file_path, detection_model=self.__model)
        elements_list = []
        image_width = None
        image_height = None
        layout_elements = layout.pages[0].elements

        for element in layout_elements:
            if element.type == "Table":
                data = {
                    "bbox": [round(element.bbox.x1, 2),
                             round(element.bbox.y1, 2),
                             round(element.bbox.x2, 2),
                             round(element.bbox.y2, 2)],
                    "td_confidence_pct": round(element.prob, 3)

                }
                elements_list.append(data)
        if elements_list:
            image_width = layout.pages[0].image_metadata["width"]
            image_height = layout.pages[0].image_metadata["height"]

        return YoloxTdResponseData(image_width=image_width,
                                   image_height=image_height, table_data=elements_list)

    def __register_local_model(self):
        local_model_path = LazyEvaluateInfo(
            download_if_needed_and_get_local_path,
            self.__model_path,
            "yolox_l0.05.onnx",
        )
        model_type = {
            self.__model_name: LazyDict(
                model_path=local_model_path,
                label_map=YOLOX_LABEL_MAP,
            )
        }
        models.register_new_model(model_type, UnstructuredYoloXModel)

    def __get_model(self):
        return models.get_model(self.__model_name)

# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                   #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import requests
import os
from infy_dpp_segmentation.segment_generator.service.detectron_service import DetectronService
import infy_fs_utils
import infy_dpp_sdk


class SegmentGeneratorService:
    '''segment generator service class'''

    def __init__(self, model_config) -> None:
        self.__logger = infy_fs_utils.manager.FileSystemLoggingManager(
        ).get_fs_logging_handler(infy_dpp_sdk.common.Constants.FSLH_DPP).get_logger()
        self.__detectron_service_obj = DetectronService(model_config)

    def get_segment_data(self, image_file_path_list):
        try:
            response_list = []
            for image_file_path in image_file_path_list:
                page_no = os.path.basename(image_file_path).replace('.jpg', '')
                detectron_output = self.__detectron_service_obj.get_bbox(
                    image_file_path)
                if not detectron_output:
                    self.__logger.info(f"Empty response for page no {page_no}")
                # updating page no
                _ = [i.update({'page': int(page_no)})
                     for i in detectron_output]
                response_list.append(
                    {"page_no": page_no, "output": detectron_output})
        except Exception as e:
            self.__logger.error(f"{e}")
            raise Exception(f"{e}")
        return response_list

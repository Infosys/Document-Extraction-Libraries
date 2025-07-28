# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#
import datetime
import json
import os
import shutil
from PIL import Image, ImageDraw, ImageFont
from infy_object_detector.detector.table_detector import TableDetector
from infy_object_detector.detector.provider.yolox_td_provider import YoloxTdProvider, \
    YoloxTdProviderConfigData, YoloxTdRequestData
from infy_dpp_evaluator.common.file_util import FileUtil


class TableDetectorYoloxService:

    def __init__(self, fs_handler, app_config, logger, model_provider_dict):
        self.__logger = logger
        self.__app_config = app_config
        self.__file_sys_handler = fs_handler

        self.__model_path = model_provider_dict.get(
            'properties').get('yolox_model_home', '')
        if self.__model_path == '':
            raise Exception(
                'YOLOX model path is not configured in the config file')
        self.__model_name = model_provider_dict.get(
            'properties').get('model_name', '')
        if self.__model_name == '':
            raise Exception(
                'YOLOX model name is not configured in the config file')
        self.__model_provider_name = model_provider_dict.get('provider_name')
        if self.__model_provider_name == '':
            raise Exception(
                'YOLOX model provider name is not configured in the config file')

        self.__td_provider = YoloxTdProvider(
            YoloxTdProviderConfigData(
                model_name=self.__model_name,
                model_path=self.__model_path
            )
        )
        self.__td = TableDetector(self.__td_provider)

    def detect_table(self, image_file_path_list: list) -> list:

        timestamp_folder_path_list = []
        for image_file_path in image_file_path_list:
            images_folder_path = os.path.join(image_file_path + "_files")
            if not os.path.exists(images_folder_path):
                os.makedirs(images_folder_path)
            yolox_folder_path = os.path.join(
                images_folder_path, self.__model_provider_name)
            if os.path.exists(yolox_folder_path):
                shutil.rmtree(yolox_folder_path)
            os.makedirs(yolox_folder_path, exist_ok=True)
            timestamp = datetime.datetime.now().strftime("%d%m%Y_%H%M%S")
            timestamp_folder_path = os.path.join(yolox_folder_path, timestamp)
            os.makedirs(timestamp_folder_path, exist_ok=True)
            elements_list = []
            td_data = self.__td.detect_table(
                YoloxTdRequestData(
                    **{
                        "image_file_path": image_file_path
                    }
                ))
            elements_list = td_data.dict()
            output_file_path = f"1.jpg_document_data.json"
            output_file_path = os.path.join(
                timestamp_folder_path, output_file_path)
            output_file_path = os.path.normpath(output_file_path)
            # Ensure the directory exists
            os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
            with open(output_file_path, "w") as json_file:
                json.dump(elements_list, json_file, indent=4)
            FileUtil.save_to_json(output_file_path, elements_list)
            server_file_dir = os.path.dirname(output_file_path.replace('\\', '/').replace('//', '/').replace(
                self.__app_config["CONTAINER"]["APP_DIR_TEMP_PATH"].replace('\\', '/').replace('//', '/'), ''))
            local_dir = os.path.dirname(output_file_path)
            self.__draw_bbox(image_file_path, elements_list,
                             timestamp_folder_path)
            self._upload_data(f'{local_dir}', f'{server_file_dir}')
            timestamp_folder_path_list.append(timestamp_folder_path)
        return timestamp_folder_path_list

    def __draw_bbox(self, img_file: str, element_list, timestamp_folder_path: str):
        image = Image.open(img_file).convert("RGB")
        draw_image = image.copy()
        draw = ImageDraw.Draw(draw_image)
        font = ImageFont.load_default()
        # Example: Using Arial font with size 24
        # font = ImageFont.truetype("arial.ttf", 24)
        for box in element_list.get('table_data'):
            # if box.get('type') == "Table":
            draw.rectangle(box.get('bbox'), outline="red", width=3)
            text_position = (box.get('bbox')[0], box.get('bbox')[1] - 20)

            # Draw the type label
            draw.text(text_position, "Table",
                      fill="red", font=font)
            draw.rectangle(box.get('bbox'), outline="red", width=3)
            text_position = (box.get('bbox')[0], box.get('bbox')[1] - 20)

            # Draw the type label
            draw.text(text_position, "Table",
                      fill="red", font=font)

        output_file_path = f"1.jpg_bbox.jpg"
        output_file_path = timestamp_folder_path + "/" + output_file_path
        draw_image.save(output_file_path)

    def _upload_data(self, local_file_path, server_file_path):
        try:
            self.__file_sys_handler.put_folder(
                local_file_path, server_file_path)
            self.__logger.info(
                f'Folder {local_file_path} uploaded successfully')
        except Exception as e:
            self.__logger.error(
                f'Error while uploading data to {server_file_path} : {e}')
            raise e

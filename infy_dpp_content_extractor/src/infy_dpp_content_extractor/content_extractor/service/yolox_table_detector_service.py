# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#
import math
import os
import unstructured_inference.models.base as models
from unstructured_inference.inference.layout import DocumentLayout
from unstructured_inference.models.yolox import UnstructuredYoloXModel, MODEL_TYPES, YOLOX_LABEL_MAP
from unstructured_inference.utils import (
    LazyDict,
    LazyEvaluateInfo,
    download_if_needed_and_get_local_path,
)
from PIL import Image, ImageDraw, ImageFont
from infy_dpp_content_extractor.common.file_util import FileUtil


class YoloxTableDetectorService:
    
    def __init__(self, model_path, model_name):
        self.model_name = model_name
        self.model_path = model_path
        
    def __register_local_model(self):
        local_model_path = LazyEvaluateInfo(
            download_if_needed_and_get_local_path,
            self.model_path,
            "yolox_l0.05.onnx",
        )
        model_type = {
            self.model_name: LazyDict(
                model_path=local_model_path,
                label_map=YOLOX_LABEL_MAP,
            )
        }
        models.register_new_model(model_type, UnstructuredYoloXModel)

    def __get_model(self):
        return models.get_model(self.model_name)

    def detect_table(self, file_full_path_list: list, table_debug) -> list:
        elements_dicts_list = []
        if self.model_name not in MODEL_TYPES:
            self.__register_local_model()
        model = self.__get_model()
        for file_path in file_full_path_list:
            layout = DocumentLayout.from_image_file(
                file_path, detection_model=model)
            elements_list = []
            layout_elements = layout.pages[0].elements

            for element in layout_elements:
                if element.type == "Table":
                    data = {
                        "type": element.type,
                        "bbox": [math.ceil(element.bbox.x1),
                                 math.ceil(element.bbox.y1),
                                 math.ceil(element.bbox.x2),
                                 math.ceil(element.bbox.y2)],
                        "conf_pct": round(element.prob, 3)
                    }
                    elements_list.append(data)

            if elements_list:
                elements_dict = {
                    "page":"",
                    "image": os.path.basename(file_path),
                    "width": layout.pages[0].image_metadata["width"],
                    "height": layout.pages[0].image_metadata["height"],
                    "bbox": "X1,Y1,X2,Y2",
                    "tokens": elements_list
                }
                elements_dicts_list.append(elements_dict)
                # Draw Table bbox on image If debug is enabled
                if table_debug.get("enabled") and table_debug.get("generate_image"):
                     output_dir = os.path.dirname(file_path)+table_debug.get("output_dir_path")
                     self.__draw_bbox(file_path, elements_list, output_dir)

        return elements_dicts_list
    
    def __draw_bbox(self, img_file: str, element_list, output_dir: str):
        image = Image.open(img_file).convert("RGB")
        draw_image = image.copy()
        draw = ImageDraw.Draw(draw_image)
        # font = ImageFont.load_default()
        # Example: Using Arial font with size 24
        font = ImageFont.truetype("arial.ttf", 24)
        for box in element_list:
            if box.get('type') == "Table":
                draw.rectangle(box.get('bbox'), outline="red", width=3)
                text_position = (box.get('bbox')[0], box.get('bbox')[1] - 20)

                # Draw the type label
                draw.text(text_position, box.get('type'),
                          fill="red", font=font)
                draw.rectangle(box.get('bbox'), outline="red", width=3)
                text_position = (box.get('bbox')[0], box.get('bbox')[1] - 20)

                # Draw the type label
                draw.text(text_position, box.get('type'),
                      fill="red", font=font)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        output_file_path = f"{os.path.basename(img_file)}_yolox.jpg"
        output_file_path = output_dir + "\\" + output_file_path
        draw_image.save(output_file_path)
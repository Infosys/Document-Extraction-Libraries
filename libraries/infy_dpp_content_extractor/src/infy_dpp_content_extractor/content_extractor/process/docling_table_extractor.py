# ===============================================================================================================#
# Copyright 2025 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#
import os
import math
from infy_dpp_content_extractor.common.file_util import FileUtil
from infy_dpp_content_extractor.content_extractor.service import InfyObjectDetectorService
from PIL import Image, ImageDraw, ImageFont


class DoclingTableExtactor():
    def __init__(self, model_provider_dict, text_provider_dict, file_sys_handler, logger, app_config):
        self.__logger = logger
        self.__app_config = app_config
        self.__file_sys_handler = file_sys_handler
        self.__is_table_html_view = model_provider_dict.get(
            'properties').get('is_table_html_view', False)
        self.__model_service_url = model_provider_dict.get(
            'properties').get('model_service_url', '')
        if self.__model_service_url == '':
            raise Exception(
                'URL for Docling table extraction api is not configured in the config file')
        self.__provider_class = model_provider_dict.get('provider_class', '')
        self.__model_provider_class_name = self.__provider_class.split('.')[-1]
        self.__model_provider_module_name = '.'.join(self.__provider_class.split('.')[
            :-1])
        self.text_provider_dict = text_provider_dict
        # self.line_detection_method = line_detection_method

    def get_tables_content(self, images_file_path_list, from_files_full_path, out_file_full_path, table_debug) -> list:
        def __get_temp_file_path(work_file_path):
            local_file_path = f'{self.__app_config["CONTAINER"]["APP_DIR_TEMP_PATH"]}/{work_file_path}'
            FileUtil.create_dirs_if_absent(os.path.dirname(local_file_path))
            with self.__file_sys_handler.get_file_object(work_file_path) as f:
                with open(local_file_path, "wb") as output:
                    output.write(f.read())
            return local_file_path

        # ------- Table detection and TSR using docling STARTS HERE --------#
        image_file_full_path_list = []
        for image_path in images_file_path_list:
            image_file_full_path_list.append(__get_temp_file_path(image_path))

        infy_object_detector_service_obj = InfyObjectDetectorService(
            self.__logger, self.__model_service_url,
            self.__model_provider_class_name, self.__model_provider_module_name,
            self.text_provider_dict, out_file_full_path,
            is_table_html_view=self.__is_table_html_view)
        page_tables_bbox_list = infy_object_detector_service_obj.detect_table(
            image_file_full_path_list)
        if not page_tables_bbox_list:
            self.__logger.info("No tables detected in the input images")
            return [], []
        else:
            self.__logger.debug(
                "Table/s detected in file by Docling model")
        # ------- Table detection and TSR using docling END HERE --------#

        # Table content formatting
        tables_detected_list = []
        table_detected_file_path_list = []
        results_list = []
        for page_tables in page_tables_bbox_list:
            tables_data_list = []
            file_name = page_tables.get("image") + "_docling.json"
            page_tables['page'] = page_tables.get(
                "image").replace(".jpg", "")
            for image_path in images_file_path_list:
                if page_tables['image'] == os.path.basename(image_path):
                    page_tables['image'] = image_path
                    break
            table_detected_file_path = os.path.join(
                out_file_full_path, file_name)
            tables_detected_list.append(page_tables)

            FileUtil.save_to_json(table_detected_file_path, page_tables)
            table_detected_file_path = table_detected_file_path.replace('\\', '/').replace('//', '/').replace(
                self.__app_config["CONTAINER"]["APP_DIR_TEMP_PATH"].replace('\\', '/').replace('//', '/'), '')
            table_detected_file_path_list.append(table_detected_file_path)

            table_number = 1

            for idx, token in enumerate(page_tables.get('table_data')):
                table_bbox = []
                token['bbox'] = [math.ceil(coord) for coord in token['bbox']]
                table_bbox.append(token['bbox'][0])
                table_bbox.append(token['bbox'][1])
                table_bbox.append(token['bbox'][2] - token['bbox'][0])
                table_bbox.append(token['bbox'][3] - token['bbox'][1])
                img_file_path = __get_temp_file_path(page_tables.get('image'))

                if table_debug.get("enabled") and table_debug.get("generate_image"):
                    output_dir = os.path.dirname(
                        img_file_path)+table_debug.get("output_dir_path")
                    self.__draw_bbox(
                        img_file_path, token['bbox'], output_dir)
                html_data = page_tables.get('table_html_data')[idx].get(
                    'cell_data_html') if page_tables.get('table_html_data') else None
                table_data = {
                    "table_id": f"p{page_tables.get('page')}_tb{table_number}",
                    "bbox":  token['bbox'],
                    "data": token.get('cell_data'),
                    "html_data": html_data,
                    "debug_path": token.get('debug_path')
                }
                table_number += 1
                tables_data_list.append(table_data)

            if tables_data_list:
                table_dict = {
                    "page_number": int(page_tables.get('page')),
                    "page_width": page_tables.get('image_width'),
                    "page_height": page_tables.get('image_height'),
                    "tables": tables_data_list
                }
                results_list.append(table_dict)

        output_file_path = os.path.join(
            out_file_full_path, f"{os.path.basename(from_files_full_path)}_docling.json")
        FileUtil.save_to_json(output_file_path, tables_detected_list)

        img_docling_td_tsr_path = os.path.join(
            out_file_full_path, f"{os.path.basename(from_files_full_path)}_img_docling_td_tsr.json")
        FileUtil.save_to_json(
            img_docling_td_tsr_path, results_list)

        server_file_dir = os.path.dirname(img_docling_td_tsr_path.replace('\\', '/').replace('//', '/').replace(
            self.__app_config["CONTAINER"]["APP_DIR_TEMP_PATH"].replace('\\', '/').replace('//', '/'), ''))
        local_dir = os.path.dirname(img_docling_td_tsr_path)
        self._upload_data(f'{local_dir}', f'{server_file_dir}')

        table_content_file_path = img_docling_td_tsr_path.replace('\\', '/').replace('//', '/').replace(
            self.__app_config["CONTAINER"]["APP_DIR_TEMP_PATH"].replace('\\', '/').replace('//', '/'), '')
        return table_content_file_path, table_detected_file_path_list

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

    def __draw_bbox(self, img_file: str, bbox, output_dir: str):
        image = Image.open(img_file).convert("RGB")
        draw_image = image.copy()
        draw = ImageDraw.Draw(draw_image)
        # font = ImageFont.load_default()
        # Example: Using Arial font with size 24
        font = ImageFont.truetype("arial.ttf", 24)

        draw.rectangle(bbox, outline="red", width=3)
        text_position = (bbox[0], bbox[1] - 20)

        # Draw the type label
        draw.text(text_position, "Table",
                  fill="red", font=font)
        draw.rectangle(bbox, outline="red", width=3)
        text_position = (bbox[0], bbox[1] - 20)

        # Draw the type label
        draw.text(text_position, "Table",
                  fill="red", font=font)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        output_file_path = f"{os.path.basename(img_file)}_docling.jpg"
        output_file_path = output_dir + "\\" + output_file_path
        draw_image.save(output_file_path)

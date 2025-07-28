
"""Module for segment structure recognition service"""
# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#
from csv import DictReader
import datetime
import shutil
import json
import os
import re
from typing import List
import infy_table_extractor as ite
from infy_object_detector.structure_recogniser.provider.bordered_table_tsr_provider import BorderedTableTsrProvider, \
    BorderedTableTsrProviderConfigData, BorderedTableTsrProviderRequestData


class TableStructureRecognizerLdService():
    """Class for segment structure recognition"""

    def __init__(self, fs_handler, app_config, logger, text_provider_dict, technique_name):
        self.__logger = logger
        self.__app_config = app_config
        temp_folder_path = f'{self.__app_config["CONTAINER"]["APP_DIR_TEMP_PATH"]}'
        self.__file_sys_handler = fs_handler

        self.__ocr_engine_home = text_provider_dict.get(
            'properties').get('ocr_engine_home', '')
        if self.__ocr_engine_home == '':
            raise Exception(
                'OCR Engine home is not configured in the config file')
        self.__model_dir_path = text_provider_dict.get(
            'properties').get('model_dir_path', '')
        if self.__model_dir_path == '':
            raise Exception(
                'Model dir path is not configured in the config file')
        __ld_method = ite.interface.LineDetectionMethod.OPENCV_LINE_DETECT
        if technique_name == 'img_infy_rgb_ld':
            __ld_method = ite.interface.LineDetectionMethod.RGB_LINE_DETECT
        config_param_dict = {
            'col_header': {
                'use_first_row': True,
            },
            # 'line_detection_method': [ite.interface.LineDetectionMethod.OPENCV_LINE_DETECT]
            'line_detection_method': [__ld_method]
        }
        self.__tsr_provider = BorderedTableTsrProvider(
            BorderedTableTsrProviderConfigData(
                ocr_engine_exe_dir_path=self.__ocr_engine_home,
                ocr_engine_model_dir_path=self.__model_dir_path,
                temp_folder_path=temp_folder_path,
                config_param_dict=config_param_dict,
                model_path="",
                model_name="",
            )
        )

    def __get_bbox_from_truth_data(self, image_file_path, truth_data_file_path):
        """Method to get bounding box from truth data file"""
        truth_data_list = []
        if truth_data_file_path:
            with open(truth_data_file_path, encoding='utf-8-sig') as file:
                dict_reader = DictReader(file)
                truth_data_list = list(dict_reader)
            truth_image_subpath_list = list(
                set([x['image_subpath'] for x in truth_data_list]))
            last_image_name = None
            table_num = None
            for truth_data in truth_data_list:
                if last_image_name == truth_data['image_subpath']:
                    table_num += 1
                else:
                    table_num = 65  # Ascii value for A
                truth_data['truth_table_name'] = "table_" + chr(
                    table_num) + "_" + truth_data['x1'] + "_" + truth_data['y1'] + "_" + truth_data['x2'] + "_" + truth_data['y2']
                last_image_name = truth_data['image_subpath']
            _truth_data_list = []
            # For each image loop
            for truth_image_subpath in truth_image_subpath_list:
                updated_truth_image_subpath = truth_image_subpath.replace(
                    '\\', '/').replace('//', '/')
                if updated_truth_image_subpath == image_file_path:
                    _truth_data_list = [
                        x for x in truth_data_list if x['image_subpath'] == truth_image_subpath]
                truth_table_bbox_list = []
            for truth_data in _truth_data_list:
                truth_table_name = truth_data['truth_table_name']
                truth_bbox = [truth_data['x1'], truth_data['y1'],
                              truth_data['x2'], truth_data['y2']]
                truth_table_bbox_list.append({
                    'truth_table_name': truth_table_name,
                    'truth_bbox': [int(x) for x in truth_bbox]
                })
        return truth_table_bbox_list

    def __get_bbox_from_detector(self, image_file_path, result_data_path):
        """Method to get bounding box from detector result"""
        records = []
        result_data_path_json_list = []
        if result_data_path:

            result_data_path_full_list = self.__list_files(result_data_path)
            result_data_path_json_list = [
                result_data_file for result_data_file
                in result_data_path_full_list if result_data_file.lower().endswith(('.json'))]
            for result_file in result_data_path_json_list:
                # result_file_temp_path = f'{self.__app_config["CONTAINER"]["APP_DIR_TEMP_PATH"]}/{result_file}'
                result_file_content = self.__file_sys_handler.read_file(
                    result_file)
                # result_file_temp_path = self.__file_sys_handler.get_bucket_name() + "/" + \
                #     result_file
                # with open(result_file_temp_path, encoding='utf-8-sig') as file:
                #      data = json.load(file)\
                data = json.loads(result_file_content)
                records = data.get('records', [])
                records = [record for record in records]
                result_image_subpath_list = list(
                    set([x['image_subpath'] for x in records]))
                last_image_name = None
                table_num = None
                for record in records:
                    if last_image_name == record['image_subpath']:
                        table_num += 1
                    else:
                        table_num = 65  # Ascii value for A
                    x1 = str(int(record['bbox'][0]))
                    y1 = str(int(record['bbox'][1]))
                    x2 = str(int(record['bbox'][2]))
                    y2 = str(int(record['bbox'][3]))
                    record['table_name'] = "table_" + chr(
                        table_num) + "_" + x1 + "_" + y1 + "_" + x2 + "_" + y2
                    last_image_name = record['image_subpath']
                _result_data_list = []
                # For each image loop
                for result_image_subpath in result_image_subpath_list:
                    updated_result_image_subpath = result_image_subpath.replace(
                        '\\', '/').replace('//', '/')
                    if updated_result_image_subpath == image_file_path:
                        _result_data_list = [
                            x for x in records if x['image_subpath'] == result_image_subpath]
                    truth_table_bbox_list = []
                for record in _result_data_list:
                    table_name = record['table_name']
                    truth_bbox = [record['bbox'][0], record['bbox'][1],
                                  record['bbox'][2], record['bbox'][3]]
                    truth_table_bbox_list.append({
                        'truth_table_name': table_name,
                        'truth_bbox': [int(x) for x in truth_bbox]
                    })
        return truth_table_bbox_list

    def recognize_structure(self, image_file_path_list: list, bbox_source, docs_truth_data_path, technique_name, result_data_full_path) -> list:
        """Method to recognize the segment structure"""
        # output_file_prefix = ssr_config_data.get('output_file_prefix', "")
        self.__logger.info("Technique Name : %s", technique_name)
        result_file_list = []
        for image_file_path in image_file_path_list:
            self.__logger.info("Processing file: %s", {image_file_path})
            images_folder_path = os.path.join(image_file_path + "_files")
            if not os.path.exists(images_folder_path):
                os.makedirs(images_folder_path)
            technique_name_path = os.path.join(
                images_folder_path, technique_name)
            if os.path.exists(technique_name_path):
                shutil.rmtree(technique_name_path)
            os.makedirs(technique_name_path, exist_ok=True)
            timestamp = datetime.datetime.now().strftime("%d%m%Y_%H%M%S")
            timestamp_folder_path = os.path.join(
                technique_name_path, timestamp)
            os.makedirs(timestamp_folder_path, exist_ok=True)
            truth_bbox = []
            pattern = r'docs/(.*)'
            image_file_subpath = image_file_path
            match = re.search(pattern, image_file_path)
            if match:
                image_file_subpath = match.group(1)
            table_bbox_list = []
            response = ""
            if bbox_source == 'truth_data':
                table_bbox_list = self.__get_bbox_from_truth_data(
                    image_file_subpath, docs_truth_data_path)
            elif bbox_source == 'detector':
                table_bbox_list = self.__get_bbox_from_detector(
                    image_file_subpath, result_data_full_path)
            for item in table_bbox_list:
                truth_table_name = item['truth_table_name']
                truth_bbox = item['truth_bbox']
                # TSR provider expects the bbox in the format [x1, y1, w, h]
                provider_bbox = [truth_bbox[0], truth_bbox[1],
                                 truth_bbox[2] - truth_bbox[0], truth_bbox[3] - truth_bbox[1]]
                table_request_data = BorderedTableTsrProviderRequestData(
                    image_file_path=image_file_path, bbox=provider_bbox)
                response = self.__tsr_provider.extract_table_data(
                    table_request_data)
                response_dict = response.dict()
                # output_file_path = f"{output_file_prefix}_{truth_table_name}.json"
                output_file_path = f"{truth_table_name}.json"
                output_file_path = os.path.join(
                    timestamp_folder_path, output_file_path)
                output_file_path = os.path.normpath(output_file_path)
                # Ensure the directory exists
                os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
                with open(output_file_path, "w", encoding="utf-8") as json_file:
                    json.dump(response_dict, json_file, indent=4)
                server_file_dir = os.path.dirname(output_file_path.replace('\\', '/').replace('//', '/').replace(
                    self.__app_config["CONTAINER"]["APP_DIR_TEMP_PATH"].replace('\\', '/').replace('//', '/'), ''))
                local_dir = os.path.dirname(output_file_path)
                self._upload_data(f'{local_dir}', f'{server_file_dir}')
                output_file_path = server_file_dir + \
                    "/"+os.path.basename(output_file_path)
                result_file_list.append(output_file_path)
        return result_file_list

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

    def __list_files(self, from_files_folder_path) -> List[str]:
        found_files = self.__file_sys_handler.list_files(
            from_files_folder_path)
        if len(found_files) > 0:
            self.__logger.info(
                "Found %d files in %s", len(found_files), from_files_folder_path)
        else:
            self.__logger.info(
                "No files found in %s, stopping pipeline execution", from_files_folder_path)
        return found_files

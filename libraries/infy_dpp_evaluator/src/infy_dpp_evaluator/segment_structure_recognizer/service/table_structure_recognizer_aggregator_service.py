"""Module to aggregate the data extracted by the table structure recognizer techniques."""
# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#
import os
import json
import datetime
from infy_dpp_evaluator.common.file_util import FileUtil


class TableStructureRecognizerAggregatorService:

    def __init__(self, fs_handler, app_config, logger, text_provider_dict, dataset_name_with_version, output_file_prefix):
        self.__logger = logger
        self.__app_config = app_config
        temp_folder_path = f'{self.__app_config["CONTAINER"]["APP_DIR_TEMP_PATH"]}'
        self.__file_sys_handler = fs_handler
        self.__output_file_prefix = output_file_prefix
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
        self.__dataset_name_with_version = dataset_name_with_version
        if self.__dataset_name_with_version == '':
            raise Exception(
                'Data set name and version is not configured in the config file')

    def transform_records(self, records):
        """Transform the records to the required format."""
        transformed_records = []
        for record in records:  # Directly iterate over records, assuming it's a list of dicts
            transformed_record = {
                "image_subpath": record.get("image_subpath", ""),
                "object_type": record.get("type", "Table"),
                "bbox_format": "X1,Y1,X2,Y2",
                "bbox": record.get("bbox", []),
                "tsr_confidence_pct": record.get("tsr_confidence_pct", 0),
                "no_of_rows": record.get("no_of_rows", ""),
                "no_of_columns": record.get("no_of_columns", ""),
                "title": record.get("title", ""),
                "cell_data": record.get("cell_data", []),
                "table_html_data": record.get("table_html_data", ""),
            }
            transformed_records.append(transformed_record)
        return transformed_records

    def aggregate_data_from_folders(self, root_dir, result_data_path, technique_name) -> list:
        """Aggregate the data extracted by the table structure recognizer techniques."""
        # Metadata should be a dict, not a list
        aggregated_data = {"metadata": {}, "records": []}
        timestamp = datetime.datetime.now().strftime("%d%m%Y_%H%M%S")
        path_separator = "\\"
        metadata = {
            "segment_structure_recognition_technique": technique_name,
            "run_id": timestamp,
            "dataset_name_with_version": self.__dataset_name_with_version,
            "root_path": root_dir
        }
        aggregated_data["metadata"] = metadata
        all_records = []
        root_dir = f'{self.__app_config["CONTAINER"]["APP_DIR_TEMP_PATH"]}/{root_dir}'
        for root, dirs, files in os.walk(root_dir):
            if technique_name in root:
                for file in files:
                    file_path = os.path.join(root, file)
                    if file_path.endswith('.json'):
                        with open(file_path, 'r') as f:
                            data = json.load(f)
                            table_data = data.get("table_data", [])
                            table_html_data = data.get("table_html_data", [])
                            image_subpath = os.path.relpath(
                                file_path, root_dir)
                            path_components = image_subpath.split(os.path.sep)
                            path_components[1] = path_components[1].replace(
                                "_files", "")
                            first_two_components = path_components[:2]
                            image_subpath = first_two_components[0] + \
                                path_separator+first_two_components[1]
                            if isinstance(table_data, dict):
                                table_data['image_subpath'] = image_subpath
                                all_records.append(table_data)
                            elif isinstance(table_data, list):
                                for item, html_data in zip(table_data, table_html_data):
                                    if isinstance(item, dict):
                                        item['image_subpath'] = image_subpath
                                        item['table_html_data'] = html_data.get(
                                            'cell_data_html', "")
                                        all_records.append(item)
                                # for item in table_data:
                                #     if isinstance(item, dict):
                                #         item['image_subpath'] = image_subpath
                                #         item['table_html_data'] = table_html_data[0].get(
                                #             'cell_data_html', [])
                                #         all_records.append(item)
        aggregated_data["records"] = self.transform_records(all_records)

        # Create the JSON file
        ts_for_json = datetime.datetime.now().strftime("%d%m%Y_%H%M%S")
        aggregated_data_path = f"{self.__output_file_prefix}_{technique_name}_{ts_for_json}.json"
        result_data_path = f'{self.__app_config["CONTAINER"]["APP_DIR_TEMP_PATH"]}/{result_data_path}'
        if not os.path.exists(result_data_path):
            os.makedirs(result_data_path)
        aggregated_data_path = result_data_path + "/" + aggregated_data_path
        with open(aggregated_data_path, "w") as json_file:
            json.dump(aggregated_data, json_file, indent=4)
        FileUtil.save_to_json(aggregated_data_path, aggregated_data)
        server_file_dir = os.path.dirname(aggregated_data_path.replace('\\', '/').replace('//', '/').replace(
            self.__app_config["CONTAINER"]["APP_DIR_TEMP_PATH"].replace('\\', '/').replace('//', '/'), ''))
        local_dir = os.path.dirname(aggregated_data_path)
        self._upload_data(f'{local_dir}', f'{server_file_dir}')
        aggregated_data_file_path = server_file_dir + \
            "/"+os.path.basename(aggregated_data_path)
        return aggregated_data_file_path

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

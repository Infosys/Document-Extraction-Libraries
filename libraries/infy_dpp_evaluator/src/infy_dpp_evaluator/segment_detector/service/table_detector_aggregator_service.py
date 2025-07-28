# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#
import os
import json
import datetime
from infy_dpp_evaluator.common.file_util import FileUtil


class TableDetectorAggregatorService:

    def __init__(self, fs_handler, app_config, logger, model_provider_dict):
        self.__logger = logger
        self.__app_config = app_config
        self.__file_sys_handler = fs_handler

        self.__model_provider_name = model_provider_dict.get('provider_name')
        if self.__model_provider_name == '':
            raise Exception(
                'Model provider name is not configured in the config file')
        self.__model_run_version = model_provider_dict.get('model_run_version')
        if self.__model_run_version == '':
            raise Exception(
                'Model version number is not configured in the config file')
        self.__dataset_name_with_version = model_provider_dict.get(
            'dataset_name_with_version')
        if self.__dataset_name_with_version == '':
            raise Exception(
                'Data set name and version is not configured in the config file')
        self.__threshold = model_provider_dict.get('threshold')
        if self.__threshold == '':
            raise Exception(
                'Threshold value is not configured in the config file')

    def transform_records(self, records):
        transformed_records = []
        for record in records:  # Directly iterate over records, assuming it's a list of dicts
            transformed_record = {
                "image_subpath": record.get("image_subpath", ""),
                "object_type": record.get("type", "Table"),
                "bbox_format": "X1,Y1,X2,Y2",
                "bbox": record.get("bbox", []),
                "td_confidence_pct": record.get("td_confidence_pct", 0)
            }
            transformed_records.append(transformed_record)
        return transformed_records

    def aggregate_data_from_folders(self, root_dir, result_data_path) -> list:
        # Metadata should be a dict, not a list
        aggregated_data = {"metadata": {}, "records": []}
        timestamp = datetime.datetime.now().strftime("%d%m%Y_%H%M%S")
        path_separator = "\\"
        metadata = {
            "model_identifier": self.__model_provider_name,
            "model_run_id": timestamp,
            "model_run_version": self.__model_run_version,
            "dataset_name_with_version": self.__dataset_name_with_version,
            "threshold": self.__threshold,
            "root_path": root_dir
        }
        aggregated_data["metadata"] = metadata
        all_records = []
        root_dir = f'{self.__app_config["CONTAINER"]["APP_DIR_TEMP_PATH"]}/{root_dir}'
        for root, dirs, files in os.walk(root_dir):
            if self.__model_provider_name in root:
                for file in files:
                    file_path = os.path.join(root, file)
                    if file_path.endswith('.json'):
                        with open(file_path, 'r') as f:
                            data = json.load(f)
                            data = data.get("table_data", [])
                            image_subpath = os.path.relpath(
                                file_path, root_dir)
                            path_components = image_subpath.split(os.path.sep)
                            path_components[1] = path_components[1].replace(
                                "_files", "")
                            first_two_components = path_components[:2]
                            image_subpath = first_two_components[0] + \
                                path_separator+first_two_components[1]
                            if isinstance(data, dict):
                                data['image_subpath'] = image_subpath
                                all_records.append(data)
                            elif isinstance(data, list):
                                for item in data:
                                    if isinstance(item, dict):
                                        item['image_subpath'] = image_subpath
                                        all_records.append(item)
        aggregated_data["records"] = self.transform_records(all_records)

        # Create the JSON file
        timestamp_for_json = datetime.datetime.now().strftime("%d%m%Y_%H%M%S")
        aggregated_data_path = f"{self.__model_provider_name}_{timestamp_for_json}_extracted_data.json"
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

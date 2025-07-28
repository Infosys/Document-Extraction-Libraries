"""Test module for Docling Table Detector and Extractor Provider"""

# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import os
import json
import pytest
import infy_fs_utils.data
import infy_object_detector
from infy_object_detector.detector.table_detector import TableDetector
from infy_object_detector.common.constants import Constants


STORAGE_ROOT_PATH = f"C:/temp/unittest/infy_object_detector/{__name__}/STORAGE"
CONTAINER_ROOT_PATH = f"C:/temp/unittest/infy_object_detector/{__name__}/CONTAINER"


@pytest.fixture(scope='module', autouse=True)
def setup(create_root_folders, copy_files_to_root_folder) -> dict:
    """Initialization method"""
    create_root_folders([STORAGE_ROOT_PATH, CONTAINER_ROOT_PATH])
    SAMPLE_ROOT_PATH = "./data/sample"
    FILES_TO_COPY = [
        ['*.json', f"{SAMPLE_ROOT_PATH}/input",
            f"{STORAGE_ROOT_PATH}/data/input"],
        ['*.jpg', f"{SAMPLE_ROOT_PATH}/input",
            f"{STORAGE_ROOT_PATH}/data/input"],
        ['*.png', f"{SAMPLE_ROOT_PATH}/input",
            f"{STORAGE_ROOT_PATH}/data/input"],
    ]

    copy_files_to_root_folder(FILES_TO_COPY)
    storage_config_data = infy_fs_utils.data.StorageConfigData(
        **{
            "storage_root_uri": f"file://{STORAGE_ROOT_PATH}",
            "storage_server_url": "",
            "storage_access_key": "",
            "storage_secret_key": ""
        })
    file_sys_handler = infy_fs_utils.provider.FileSystemHandler(
        storage_config_data)
    infy_fs_utils.manager.FileSystemManager().set_root_handler_name(
        Constants.FSH_OBJECT_DETECTOR)
    infy_fs_utils.manager.FileSystemManager().add_fs_handler(file_sys_handler)

    logging_config_data = infy_fs_utils.data.LoggingConfigData(
        **{
            # "logger_group_name": "my_group_1",
            "logging_level": 10,
            "logging_format": "",
            "logging_timestamp_format": "",
            "log_file_data": {
                "log_file_dir_path": "/logs",
                "log_file_name_prefix": "infy_object_detector",
                # "log_file_name_suffix": "1",
                "log_file_extension": ".log"

            }})
    file_sys_logging_handler = infy_fs_utils.provider.FileSystemLoggingHandler(
        logging_config_data, file_sys_handler)
    infy_fs_utils.manager.FileSystemLoggingManager(
    ).set_root_handler_name(Constants.FSLH_OBJECT_DETECTOR)
    infy_fs_utils.manager.FileSystemLoggingManager(
    ).add_fs_logging_handler(file_sys_logging_handler)

    yield
    infy_fs_utils.manager.FileSystemManager().delete_fs_handler()
    infy_fs_utils.manager.FileSystemLoggingManager().delete_fs_logging_handler()


def test_docling_td_tsr():
    """Test the Docling Table Detector and Extractor Provider"""
    ### Make sure the model service is running and urls are working before running this test ###
    image_path = "./data/sample/input/sample_1.png"
    url = f"{os.environ['INFY_MODEL_SERVICE_BASE_URL']}/api/v1/model/docling"
    table_detector_provider = infy_object_detector.detector.provider.DoclingTableTdTsrProvider(
        infy_object_detector.detector.provider.DoclingTableTdTsrProviderConfigData(
            **{
                "model_service_url": url,
                "model_name": "",
                "model_path": "",
                "is_table_html_view": True
            }
        ))

    table_detector = TableDetector(table_detector_provider)
    response = table_detector.detect_table(
        infy_object_detector.detector.provider.DoclingTableTdTsrProviderRequestData(
            **{
                "image_file_path": image_path
            }
        ))
    assert response is not None and response.table_data is not None
    __pretty_print(response.dict())
    # Save the HTML content to a file
    html_file_path = './data/sample/output/docling_table_data.html'
    __save_to_html(response, html_file_path)
    assert response.table_data[0].bbox is not None
    assert response.table_data[1].bbox is not None


def __pretty_print(dictionary):
    p = json.dumps(dictionary, indent=4)
    print(p.replace('\"', '\''))


def __save_to_html(dictionary, file_path):
    if os.path.exists(file_path):
        os.remove(file_path)
    html_content = ""
    for table in dictionary.table_html_data:
        html_content = html_content + table.cell_data_html
    with open(file_path, 'w') as file:
        file.write(html_content)

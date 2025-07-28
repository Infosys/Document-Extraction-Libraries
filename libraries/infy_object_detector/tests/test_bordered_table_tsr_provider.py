"""Test module for Bordered Table Extractor Provider"""

# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import os
import json
import pytest
import infy_fs_utils.data
import infy_table_extractor as ite
from infy_object_detector.common.constants import Constants
from infy_object_detector.structure_recogniser.provider.bordered_table_tsr_provider import (
    BorderedTableTsrProviderConfigData, BorderedTableTsrProvider, BorderedTableTsrProviderRequestData)


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


def test_bordered_table_extractor_rgb_ld_infy_ocr_engine():
    """test method for bordered table extractor using RGB line detect"""
    config_param_dict: dict = {
        'custom_cells': [{'rows': [], 'columns': []}],
        'col_header': {'use_first_row': True, 'values': []},
        'deskew_image_reqd': False,
        'auto_detect_border': False,
        'image_cell_cleanup_reqd': True,
        'output': {
            'path': None,
            'format': None
        },
        'rgb_line_skew_detection_method': [ite.interface.RgbSkewDetectionMethod.CONVOLUTION_CONTRAST_METHOD],
        'line_detection_method': [ite.interface.LineDetectionMethod.RGB_LINE_DETECT]
    }

    bordered_table_extractor_provider_config_data = BorderedTableTsrProviderConfigData(
        **{
            "model_path": "",
            "model_name": "",
            "ocr_engine_exe_dir_path": "C:/MyProgramFiles/InfyOcrEngine",
            "ocr_engine_model_dir_path": "C:/MyProgramFiles/AI/models/tessdata",
            "method_name": "rgb",
            "temp_folder_path": "C:/temp/",
            "config_param_dict": config_param_dict

        })

    provider = BorderedTableTsrProvider(
        bordered_table_extractor_provider_config_data)
    table_request_data = BorderedTableTsrProviderRequestData(
        image_file_path='./data/sample/input/sample_1.png',
        bbox=[73, 2001, 4009, 937])  # bbox format -> [x1, y1, width, height]
    response = provider.extract_table_data(table_request_data)
    assert response is not None and response.table_data is not None
    __pretty_print(response.dict())
    # Save the HTML content to a file
    html_file_path = './data/sample/output/rgb_ld_ioe_table_data.html'
    __save_to_html(response, html_file_path)


def test_bordered_table_extractor_opencv_ld_infy_ocr_engine():
    """test method for bordered table extractor using OpenCV line detect"""
    config_param_dict = {
        'col_header': {
            'use_first_row': True,
        },
        'line_detection_method': [ite.interface.LineDetectionMethod.OPENCV_LINE_DETECT]
    }

    bordered_table_extractor_provider_config_data = BorderedTableTsrProviderConfigData(
        **{
            "model_path": "",
            "model_name": "",
            "ocr_engine_exe_dir_path": "C:/MyProgramFiles/InfyOcrEngine",
            "ocr_engine_model_dir_path": "C:/MyProgramFiles/AI/models/tessdata",
            "method_name": "opencv",
            "temp_folder_path": "C:/temp/",
            "config_param_dict": config_param_dict

        })

    provider = BorderedTableTsrProvider(
        bordered_table_extractor_provider_config_data)
    table_request_data = BorderedTableTsrProviderRequestData(
        image_file_path='./data/sample/input/sample_1.png',
        bbox=[73, 2001, 4009, 937])  # bbox format -> [x1, y1, width, height]
    response = provider.extract_table_data(table_request_data)
    assert response is not None and response.table_data is not None
    assert response.table_html_data is not None
    __pretty_print(response.dict())
    # Save the HTML content to a file
    html_file_path = './data/sample/output/opencv_ld_ioe_table_data.html'
    __save_to_html(response, html_file_path)


def test_bordered_table_extractor_opencv_ld_tesseract():
    """test method for bordered table extractor using OpenCV line detect"""
    config_param_dict = {
        'col_header': {
            'use_first_row': True,
        },
        'line_detection_method': [ite.interface.LineDetectionMethod.OPENCV_LINE_DETECT]
    }

    bordered_table_extractor_provider_config_data = BorderedTableTsrProviderConfigData(
        **{
            "model_path": "C:/MyProgramFiles/Tesseract-OCR/tesseract.exe",
            "model_name": "Tesseract",
            "ocr_engine_exe_dir_path": "",
            "ocr_engine_model_dir_path": "",
            "method_name": "opencv",
            "temp_folder_path": "C:/temp/",
            "config_param_dict": config_param_dict

        })

    provider = BorderedTableTsrProvider(
        bordered_table_extractor_provider_config_data)
    table_request_data = BorderedTableTsrProviderRequestData(
        image_file_path='./data/sample/input/sample_1.png',
        bbox=[73, 2001, 4009, 937])  # bbox format -> [x1, y1, width, height]
    response = provider.extract_table_data(table_request_data)
    assert response is not None and response.table_data is not None
    assert response.table_html_data is not None
    __pretty_print(response.dict())
    # Save the HTML content to a file
    html_file_path = './data/sample/output/opencv_ld_tess_table_data.html'
    __save_to_html(response, html_file_path)


def test_bordered_table_extractor_rgb_ld_tesseract():
    """test method for bordered table extractor using RGB line detect"""
    config_param_dict: dict = {
        'custom_cells': [{'rows': [], 'columns': []}],
        'col_header': {'use_first_row': True, 'values': []},
        'deskew_image_reqd': False,
        'auto_detect_border': False,
        'image_cell_cleanup_reqd': True,
        'output': {
            'path': None,
            'format': None
        },
        'rgb_line_skew_detection_method': [ite.interface.RgbSkewDetectionMethod.CONVOLUTION_CONTRAST_METHOD],
        'line_detection_method': [ite.interface.LineDetectionMethod.RGB_LINE_DETECT]
    }

    bordered_table_extractor_provider_config_data = BorderedTableTsrProviderConfigData(
        **{
            "model_path": "C:/MyProgramFiles/Tesseract-OCR/tesseract.exe",
            "model_name": "Tesseract",
            "ocr_engine_exe_dir_path": "",
            "ocr_engine_model_dir_path": "",
            "method_name": "rgb",
            "temp_folder_path": "C:/temp/",
            "config_param_dict": config_param_dict

        })

    provider = BorderedTableTsrProvider(
        bordered_table_extractor_provider_config_data)
    table_request_data = BorderedTableTsrProviderRequestData(
        image_file_path='./data/sample/input/sample_1.png',
        bbox=[73, 2001, 4009, 937])  # bbox format -> [x1, y1, width, height]
    response = provider.extract_table_data(table_request_data)
    assert response is not None and response.table_data is not None
    __pretty_print(response.dict())
    # Save the HTML content to a file
    html_file_path = './data/sample/output/rgb_ld_tess_table_data.html'
    __save_to_html(response, html_file_path)


def __pretty_print(dictionary):
    p = json.dumps(dictionary, indent=4)
    print(p.replace('\"', '\''))


def __save_to_html(dictionary, file_path):
    if os.path.exists(file_path):
        os.remove(file_path)
    html_content = dictionary.table_html_data[0].cell_data_html
    with open(file_path, 'w') as file:
        file.write(html_content)

# ===============================================================================================================#
# Copyright 2021 Infosys Ltd.
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at
# http://www.apache.org/licenses/                                                    #
# ===============================================================================================================#

import os
import json
import logging
from infy_bordered_table_extractor import bordered_table_extractor
from infy_bordered_table_extractor.bordered_table_extractor import OutputFileFormat
from infy_bordered_table_extractor.providers.tesseract_data_service_provider import TesseractDataServiceProvider
from infy_bordered_table_extractor.bordered_table_extractor import LineDetectionMethod


def __create_new_instance():
    if not os.path.exists("./logs"):
        os.makedirs("./logs")
    logging.basicConfig(
        filename=("./logs" + "/app_log.log"),
        format="%(asctime)s- %(levelname)s- %(message)s",
        level=logging.INFO,
        datefmt="%d-%b-%y %H:%M:%S",
    )
    logger = logging.getLogger()
    TESSERACT_PATH = os.environ['TESSERACT_PATH']
    provider = TesseractDataServiceProvider(TESSERACT_PATH)
    # input files path
    temp_folderpath = './data/temp'
    img_filepath = os.path.abspath(
        './data/sample_1.png')
    table_object = bordered_table_extractor.BorderedTableExtractor(
        provider, provider, temp_folderpath, logger, True)

    return table_object, img_filepath


def test_bordered_table_extractor_bbox_RGBLineDetect():
    """test method"""
    table_object, img_filepath = __create_new_instance()
    save_folder_path = os.path.abspath('./data/output')
    if not os.path.exists(save_folder_path):
        os.makedirs(save_folder_path)
    result = table_object.extract_all_fields(
        img_filepath, within_bbox=[73, 2001, 4009, 937], config_param_dict={
            'output': {'path': save_folder_path,
                       'format': [OutputFileFormat.EXCEL]}
        }
    )
    __pretty_print(result)
    assert result['error'] is None
    assert __get_summary(result) == {
        'table_count': 1,
        'row_count': 5,
        'col_count': [4, 4, 4, 4, 4]
    }


def test_bordered_table_extractor_bbox_OpenCVLineDetect():
    """test method"""
    table_object, img_filepath = __create_new_instance()

    result = table_object.extract_all_fields(
        img_filepath, within_bbox=[73, 2001, 4009, 937],
        config_param_dict={'line_detection_method': [
            LineDetectionMethod.OPENCV_LINE_DETECT]})

    __pretty_print(result)
    assert result['error'] is None
    assert __get_summary(result) == {
        'table_count': 1,
        'row_count': 5,
        'col_count': [4, 4, 4, 4, 4]
    }


def test_bordered_table_extractor_with_custom_cells():
    """test method"""
    table_object, img_filepath = __create_new_instance()
    result = table_object.extract_all_fields(
        img_filepath, within_bbox=[73, 2001, 4009, 937],
        config_param_dict={
            'custom_cells': [
                {'rows': [1], 'columns':[1]}, {'rows': [2], 'columns':[2]}]
        }
    )
    __pretty_print(result)
    assert result['error'] is None
    assert __get_summary(result) == {
        'table_count': 1,
        'row_count': 2,
        'col_count': [3, 3]
    }


def __get_summary(api_result):
    row_count = -1
    col_counts = []
    for table in api_result['fields']:
        rows = table['table_value']
        row_count = len(rows)
        for row in rows:
            col_counts.append(len(row))

    return {
        'table_count': len(api_result['fields']),
        'row_count': row_count,
        'col_count': col_counts
    }


def __pretty_print(dictionary):
    p = json.dumps(dictionary, indent=4)
    print(p.replace('\"', '\''))

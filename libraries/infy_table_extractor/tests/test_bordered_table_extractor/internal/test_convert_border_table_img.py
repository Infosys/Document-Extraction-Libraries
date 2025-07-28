# ===============================================================================================================#
# Copyright 2020 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import os
import json
import datetime
import logging
import pytest

import infy_table_extractor as ite

INFY_SP_ROOT_PATH = os.environ['INFY_SP_ROOT_PATH']
UNIT_TEST_DATA_LOCATION = INFY_SP_ROOT_PATH + \
    "\\workbenchlibraries - Documents\\SHARED_DATA\\unit_test_data\\infy_table_extractor\\bordered_table"


class ConfigData():
    """Variable declaration"""
    save_folder_path = None
    table_object = None
    config_param_dict = None


@pytest.fixture(scope='module', autouse=True)
def pre_test():
    """Initialization method"""

    # Logging configuration
    log_folder = os.path.abspath('./logs')
    if not os.path.exists(log_folder):
        os.makedirs(log_folder)
    LOG_LEVEL = logging.DEBUG
    LOG_FORMAT = logging.Formatter(
        '%(asctime)s.%(msecs)03d %(levelname)s [%(module)s] [%(funcName)s:%(lineno)d] %(message)s')

    date = datetime.datetime.now().strftime("%Y%m%d")
    logfilename = f'{log_folder}/bordered_table_log_{date}.log'

    logger = logging.getLogger(__name__)
    logger.setLevel(LOG_LEVEL)
    fileHandler = logging.FileHandler(logfilename)
    fileHandler.setLevel(LOG_LEVEL)
    fileHandler.setFormatter(LOG_FORMAT)
    logger.addHandler(fileHandler)

    logger.info('Initialization Completed')

    # creating instance of provider
    TESSERACT_PATH = os.environ['TESSERACT_PATH']
    provider = ite.bordered_table_extractor.providers.TesseractDataServiceProvider(
        TESSERACT_PATH)
    # input files path
    save_folder_path = os.path.abspath('./data/output')
    temp_folderpath = './data/temp'
    table_object = ite.bordered_table_extractor.BorderedTableExtractor(
        provider, provider, temp_folderpath, logger, True)

    config_param_dict = {}

    ConfigData.config_param_dict = config_param_dict
    ConfigData.table_object = table_object


def test_bordered_table_extractor_PO():
    input_path_imgfile1 = os.path.abspath(
        './data/input/PO-Upgrade.jpg')
    input_path = input_path_imgfile1

    result = ConfigData.table_object.extract_all_fields(
        input_path)
    __pretty_print(result)
    assert result['error'] is None
    assert __get_summary(result) == {
        'table_count': 1,
        'row_count': 3,
        'col_count': [7, 7, 7]
    }


def test_bordered_table_extractor_PO_modified():
    input_path_imgfile1 = os.path.abspath(
        './data/input/PO-Upgrade_modified.jpg')
    input_path = input_path_imgfile1

    result = ConfigData.table_object.extract_all_fields(
        input_path)
    __pretty_print(result)
    assert result['error'] is None


def test_bordered_table_extractor_1():
    input_path_imgfile1 = os.path.abspath(
        './data/input/table1.jpg')
    input_path = input_path_imgfile1

    result = ConfigData.table_object.extract_all_fields(
        input_path)
    __pretty_print(result)
    assert result['error'] is None
    assert __get_summary(result) == {
        'table_count': 1,
        'row_count': 5,
        'col_count': [2, 2, 2, 2, 2]
    }


def test_bordered_table_extractor_1_modified():
    input_path_imgfile1 = os.path.abspath(
        './data/input/table1_modified.jpg')
    input_path = input_path_imgfile1

    result = ConfigData.table_object.extract_all_fields(
        input_path)
    __pretty_print(result)
    assert result['error'] is None


def test_bordered_table_extractor_2():
    input_path_imgfile1 = os.path.abspath(
        './data/input/table2.jpg')
    input_path = input_path_imgfile1

    result = ConfigData.table_object.extract_all_fields(
        input_path)
    __pretty_print(result)
    assert result['error'] is None
    assert __get_summary(result) == {
        'table_count': 1,
        'row_count': 4,
        'col_count': [5, 5, 5, 5]
    }


def test_bordered_table_extractor_3():
    input_path_imgfile1 = os.path.abspath(
        './data/input/table3.jpg')
    input_path = input_path_imgfile1

    result = ConfigData.table_object.extract_all_fields(
        input_path)
    __pretty_print(result)
    assert result['error'] is None


def test_bordered_table_extractor_4():
    input_path_imgfile1 = os.path.abspath(
        './data/input/table4.jpg')
    input_path = input_path_imgfile1

    result = ConfigData.table_object.extract_all_fields(
        input_path)
    __pretty_print(result)
    assert result['error'] is None


def test_bordered_table_extractor_5():
    input_path_imgfile1 = os.path.abspath(
        './data/input/table5.jpg')
    input_path = input_path_imgfile1

    result = ConfigData.table_object.extract_all_fields(
        input_path)
    __pretty_print(result)
    assert result['error'] is None


def test_bordered_table_extractor_6():
    input_path_imgfile1 = os.path.abspath(
        './data/input/table6.jpg')
    input_path = input_path_imgfile1

    result = ConfigData.table_object.extract_all_fields(
        input_path)
    __pretty_print(result)
    assert result['error'] is None


def test_bordered_table_extractor_7():
    input_path_imgfile1 = os.path.abspath(
        './data/input/table7.jpg')
    input_path = input_path_imgfile1

    result = ConfigData.table_object.extract_all_fields(
        input_path)
    __pretty_print(result)
    assert result['error'] is None


def test_bordered_table_extractor_8():
    input_path_imgfile1 = os.path.abspath(
        './data/input/table8.jpg')
    input_path = input_path_imgfile1

    result = ConfigData.table_object.extract_all_fields(
        input_path)
    assert result['error'] is None


def test_bordered_table_extractor_9():
    input_path_imgfile1 = os.path.abspath(
        './data/input/table9.jpg')
    input_path = input_path_imgfile1

    result = ConfigData.table_object.extract_all_fields(
        input_path)
    assert result['error'] is None


def test_bordered_table_extractor_10():
    input_path_imgfile1 = os.path.abspath(
        './data/input/table10.jpg')
    input_path = input_path_imgfile1

    result = ConfigData.table_object.extract_all_fields(
        input_path)
    assert result['error'] is None


def test_bordered_table_extractor_11():
    input_path_imgfile1 = os.path.abspath(
        './data/input/table11.jpg')
    input_path = input_path_imgfile1

    result = ConfigData.table_object.extract_all_fields(
        input_path)
    assert result['error'] is None


def test_bordered_table_extractor_12():
    input_path_imgfile1 = os.path.abspath(
        './data/input/table12.jpg')
    input_path = input_path_imgfile1

    result = ConfigData.table_object.extract_all_fields(
        input_path)
    assert result['error'] is None


def test_bordered_table_extractor_13():
    input_path_imgfile1 = os.path.abspath(
        './data/input/table13.jpg')
    input_path = input_path_imgfile1

    result = ConfigData.table_object.extract_all_fields(
        input_path)
    __pretty_print(result)
    assert result['error'] is None


def test_bordered_table_extractor_within_bbox():
    input_path_imgfile1 = os.path.abspath(
        fr"{UNIT_TEST_DATA_LOCATION}\aa-doc\aa-doc-files\1.jpg")
    input_path = input_path_imgfile1

    result = ConfigData.table_object.extract_all_fields(
        input_path, within_bbox=[1716, 1298, 689, 765])
    __pretty_print(result)
    assert result['error'] is None
    assert __get_summary(result) == {
        'table_count': 1,
        'row_count': 14,
        'col_count': [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2]
    }


# added on 29/09/22


def test_bordered_table_extractor_within_bbox_exact_border():
    input_path_imgfile1 = os.path.abspath(
        fr"{UNIT_TEST_DATA_LOCATION}\sample_01.jpg")

    input_path = input_path_imgfile1

    result = ConfigData.table_object.extract_all_fields(
        input_path, within_bbox=[75, 247, 1933, 282])
    __pretty_print(result)
    assert result['error'] is None
    assert __get_summary(result) == {
        'table_count': 1,
        'row_count': 5,
        'col_count': [5, 5, 5, 5, 5]
    }

# added on 29/09/22


def test_bordered_table_extractor_rgb_line_detect_within_bbox_larger_border_1():
    input_path_imgfile1 = os.path.abspath(
        fr"{UNIT_TEST_DATA_LOCATION}\sample_01.jpg")

    input_path = input_path_imgfile1
    config_param_dict = {
        'col_header': {
            'use_first_row': True,
            'values': []
        },
        'line_detection_method': [ite.interface.LineDetectionMethod.RGB_LINE_DETECT],
        'auto_detect_border': True
    }

    result = ConfigData.table_object.extract_all_fields(
        input_path, within_bbox=[75, 247, 1933, 380],
        config_param_dict=config_param_dict)

    __pretty_print(result)
    assert result['error'] is None
    assert __get_summary(result) == {
        'table_count': 1,
        'row_count': 5,
        'col_count': [5, 5, 5, 5, 5]
    }

# added on 29/09/22


def test_bordered_table_extractor_rgb_line_detect_within_bbox_larger_border_2():
    input_path_imgfile1 = os.path.abspath(
        fr"{UNIT_TEST_DATA_LOCATION}\sample_01.jpg")

    input_path = input_path_imgfile1
    config_param_dict = {
        'col_header': {
            'use_first_row': True,
            'values': []
        },
        'line_detection_method': [ite.interface.LineDetectionMethod.RGB_LINE_DETECT],
        'auto_detect_border': True
    }
    result = ConfigData.table_object.extract_all_fields(
        input_path, within_bbox=[0, 0, 2124, 824],
        config_param_dict=config_param_dict)

    __pretty_print(result)
    assert result['error'] is None
    assert __get_summary(result) == {
        'table_count': 1,
        'row_count': 5,
        'col_count': [5, 5, 5, 5, 5]
    }

# added on 29/09/22


def test_bordered_table_extractor_rgb_line_detect_within_bbox_no_outer_border():
    input_path_imgfile1 = os.path.abspath(
        fr"{UNIT_TEST_DATA_LOCATION}\sample_01.jpg")

    input_path = input_path_imgfile1
    config_param_dict = {
        'col_header': {
            'use_first_row': True,
            'values': []
        },
        'line_detection_method': [ite.interface.LineDetectionMethod.RGB_LINE_DETECT],
        'auto_detect_border': True
    }
    result = ConfigData.table_object.extract_all_fields(
        input_path, within_bbox=[85, 255, 1910, 270],
        config_param_dict=config_param_dict)

    __pretty_print(result)
    assert result['error'] is None
    assert __get_summary(result) == {
        'table_count': 1,
        'row_count': 5,
        'col_count': [5, 5, 5, 5, 5]
    }

# added on 29/09/22


def test_bordered_table_extractor_rgb_line_detect_without_bbox():
    input_path_imgfile1 = os.path.abspath(
        fr"{UNIT_TEST_DATA_LOCATION}\sample_01.jpg")

    input_path = input_path_imgfile1
    config_param_dict = {
        'col_header': {
            'use_first_row': True,
            'values': []
        },
        'line_detection_method': [ite.interface.LineDetectionMethod.RGB_LINE_DETECT],
        'auto_detect_border': True
    }
    result = ConfigData.table_object.extract_all_fields(
        input_path, within_bbox=None,
        config_param_dict=config_param_dict)

    __pretty_print(result)
    assert result['error'] is None
    assert __get_summary(result) == {
        'table_count': 1,
        'row_count': 5,
        'col_count': [5, 5, 5, 5, 5]
    }

# added on 29/09/22


def test_bordered_table_extractor_opencv_line_detect_within_bbox_exact_border():
    input_path_imgfile1 = os.path.abspath(
        fr"{UNIT_TEST_DATA_LOCATION}\sample_01.jpg")

    input_path = input_path_imgfile1
    config_param_dict = {
        'col_header': {
            'use_first_row': True,
            'values': []
        },
        'line_detection_method': [ite.interface.LineDetectionMethod.OPENCV_LINE_DETECT],
        'auto_detect_border': True
    }
    result = ConfigData.table_object.extract_all_fields(
        input_path, within_bbox=[0, 0, 2124, 824],
        config_param_dict=config_param_dict)

    __pretty_print(result)
    assert result['error'] is None
    assert __get_summary(result) == {
        'table_count': 1,
        'row_count': 5,
        'col_count': [5, 5, 5, 5, 5]
    }

# added on 29/09/22


def test_bordered_table_extractor_opencv_line_detect_within_bbox_larger_border():
    input_path_imgfile1 = os.path.abspath(
        fr"{UNIT_TEST_DATA_LOCATION}\sample_01.jpg")

    input_path = input_path_imgfile1
    config_param_dict = {
        'col_header': {
            'use_first_row': True,
            'values': []
        },
        'line_detection_method': [ite.interface.LineDetectionMethod.OPENCV_LINE_DETECT],
        'auto_detect_border': True
    }
    result = ConfigData.table_object.extract_all_fields(
        input_path, within_bbox=[0, 0, 2124, 824],
        config_param_dict=config_param_dict)

    __pretty_print(result)
    assert result['error'] is None
    assert __get_summary(result) == {
        'table_count': 1,
        'row_count': 5,
        'col_count': [5, 5, 5, 5, 5]
    }

# added on 29/09/22


def test_bordered_table_extractor_opencv_line_detect_within_bbox_no_border():
    input_path_imgfile1 = os.path.abspath(
        fr"{UNIT_TEST_DATA_LOCATION}\sample_01.jpg")

    input_path = input_path_imgfile1
    config_param_dict = {
        'col_header': {
            'use_first_row': True,
            'values': []
        },
        'line_detection_method': [ite.interface.LineDetectionMethod.OPENCV_LINE_DETECT],
        'auto_detect_border': True
    }
    result = ConfigData.table_object.extract_all_fields(
        input_path, within_bbox=[85, 255, 1910, 270],
        config_param_dict=config_param_dict)

    __pretty_print(result)
    assert result['error'] is None
    assert __get_summary(result) == {
        'table_count': 1,
        'row_count': 5,
        'col_count': [5, 5, 5, 5, 5]
    }

# added on 29/09/22


def test_bordered_table_extractor_opencv_line_detect_without_bbox():
    input_path_imgfile1 = os.path.abspath(
        fr"{UNIT_TEST_DATA_LOCATION}\sample_01.jpg")

    input_path = input_path_imgfile1
    config_param_dict = {
        'col_header': {
            'use_first_row': True,
            'values': []
        },
        'line_detection_method': [ite.interface.LineDetectionMethod.OPENCV_LINE_DETECT],
        'auto_detect_border': True
    }
    result = ConfigData.table_object.extract_all_fields(
        input_path, within_bbox=None,
        config_param_dict=config_param_dict)

    __pretty_print(result)
    assert result['error'] is None
    assert __get_summary(result) == {
        'table_count': 1,
        'row_count': 5,
        'col_count': [5, 5, 5, 5, 5]
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

# ===============================================================================================================#
# Copyright 2020 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import json
import os
import datetime
import logging
import pytest
import infy_table_extractor as ite

INFY_SP_ROOT_PATH = os.environ['INFY_SP_ROOT_PATH']
UNIT_TEST_DATA_LOCATION = INFY_SP_ROOT_PATH + \
    "\\workbenchlibraries - Documents\\SHARED_DATA\\unit_test_data\\infy_table_extractor\\bordered_table"


class ConfigData():
    """Variable declaration"""
    img_file_path_prefix = None
    save_folder_path = None
    table_object = None
    config_param_dict = None


@pytest.fixture(scope='module', autouse=True)
def pre_test():
    """Initialization method"""

    TESSERACT_PATH = os.environ['TESSERACT_PATH']
    img_file_path_prefix = fr'{UNIT_TEST_DATA_LOCATION}\c-firefight'

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

    # input files path
    provider = ite.bordered_table_extractor.providers.TesseractDataServiceProvider(
        TESSERACT_PATH, None, LOG_LEVEL)
    save_folder_path = os.path.abspath('./data/output')
    temp_folderpath = './data/temp'
    table_object = ite.bordered_table_extractor.BorderedTableExtractor(
        provider, provider, temp_folderpath, logger, True)

    config_param_dict = {
        'line_detection_method': [ite.interface.LineDetectionMethod.RGB_LINE_DETECT]
    }

    ConfigData.img_file_path_prefix = img_file_path_prefix
    ConfigData.save_folder_path = save_folder_path
    ConfigData.table_object = table_object
    ConfigData.config_param_dict = config_param_dict


def test_bordered_table_extractor_c_1():
    """Test method"""
    input_path_imgfile1 = ConfigData.img_file_path_prefix + '/c_table_01.png'
    input_path = input_path_imgfile1
    result = ConfigData.table_object.extract_all_fields(
        image_file_path=input_path,
        config_param_dict={'image_cell_cleanup_reqd': True,
                           'line_detection_method': [ite.interface.LineDetectionMethod.OPENCV_LINE_DETECT]})

    __pretty_print(result)
    assert result['error'] is None


def test_bordered_table_extractor_c_2():
    """Test method"""
    input_path_imgfile1 = ConfigData.img_file_path_prefix + '/c_table_02.png'
    input_path = input_path_imgfile1
    result = ConfigData.table_object.extract_all_fields(
        image_file_path=input_path, config_param_dict=ConfigData.config_param_dict
    )
    __pretty_print(result)
    assert result['error'] is None


def test_bordered_table_extractor_c_3():
    """Test method"""
    input_path_imgfile1 = ConfigData.img_file_path_prefix + '/c_table_03.png'
    input_path = input_path_imgfile1

    result = ConfigData.table_object.extract_all_fields(
        image_file_path=input_path, config_param_dict=ConfigData.config_param_dict
    )
    __pretty_print(result)
    assert result['error'] is None


def test_bordered_table_extractor_c_4():
    """Test method"""
    input_path_imgfile1 = ConfigData.img_file_path_prefix + '/c_table_04.png'
    input_path = input_path_imgfile1

    result = ConfigData.table_object.extract_all_fields(
        image_file_path=input_path, config_param_dict=ConfigData.config_param_dict
    )
    __pretty_print(result)
    assert result['error'] is None


def test_bordered_table_extractor_c_5():
    """Test method"""
    input_path_imgfile1 = ConfigData.img_file_path_prefix + '/c_table_05.png'
    input_path = input_path_imgfile1

    result = ConfigData.table_object.extract_all_fields(
        image_file_path=input_path, config_param_dict=ConfigData.config_param_dict
    )
    __pretty_print(result)
    assert result['error'] is None


def test_bordered_table_extractor_c_6():
    """Test method"""
    input_path_imgfile1 = ConfigData.img_file_path_prefix + '/c_table_06.png'
    input_path = input_path_imgfile1

    result = ConfigData.table_object.extract_all_fields(
        image_file_path=input_path, config_param_dict=ConfigData.config_param_dict
    )
    __pretty_print(result)
    assert result['error'] is None


def test_bordered_table_extractor_c_7():
    """Test method"""
    input_path_imgfile1 = ConfigData.img_file_path_prefix + '/c_table_7.png'
    input_path = input_path_imgfile1

    result = ConfigData.table_object.extract_all_fields(
        image_file_path=input_path, config_param_dict=ConfigData.config_param_dict
    )
    __pretty_print(result)
    assert result['error'] is None


def test_bordered_table_extractor_c_8():
    """Test method"""
    input_path_imgfile1 = ConfigData.img_file_path_prefix + '/c_table_8.png'
    input_path = input_path_imgfile1

    result = ConfigData.table_object.extract_all_fields(
        image_file_path=input_path, config_param_dict=ConfigData.config_param_dict
    )
    __pretty_print(result)
    assert result['error'] is None


def test_bordered_table_extractor_c_9():
    """Test method"""
    input_path_imgfile1 = ConfigData.img_file_path_prefix + '/c_table_9.png'
    input_path = input_path_imgfile1

    result = ConfigData.table_object.extract_all_fields(
        image_file_path=input_path, config_param_dict=ConfigData.config_param_dict
    )
    __pretty_print(result)
    assert result['error'] is None


def test_bordered_table_extractor_c_10():
    """Test method"""
    input_path_imgfile1 = ConfigData.img_file_path_prefix + '/c_table_10.png'
    input_path = input_path_imgfile1

    result = ConfigData.table_object.extract_all_fields(
        image_file_path=input_path, config_param_dict=ConfigData.config_param_dict
    )
    __pretty_print(result)
    assert result['error'] is None


def test_bordered_table_extractor_c_11():
    """Test method"""
    input_path_imgfile1 = ConfigData.img_file_path_prefix + '/c_table_11.png'
    input_path = input_path_imgfile1

    result = ConfigData.table_object.extract_all_fields(
        image_file_path=input_path, config_param_dict=ConfigData.config_param_dict
    )
    __pretty_print(result)
    assert result['error'] is None


def test_bordered_table_extractor_c_12():
    """Test method"""
    input_path_imgfile1 = ConfigData.img_file_path_prefix + '/c_table_12.png'
    input_path = input_path_imgfile1

    result = ConfigData.table_object.extract_all_fields(
        image_file_path=input_path, config_param_dict=ConfigData.config_param_dict
    )
    __pretty_print(result)
    assert result['error'] is None


def test_bordered_table_extractor_c_13():
    """Test method"""
    input_path_imgfile1 = ConfigData.img_file_path_prefix + '/c_table_13.png'
    input_path = input_path_imgfile1

    result = ConfigData.table_object.extract_all_fields(
        image_file_path=input_path, config_param_dict=ConfigData.config_param_dict
    )
    __pretty_print(result)
    assert result['error'] is None


def test_bordered_table_extractor_c_14():
    """Test method"""
    input_path_imgfile1 = ConfigData.img_file_path_prefix + '/c_table_14.png'
    input_path = input_path_imgfile1

    result = ConfigData.table_object.extract_all_fields(
        image_file_path=input_path, config_param_dict=ConfigData.config_param_dict
    )
    __pretty_print(result)
    assert result['error'] is None


def test_bordered_table_extractor_c_15():
    """Test method"""
    input_path_imgfile1 = ConfigData.img_file_path_prefix + '/c_table_15.png'
    input_path = input_path_imgfile1

    result = ConfigData.table_object.extract_all_fields(
        image_file_path=input_path, config_param_dict=ConfigData.config_param_dict
    )
    __pretty_print(result)
    assert result['error'] is None


def test_bordered_table_extractor_c_16():
    """Test method"""
    input_path_imgfile1 = ConfigData.img_file_path_prefix + '/c_table_16.png'
    input_path = input_path_imgfile1

    result = ConfigData.table_object.extract_all_fields(
        image_file_path=input_path, config_param_dict=ConfigData.config_param_dict
    )
    __pretty_print(result)
    assert result['error'] is None


def test_bordered_table_extractor_c_17():
    """Test method"""
    input_path_imgfile1 = ConfigData.img_file_path_prefix + '/c_table_17.png'
    input_path = input_path_imgfile1

    result = ConfigData.table_object.extract_all_fields(
        image_file_path=input_path, config_param_dict=ConfigData.config_param_dict
    )
    __pretty_print(result)
    assert result['error'] is None


def test_bordered_table_extractor_c_18():
    """Test method"""
    input_path_imgfile1 = ConfigData.img_file_path_prefix + '/c_table_18.png'
    input_path = input_path_imgfile1

    result = ConfigData.table_object.extract_all_fields(
        image_file_path=input_path, config_param_dict=ConfigData.config_param_dict
    )
    __pretty_print(result)
    assert result['error'] is None


def test_bordered_table_extractor_c_19():
    """Test method"""
    input_path_imgfile1 = ConfigData.img_file_path_prefix + '/c_table_19.png'
    input_path = input_path_imgfile1

    result = ConfigData.table_object.extract_all_fields(
        image_file_path=input_path, config_param_dict=ConfigData.config_param_dict
    )
    __pretty_print(result)
    assert result['error'] is None


def test_bordered_table_extractor_c_20():
    """Test method"""
    input_path_imgfile1 = ConfigData.img_file_path_prefix + '/c_table_20.png'
    input_path = input_path_imgfile1

    result = ConfigData.table_object.extract_all_fields(
        image_file_path=input_path, config_param_dict=ConfigData.config_param_dict
    )
    __pretty_print(result)
    assert result['error'] is None


def test_bordered_table_extractor_c_21():
    """Test method"""
    input_path_imgfile1 = ConfigData.img_file_path_prefix + '/c_table_21.png'
    input_path = input_path_imgfile1

    result = ConfigData.table_object.extract_all_fields(
        image_file_path=input_path, config_param_dict=ConfigData.config_param_dict
    )
    __pretty_print(result)
    assert result['error'] is None


def test_bordered_table_extractor_c_22():
    """Test method"""
    input_path_imgfile1 = ConfigData.img_file_path_prefix + '/c_table_22.png'
    input_path = input_path_imgfile1

    result = ConfigData.table_object.extract_all_fields(
        image_file_path=input_path, config_param_dict=ConfigData.config_param_dict
    )
    __pretty_print(result)
    assert result['error'] is None


def test_bordered_table_extractor_c_23():
    """Test method"""
    input_path_imgfile1 = ConfigData.img_file_path_prefix + '/c_table_23.png'
    input_path = input_path_imgfile1

    result = ConfigData.table_object.extract_all_fields(
        image_file_path=input_path, config_param_dict=ConfigData.config_param_dict
    )
    __pretty_print(result)
    assert result['error'] is None


def test_bordered_table_extractor_c_24():
    """Test method"""
    input_path_imgfile1 = ConfigData.img_file_path_prefix + '/c_table_24.png'
    input_path = input_path_imgfile1

    result = ConfigData.table_object.extract_all_fields(
        image_file_path=input_path, config_param_dict=ConfigData.config_param_dict
    )
    __pretty_print(result)
    assert result['error'] is None


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

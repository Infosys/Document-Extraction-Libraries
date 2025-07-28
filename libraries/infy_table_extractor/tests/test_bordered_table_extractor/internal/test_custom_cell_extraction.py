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


class ConfigData():
    """Variable declaration"""
    save_folder_path = None
    table_object = None


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
        TESSERACT_PATH, logger)
    # input files path
    save_folder_path = os.path.abspath('./data/output')
    temp_folderpath = './data/temp'
    table_object = ite.bordered_table_extractor.BorderedTableExtractor(
        provider, provider, temp_folderpath, logger, True)

    ConfigData.save_folder_path = save_folder_path
    ConfigData.table_object = table_object


def test_bordered_table_extractor_1():
    config_params_dict = {
        'custom_cells': [{'rows': [2], 'columns':[1]}]
    }
    input_path_imgfile1 = os.path.abspath(
        './data/input/table8.jpg')
    input_path = input_path_imgfile1
    result = ConfigData.table_object.extract_all_fields(
        input_path, config_param_dict=config_params_dict)
    __pretty_print(result)
    assert result['error'] is None


def test_bordered_table_extractor_2():
    config_params_dict = {
        'custom_cells': []
    }
    input_path_imgfile1 = os.path.abspath(
        './data/input/table8.jpg')
    input_path = input_path_imgfile1
    result = ConfigData.table_object.extract_all_fields(
        input_path, config_param_dict=config_params_dict)
    __pretty_print(result)
    assert result['error'] is None


def test_bordered_table_extractor_3():
    config_params_dict = {
        'custom_cells': [
            {'rows': [1], 'columns':[1]}, {'rows': [2], 'columns':[2]}]
    }
    input_path_imgfile1 = os.path.abspath(
        './data/input/table8.jpg')
    input_path = input_path_imgfile1
    result = ConfigData.table_object.extract_all_fields(
        input_path, config_param_dict=config_params_dict)
    __pretty_print(result)
    assert result['error'] is None
# {'fields': [{'table_value': [{'__rownum': '1', 'Second': 'Two', 'Thirc)': '((Not Extracted))'}, {
#     '__rownum': '2', 'Second': '((Not Extracted))', 'Thirc)': '3'}], 'error': None, 'table_value_bbox': []}], 'error': None}


def test_bordered_table_extractor_4():
    config_params_dict = {'custom_cells': [
        {'columns': [1]}]}
    input_path_imgfile1 = os.path.abspath(
        './data/input/table8.jpg')
    input_path = input_path_imgfile1
    result = ConfigData.table_object.extract_all_fields(
        input_path, config_param_dict=config_params_dict)
    __pretty_print(result)
    assert result['error'] is None


def test_bordered_table_extractor_5():
    config_params_dict = {'custom_cells': [
        {'rows': [1, 2], 'columns': ['0:2']}]}
    input_path_imgfile1 = os.path.abspath(
        './data/input/table8.jpg')
    input_path = input_path_imgfile1
    result = ConfigData.table_object.extract_all_fields(
        input_path, config_param_dict=config_params_dict)
    __pretty_print(result)
    assert result['error'] is None


def test_bordered_table_extractor_6():
    config_params_dict = {'custom_cells': [
        {'rows': [1, ':3']}]}
    input_path_imgfile1 = os.path.abspath(
        './data/input/table8.jpg')
    input_path = input_path_imgfile1
    result = ConfigData.table_object.extract_all_fields(
        input_path, config_param_dict=config_params_dict)
    __pretty_print(result)
    assert result['error'] is None


def test_bordered_table_extractor_7():
    config_params_dict = {'custom_cells': [
        {'rows': ['0:']}]}
    input_path_imgfile1 = os.path.abspath(
        './data/input/table8.jpg')
    input_path = input_path_imgfile1
    result = ConfigData.table_object.extract_all_fields(
        input_path, config_param_dict=config_params_dict)
    __pretty_print(result)
    assert result['error'] is None


def test_bordered_table_extractor_8():
    config_params_dict = {'custom_cells': []}
    input_path_imgfile1 = os.path.abspath(
        './data/input/table8.jpg')
    input_path = input_path_imgfile1
    result = ConfigData.table_object.extract_all_fields(
        input_path, config_param_dict=config_params_dict)
    __pretty_print(result)
    assert result['error'] is None


def test_bordered_table_extractor_9():
    input_path_imgfile1 = os.path.abspath(
        './data/input/table8.jpg')
    input_path = input_path_imgfile1
    result = ConfigData.table_object.extract_all_fields(
        input_path)
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

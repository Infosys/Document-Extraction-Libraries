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
    pdf_file_name = None


@pytest.fixture(scope='module', autouse=True)
def pre_test():
    """Initialization method"""
    img_file_path_prefix = fr'{UNIT_TEST_DATA_LOCATION}\aa-doc'
    pdf_file_name = ('aa-doc.pdf')

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
    provider = ite.bordered_table_extractor.providers.NativePdfDataServiceProvider(
        log_level=LOG_LEVEL)
    save_folder_path = os.path.abspath('./data/output')
    temp_folderpath = './data/temp'
    table_object = ite.bordered_table_extractor.BorderedTableExtractor(
        provider, provider, temp_folderpath, logger, True)

    ConfigData.img_file_path_prefix = img_file_path_prefix
    ConfigData.save_folder_path = save_folder_path
    ConfigData.table_object = table_object
    ConfigData.pdf_file_name = pdf_file_name


def test_bordered_table_extractor_header_value():
    """test method"""
    input_path_imgfile1 = ConfigData.img_file_path_prefix + \
        '/aa-doc-files/1.jpg'
    input_path = input_path_imgfile1
    file_data_list = [{
        'path': ConfigData.img_file_path_prefix + '/' + ConfigData.pdf_file_name,
        'pages': [1]
    }]
    result = ConfigData.table_object.extract_all_fields(
        image_file_path=input_path,
        file_data_list=file_data_list,
        within_bbox=[1720, 1308, 666, 334],
        config_param_dict={'image_cell_cleanup_reqd': False,
                           'col_header': {'use_first_row': False, 'values': ['Name', 'Amount']}})

    __pretty_print(result)
    assert result['error'] is None


def test_bordered_table_extractor_no_header_value():
    """test method"""
    input_path_imgfile1 = ConfigData.img_file_path_prefix + \
        '/aa-doc-files/1.jpg'
    input_path = input_path_imgfile1
    file_data_list = [{
        'path': ConfigData.img_file_path_prefix + '/' + ConfigData.pdf_file_name,
        'pages': [1]
    }]
    result = ConfigData.table_object.extract_all_fields(
        image_file_path=input_path,
        file_data_list=file_data_list,
        within_bbox=[1720, 1308, 666, 334],
        config_param_dict={'image_cell_cleanup_reqd': False,
                           'col_header': {'use_first_row': False}})

    __pretty_print(result)
    assert result['error'] is None


def test_bordered_table_extractor_2():
    """test method"""
    input_path_imgfile1 = ConfigData.img_file_path_prefix + \
        '/aa-doc-files/1.jpg'
    input_path = input_path_imgfile1
    file_data_list = [{
        'path': ConfigData.img_file_path_prefix + '/' + ConfigData.pdf_file_name,
        'pages': [1]
    }]
    result = ConfigData.table_object.extract_all_fields(
        image_file_path=input_path,
        file_data_list=file_data_list,
        within_bbox=[900, 1267, 823, 783],
        config_param_dict={'image_cell_cleanup_reqd': False})

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

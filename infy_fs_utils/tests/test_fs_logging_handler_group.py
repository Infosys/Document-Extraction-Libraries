# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                   #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import os
import pytest
import infy_fs_utils


# Create inside temp folder for the purpose of unit testing
STORAGE_ROOT_PATH = f"C:/temp/unittest/infy_fs_utils/{__name__}/STORAGE"
EXPECTED_DATA = {
    "LOG_FILE_1": {
        "LOG_FILE_PATH": f"{STORAGE_ROOT_PATH}/logs/my_log_file1.log",
    },
    "LOG_FILE_2": {
        "LOG_FILE_PATH": f"{STORAGE_ROOT_PATH}/logs/my_log_file2.log",
    },
    "LOG_FILE_3": {
        "LOG_FILE_PATH": f"{STORAGE_ROOT_PATH}/logs/my_log_file3.log",
    }
}


@pytest.fixture(scope='module', autouse=True)
def pre_test(create_root_folders):
    """Initialization method"""
    create_root_folders([STORAGE_ROOT_PATH])
    # Step1 - Create file system handler
    storage_config_data = infy_fs_utils.data.StorageConfigData(
        **{
            "storage_root_uri": f"file://{STORAGE_ROOT_PATH}",
            "storage_server_url": "",
            "storage_access_key": "",
            "storage_secret_key": ""
        })
    file_sys_handler = infy_fs_utils.provider.FileSystemHandler(
        storage_config_data)

    # Step2 - Create logging handlers and add to manager
    logging_config_data_1 = infy_fs_utils.data.LoggingConfigData(
        **{
            "logger_group_name": "my_group_1",
            "logging_level": 10,
            "logging_format": "",
            "logging_timestamp_format": "",
            "log_file_data": {
                "log_file_dir_path": "/logs",
                "log_file_name_prefix": "my_log_file",
                "log_file_name_suffix": "1",
                "log_file_extension": ".log"

            }})
    logging_config_data_2 = infy_fs_utils.data.LoggingConfigData(
        **{
            "logger_group_name": "my_group_1",
            "logging_level": 10,
            "logging_format": "",
            "logging_timestamp_format": "",
            "log_file_data": {
                "log_file_dir_path": "/logs",
                "log_file_name_prefix": "my_log_file",
                "log_file_name_suffix": "2",
                "log_file_extension": ".log"

            }})
    logging_config_data_3 = infy_fs_utils.data.LoggingConfigData(
        **{
            "logger_group_name": "my_group_2",
            "logging_level": 10,
            "logging_format": "",
            "logging_timestamp_format": "",
            "log_file_data": {
                "log_file_dir_path": "/logs",
                "log_file_name_prefix": "my_log_file",
                "log_file_name_suffix": "3",
                "log_file_extension": ".log"

            }})
    infy_fs_utils.manager.FileSystemLoggingManager().add_fs_logging_handlers({
        'my_fs_log_handler_1': infy_fs_utils.provider.FileSystemLoggingHandler(
            logging_config_data_1, file_sys_handler),
        'my_fs_log_handler_2': infy_fs_utils.provider.FileSystemLoggingHandler(
            logging_config_data_2, file_sys_handler),
        'my_fs_log_handler_3': infy_fs_utils.provider.FileSystemLoggingHandler(
            logging_config_data_3, file_sys_handler)
    }
    )


def test_group_logging():
    """Test method"""
    logger = infy_fs_utils.manager.FileSystemLoggingManager(
    ).get_fs_logging_handler('my_fs_log_handler_1').get_logger()
    logger.debug('This is a debug message')
    logger.info('This is an info message')
    logger.warning('This is a warning message')
    logger.error('This is an error message')
    logger.critical('This is a critical message')
    # Log file 1 and 2 belong to same family hence they'll be created and log the same events
    assert os.path.exists(EXPECTED_DATA['LOG_FILE_1']['LOG_FILE_PATH'])
    assert os.path.exists(EXPECTED_DATA['LOG_FILE_2']['LOG_FILE_PATH'])
    with open(EXPECTED_DATA['LOG_FILE_1']['LOG_FILE_PATH'], encoding='utf-8') as f1:
        with open(EXPECTED_DATA['LOG_FILE_2']['LOG_FILE_PATH'], encoding='utf-8') as f2:
            assert f1.read() == f2.read()
    # Log file 3 belongs to different family hence it'll NOT be created
    assert not os.path.exists(EXPECTED_DATA['LOG_FILE_3']['LOG_FILE_PATH'])


def test_non_group_logging():
    """Test method"""
    logger = infy_fs_utils.manager.FileSystemLoggingManager(
    ).get_fs_logging_handler('my_fs_log_handler_3').get_logger()
    # logger = logging.getLogger(__name__)
    logger.debug('This is a debug message')
    logger.info('This is an info message')
    logger.warning('This is a warning message')
    logger.error('This is an error message')
    logger.critical('This is a critical message')
    # Log file 3 belongs to same family hence it'll be created
    assert os.path.exists(EXPECTED_DATA['LOG_FILE_3']['LOG_FILE_PATH'])


def test_delete_handler_impact_on_logging():
    """Test method"""
    logger = infy_fs_utils.manager.FileSystemLoggingManager(
    ).get_fs_logging_handler('my_fs_log_handler_1').get_logger()
    logger.debug('This is a debug message going to both log files')
    infy_fs_utils.manager.FileSystemLoggingManager(
    ).delete_fs_logging_handler('my_fs_log_handler_2')
    MESSAGE_1 = 'This is a debug message going to only 1 log file'
    logger.debug(MESSAGE_1)
    with open(EXPECTED_DATA['LOG_FILE_1']['LOG_FILE_PATH'], encoding='utf-8') as f1:
        data = f1.read()
        assert MESSAGE_1 in data
    with open(EXPECTED_DATA['LOG_FILE_2']['LOG_FILE_PATH'], encoding='utf-8') as f1:
        data = f1.read()
        assert not MESSAGE_1 in data

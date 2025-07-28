# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

"""Module containing FileSystemLoggingHandler class"""

import logging

from infy_fs_utils.data import LoggingConfigData
from ..interface.i_file_system_logging_handler import IFileSystemLoggingHandler
from ..interface.i_file_system_handler import IFileSystemHandler


class FileSystemLoggingHandler(IFileSystemLoggingHandler):
    """
    Class for logging handler based on FileSystemHandler.

    This class handles logging operations and writes log messages to a file system.

    Attributes:
        logging_config_data (LoggingConfigData): Configuration data for logging.
        file_sys_handler (IFileSystemHandler): Handler for file system operations.
    """

    def __init__(self, logging_config_data: LoggingConfigData, file_sys_handler: IFileSystemHandler):
        """
        Constructor for FileSystemLoggingHandler.

        Args:
            logging_config_data (LoggingConfigData): Configuration data for logging.
            file_sys_handler (IFileSystemHandler): Handler for file system operations.
        Example:
            >>> from infy_fs_utils.data import LoggingConfigData, StorageConfigData
            >>> from infy_fs_utils.provider import FileSystemHandler
            >>> storage_config_data = StorageConfigData(
            ...     storage_root_uri='file://C:/temp/unittest/infy_fs_utils/tests.test_fs_lh/STORAGE',
            ...     storage_server_url='',
            ...     storage_access_key='',
            ...     storage_secret_key=''
            ... )
            >>> file_sys_handler = FileSystemHandler(storage_config_data)
            >>> logging_config_data = LoggingConfigData(
            ...     logging_format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            ...     logging_timestamp_format='%Y-%m-%d %H:%M:%S',
            ...     logging_level=logging.DEBUG,
            ...     log_file_data={
            ...         'log_dir_path': 'logs',
            ...         'log_file_name_prefix': 'app_',
            ...         'log_file_name_suffix': 'log',
            ...         'log_file_extension': '.txt'
            ...     }
            ... )
            >>> logger = FileSystemLoggingHandler(logging_config_data, file_sys_handler)
        """
        super().__init__(logging_config_data=logging_config_data,
                         file_sys_handler=file_sys_handler)

        # Get logging config data from parent class
        logging_config_data_1 = self.get_logging_config_data()
        # Set log file path on object
        self.__log_file_path = self.__prepare_log_file_path()

        # Set properties at handler level
        formatter = logging.Formatter(
            logging_config_data_1.logging_format,
            datefmt=logging_config_data_1.logging_timestamp_format)
        self.setFormatter(formatter)
        self.setLevel(logging_config_data_1.logging_level)

        # Set properties at logger level
        self.get_logger().setLevel(logging_config_data_1.logging_level)
        self.set_handler()

    def emit(self, record):
        """
        Emit a log record.

        Args:
            record (logging.LogRecord): The log record to be emitted.
        Example:
            >>> import infy_fs_utils
            >>> from infy_fs_utils.data import LoggingConfigData, StorageConfigData
            >>> from infy_fs_utils.provider import FileSystemHandler
            >>> storage_config_data = StorageConfigData(
            ...     storage_root_uri='file://C:/temp/unittest/infy_fs_utils/tests.test_fs_lh/STORAGE',
            ...     storage_server_url='',
            ...     storage_access_key='',
            ...     storage_secret_key=''
            ... )
            >>> file_sys_handler = FileSystemHandler(storage_config_data)
            >>> logging_config_data = LoggingConfigData(
            ...     logging_format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            ...     logging_timestamp_format='%Y-%m-%d %H:%M:%S',
            ...     logging_level=logging.DEBUG,
            ...     log_file_data={
            ...         'log_dir_path': 'logs',
            ...         'log_file_name_prefix': 'app_',
            ...         'log_file_name_suffix': 'log',
            ...         'log_file_extension': '.txt'
            ...     }
            ... )
            >>> infy_fs_utils.manager.FileSystemLoggingManager().add_fs_logging_handler(infy_fs_utils.provider.FileSystemLoggingHandler(logging_config_data,file_sys_handler))
            >>> logger = infy_fs_utils.manager.FileSystemLoggingManager().get_fs_logging_handler().get_logger()
            >>> logger.debug('This is a debug message')
            >>> logger.info('This is an info message')
            >>> logger.warning('This is a warning message')
            >>> logger.error('This is an error message')
            >>> logger.critical('This is a critical message')
        """
        msg = self.format(record) + '\n'
        # print('emit()', msg)
        log_file_path = self.__log_file_path
        self.get_file_system_handler().append_file(log_file_path, msg)

    def __prepare_log_file_path(self):
        """Returns the log file path"""
        log_file_data = self.get_logging_config_data().log_file_data
        log_file_path = f"{log_file_data.log_dir_path}/{log_file_data.log_file_name_prefix}"
        log_file_path += f"{log_file_data.log_file_name_suffix}{log_file_data.log_file_extension}"

        # Create log folders if they doesn't exist
        log_dir_path = log_file_data.log_dir_path
        file_sys_handler = self.get_file_system_handler()
        if not file_sys_handler.exists(log_dir_path):
            file_sys_handler.create_folders(log_dir_path)

        return log_file_path

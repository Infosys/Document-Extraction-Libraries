# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import infy_fs_utils
from ...common import Constants
try:
    from dask.distributed import WorkerPlugin
except ImportError:
    # This is optional component only required for implementing Dask
    class WorkerPlugin:
        pass
    pass


class DaskWorkerPlugin(WorkerPlugin):
    """Worker plugin for Dask workers to setup FSHandler and LoggingHandler"""

    def __init__(self, fs_handler, logging_data_dict=None, storage_data_dict=None):
        self.fs_handler = fs_handler
        self.storage_data_dict = storage_data_dict
        self.storage_access_key = storage_data_dict.storage_access_key
        self.storage_root_uri = storage_data_dict.storage_root_uri
        self.storage_secret_key = storage_data_dict.storage_secret_key
        self.storage_server_url = storage_data_dict.storage_server_url
        self.logging_data_dict = logging_data_dict
        self.logger_group_name = logging_data_dict.logger_group_name
        self.logging_format = logging_data_dict.logging_format
        self.logging_level = logging_data_dict.logging_level
        self.logging_timestamp_format = logging_data_dict.logging_timestamp_format
        self.log_file_data = logging_data_dict.log_file_data

    def setup(self, worker):
        """
        This method is called when the worker starts up.
        Setup FSHandler and LoggingHandler for Dask worker
        """
        # FSHandler
        storage_config_data = infy_fs_utils.data.StorageConfigData(
            **{
                "storage_root_uri": self.storage_root_uri,
                "storage_server_url": self.storage_server_url,
                "storage_access_key": self.storage_access_key,
                "storage_secret_key": self.storage_secret_key
            })
        if infy_fs_utils.manager.FileSystemManager().get_fs_handler():
            return infy_fs_utils.manager.FileSystemManager().get_fs_handler()
        else:
            file_sys_handler = infy_fs_utils.provider.FileSystemHandler(
                storage_config_data)
            infy_fs_utils.manager.FileSystemManager().set_root_handler_name(Constants.FSLH_DPP)
            infy_fs_utils.manager.FileSystemManager().add_fs_handler(file_sys_handler)
        fs_handler = infy_fs_utils.manager.FileSystemManager().get_fs_handler()

        # Logging
        log_file_prefix = f"{self.log_file_data.log_file_name_prefix}_{worker.name}"
        logging_config_data = infy_fs_utils.data.LoggingConfigData(
            **{
                "logger_group_name": self.logger_group_name,
                "logging_level": self.logging_level,
                "logging_format": self.logging_format,
                "logging_timestamp_format": self.logging_timestamp_format,
                "log_file_data": {
                    "log_file_dir_path": self.log_file_data.log_dir_path,
                    "log_file_name_prefix": log_file_prefix,
                    "log_file_name_suffix": self.log_file_data.log_file_name_suffix,
                    "log_file_extension": self.log_file_data.log_file_extension

                }})
        if infy_fs_utils.manager.FileSystemLoggingManager().has_fs_logging_handler():
            return infy_fs_utils.manager.FileSystemLoggingManager(
            ).get_fs_logging_handler()
        else:
            file_sys_logging_handler = infy_fs_utils.provider.FileSystemLoggingHandler(
                logging_config_data, self.fs_handler)
            infy_fs_utils.manager.FileSystemLoggingManager(
            ).set_root_handler_name(Constants.FSLH_DPP)
            infy_fs_utils.manager.FileSystemLoggingManager(
            ).add_fs_logging_handler(file_sys_logging_handler)
        logging_handler = infy_fs_utils.manager.FileSystemLoggingManager(
        ).get_fs_logging_handler()

        # Worker setup
        setattr(worker, 'dask_worker_fs_handler', fs_handler)
        setattr(worker, 'dask_worker_logger_handler', logging_handler)

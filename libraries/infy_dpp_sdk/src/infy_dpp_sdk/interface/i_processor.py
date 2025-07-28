# ===============================================================================================================#
# Copyright 2022 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import copy
import logging
import traceback
from datetime import datetime
from abc import ABC, abstractmethod
from typing import List
import infy_fs_utils
from ..common import Constants
from ..data import (DocumentData, ProcessorResponseData)
from ..common._internal.processor_helper import ProcessorHelper
from ..common.app_config_manager import AppConfigManager
try:
    from dask import delayed, compute
    from dask.distributed import Client
    from dask.diagnostics import ProgressBar
    import distributed
except ImportError:
    # This is optional component only required for implementing Dask
    pass


class IProcessor(ABC):
    """Interface for Processor"""

    # ------------------------abstract methods----------------------------
    # These operations have to be implemented in subclasses.

    def __init__(self):
        self.__start_time, self.processor_name = None, None
        self.response_list = []

    @abstractmethod
    def do_execute(self, document_data: DocumentData,
                   context_data: dict, config_data: dict) -> ProcessorResponseData:
        """Run the processor"""
        raise NotImplementedError

    # ------------------------concrete methods----------------------------

    def do_execute_batch(self, document_data_list: List[DocumentData],
                         context_data_list: List[dict],
                         config_data: dict) -> List[ProcessorResponseData]:
        """Run the processor in batch mode"""
        __logger = self.get_logger()
        self.response_list: List[ProcessorResponseData] = []
        try:
            try:
                client = Client.current()
            except (NameError, ValueError):
                client = None
            if client:
                # Parallel execution
                self._do_execute_batch_parallel(
                    document_data_list, context_data_list, config_data)
            else:
                # Serial execution
                self._do_execute_batch_serial(
                    document_data_list, context_data_list, config_data)
        except Exception as ex:
            full_trace_error = traceback.format_exc()
            __logger.error(ex)
            __logger.error(full_trace_error)

        return self.response_list

    def _do_execute_batch_serial(self, document_data_list: List[DocumentData],
                                 context_data_list: List[dict],
                                 config_data: dict) -> List[ProcessorResponseData]:
        """Run the processor in batch mode"""
        __logger = self.get_logger()
        self.response_list: List[ProcessorResponseData] = []
        for document_data, context_data in zip(document_data_list, context_data_list):
            try:
                config_data_pristine = copy.deepcopy(config_data)
                _processor_response_data = self.do_execute(
                    document_data, context_data, config_data_pristine)
                self.response_list.append(_processor_response_data)
            except Exception as ex:
                full_trace_error = traceback.format_exc()
                __logger.error(full_trace_error)
                _processor_response_data = ProcessorHelper.create_processor_response_data(
                    document_data, context_data, ex)
                self.response_list.append(_processor_response_data)

        return self.response_list

    def _do_execute_batch_parallel(self, document_data_list: List[DocumentData],
                                   context_data_list: List[dict],
                                   config_data: dict) -> List[ProcessorResponseData]:
        """Run the processor in batch mode"""
        __logger = self.get_logger()
        self.response_list: List[ProcessorResponseData] = []
        tasks = []

        def execute_with_time(document_data, context_data, config_data_pristine):
            self.start()
            try:
                return self.do_execute(document_data, context_data, config_data_pristine)
            finally:
                document_id = document_data.document_id if document_data else ""
                self.end(self.processor_name, document_id)

        for document_data, context_data in zip(document_data_list, context_data_list):
            try:
                config_data_pristine = copy.deepcopy(config_data)
                _processor_response_data = delayed(execute_with_time)(
                    document_data, context_data, config_data_pristine)
                tasks.append(_processor_response_data)
            except Exception as ex:
                full_trace_error = traceback.format_exc()
                __logger.error(full_trace_error)
                _processor_response_data = ProcessorHelper.create_processor_response_data(
                    document_data, context_data, ex)
                self.response_list.append(_processor_response_data)
        with ProgressBar():
            self.response_list = compute(*tasks, timeout=60)

        return self.response_list

    def set_proc_name(self, processor_name):
        """Set processor name"""
        self.processor_name = processor_name

    def start(self):
        """This method is called before processor `do_execute`"""
        self.__start_time = datetime.now()

    def end(self, processor_name, document_id):
        """This method is called after completion of `do_execute`"""
        end_time = datetime.now()
        duration = end_time - self.__start_time
        start_time_str = self.__start_time.strftime("%H:%M:%S.%f")[:-3]
        logger = self.get_logger()
        end_message = f"Concurrent | Document Id: {document_id} | Processor Name: {processor_name} | Start time: {start_time_str} | Execution time: {duration.total_seconds()} secs"
        logger.debug(end_message)

    # ------------------------helper methods-------------------------------

    def get_fs_handler(self) -> infy_fs_utils.interface.IFileSystemHandler:
        """Get file system handler instance"""
        try:
            worker = distributed.get_worker()
            fs_handler = getattr(
                worker, 'dask_worker_fs_handler', None)
            return fs_handler
        except Exception:
            pass  # This is optional component only required for implementing Dask
        fs_handler = infy_fs_utils.manager.FileSystemManager(
        ).get_fs_handler()
        return fs_handler

    def __get_fs_logging_handler(self) -> infy_fs_utils.interface.IFileSystemLoggingHandler:
        """Get file system logging handler instance"""
        if infy_fs_utils.manager.FileSystemLoggingManager().has_fs_logging_handler(Constants.FSLH_DPP):
            return infy_fs_utils.manager.FileSystemLoggingManager(
            ).get_fs_logging_handler(Constants.FSLH_DPP)
        return None

    def get_logger(self) -> logging.Logger:
        """Get logger instance"""
        logging_handler = None
        try:
            worker = distributed.get_worker()
            logging_handler = getattr(
                worker, 'dask_worker_logger_handler', None)
        except Exception:
            pass  # This is optional component only required for implementing Dask
        if self.__get_fs_logging_handler():
            logging_handler = self.__get_fs_logging_handler()
        if logging_handler:
            return logging_handler.get_logger()
        else:
            return logging.getLogger()

    def get_app_config(self):
        """Get app_config instance"""
        return AppConfigManager().get_app_config()

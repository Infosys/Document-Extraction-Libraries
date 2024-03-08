# ===============================================================================================================#
# Copyright 2022 Infosys Ltd.                                                                                   #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

from abc import ABC, abstractmethod
from typing import List
import logging
import infy_fs_utils
from ..common import Constants
from ..data import (DocumentData, ProcessorResponseData)


class IProcessor(ABC):
    """Interface for Processor"""

    # ------------------------abstract methods----------------------------
    # These operations have to be implemented in subclasses.

    @abstractmethod
    def do_execute(self, document_data: DocumentData, context_data: dict, config_data: dict) -> ProcessorResponseData:
        """Run the processor"""
        raise NotImplementedError

    # ------------------------concrete methods----------------------------

    def do_execute_batch(self, document_data_list: List[DocumentData],
                         context_data_list: List[dict], config_data: dict) -> List[ProcessorResponseData]:
        """Run the processor in batch mode"""
        response_list: List[ProcessorResponseData] = []
        for document_data, context_data in zip(document_data_list, context_data_list):
            response_list.append(self.do_execute(
                document_data, context_data, config_data))
        return response_list

    # ------------------------helper methods-------------------------------

    def get_fs_handler(self) -> infy_fs_utils.interface.IFileSystemHandler:
        """Get file system handler instance"""
        return infy_fs_utils.manager.FileSystemManager().get_fs_handler(Constants.FSH_DPP)

    def get_fs_logging_handler(self) -> infy_fs_utils.interface.IFileSystemLoggingHandler:
        """Get file system logging handler instance"""
        if infy_fs_utils.manager.FileSystemLoggingManager().has_fs_logging_handler(Constants.FSLH_DPP):
            return infy_fs_utils.manager.FileSystemLoggingManager(
            ).get_fs_logging_handler(Constants.FSLH_DPP)
        return None

    def get_logger(self) -> logging.Logger:
        """Get logger instance"""
        if self.get_fs_logging_handler():
            return self.get_fs_logging_handler().get_logger()
        return logging.getLogger()

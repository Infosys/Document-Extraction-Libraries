# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

"""Module for table structure recogniser (TSR) interface class"""

import abc
from ...schema.table_data import BaseTableRequestData, BaseTableResponseData


class ITableStructureRecogniserProvider(metaclass=abc.ABCMeta):
    """Interface class for TSR"""

    def __init__(self) -> None:
        pass

    @abc.abstractmethod
    def extract_table_data(self, table_request_data: BaseTableRequestData) -> BaseTableResponseData:
        """Extrat table content from the input image file"""
        raise NotImplementedError

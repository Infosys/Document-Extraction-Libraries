# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

"""Module for table detector interface class"""

import abc
from ...schema.table_data import BaseTableRequestData, BaseTableResponseData


class ITableDetectorProvider(metaclass=abc.ABCMeta):
    """Interface class for table detector provider"""

    @abc.abstractmethod
    def detect_table(self, request_data: BaseTableRequestData) -> BaseTableResponseData:
        """Generate Q&A for the provided text"""
        raise NotImplementedError

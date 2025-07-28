# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

"""
This class is the implementation for the process layer
"""

from .interface.i_table_detector_provider import ITableDetectorProvider
from ..schema.table_data import BaseTableRequestData, BaseTableResponseData


class TableDetectorRequestData(BaseTableRequestData):
    """Class for table detector request data"""


class TableDetectorResponseData(BaseTableResponseData):
    """Class for table detector response data"""


class TableDetector():
    """Class for table detection in image"""

    def __init__(self, table_detector_provider: ITableDetectorProvider) -> None:
        self.__table_detector_provider = table_detector_provider

    def detect_table(self, request_data: TableDetectorRequestData) -> TableDetectorResponseData:
        """Detect Table for the provided image"""

        td_response_data = self.__table_detector_provider.detect_table(
            request_data)

        return td_response_data

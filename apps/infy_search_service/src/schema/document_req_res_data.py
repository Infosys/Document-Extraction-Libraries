# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

from typing import List, Optional
from pydantic import BaseModel, root_validator
from .base_req_res_data import BaseRequestData, BaseResponseData
from pydantic import Field


class DownloadDocumentResponseData(BaseResponseData):
    """Download document response data"""
    response: Optional[str] = None


class DownloadDocumentRequestData(BaseRequestData):
    """Download document request data"""
    file_name: str = Field(...,
                           description="Enter the full name of the file with extension")

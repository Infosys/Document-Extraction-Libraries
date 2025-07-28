# ===============================================================================================================#
# Copyright 2025 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

from typing import List, Optional, Any, Dict
from pydantic import BaseModel
from .base_req_res_data import BaseRequestData, BaseResponseData
from pydantic import Field


class SaveResourceRequestData(BaseRequestData):
    """SaveResource request data"""
    resource_file_path: str = ''


class FetchResourceRequestData(BaseRequestData):
    """FetchResource request data"""
    resource_file_name: str = ''


class ResourceResponseData(BaseResponseData):
    """Resource response data"""
    response: Optional[str] = None
    responseCde: int
    responseMsg: str
    timestamp: str
    responseTimeInSecs: float



# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

from typing import List
import pydantic
from pydantic import BaseModel, Field
from datetime import datetime, timezone


class BaseRequestData(BaseModel):
    """Base class for request data"""
    class Config:
        """Config"""
        extra = pydantic.Extra.forbid


class ResponseCode:
    """Base class for response code"""
    SUCCESS = 200
    CLIENT_FAILURE = 400
    SERVER_FAILURE = 500


class ResponseMessage:
    """Base class for response message"""
    SUCCESS = "Success"
    FAILURE = "Faliure"


class BaseResponseData(BaseModel):
    """Base class for response data"""
    class Config:
        """Config"""
        extra = pydantic.Extra.forbid

    response: dict = None
    responseCde: int = Field(default=ResponseCode.SUCCESS)
    responseMsg: str = Field(default=ResponseMessage.SUCCESS)
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc))
    responseTimeInSecs: float = Field(default=0.0)

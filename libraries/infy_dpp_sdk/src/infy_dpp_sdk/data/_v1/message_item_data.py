# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

from enum import Enum
from typing import Union
from pydantic import BaseModel


class MessageTypeEnum(Enum):
    """Message Type Enum"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class MessageCodeEnum(Enum):
    """Message Code Enum
    Informational responses (0 - 99)
    Client error responses (100 - 199)
    Server error responses (200 - 299)
    """

    INFO_SUCCESS = 0  # (0, "Success")
    INFO_NO_RECORDS_FOUND = 10  # (10, "No records found")
    CLIENT_ERR_INVALID_INPUT = 100  # (100, "Invalid input")
    SERVER_ERR_UNHANDLED_EXCEPTION = 200  # (200, "Server exception")


class MessageItemData(BaseModel):
    """Message record data class"""
    processor_name: str = None
    message_type: MessageTypeEnum = None
    message_code: Union[MessageCodeEnum, int] = None
    message_text: str = None

    def __str__(self) -> str:
        message_code = self.message_code.value if isinstance(
            self.message_code, Enum) else self.message_code
        data = {
            "processor_name": self.processor_name or '',
            "message_type": self.message_type.value,
            "message_code": message_code,
            "message_text": self.message_text

        }
        return str(data)

# ===============================================================================================================#
# Copyright 2022 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

from typing import List
from pydantic import BaseModel
from .message_item_data import MessageItemData


class MessageData(BaseModel):
    """Message data class"""
    messages: List[MessageItemData] = []

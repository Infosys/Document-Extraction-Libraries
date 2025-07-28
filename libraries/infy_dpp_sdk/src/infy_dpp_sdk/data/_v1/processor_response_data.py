# ===============================================================================================================#
# Copyright 2022 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

from typing import List

from pydantic import BaseModel

from .document_data import DocumentData
from .message_data import MessageData


class ProcessorResponseData(BaseModel):
    """Processor response data"""
    document_data: DocumentData = None
    context_data: dict = None
    message_data: MessageData = None

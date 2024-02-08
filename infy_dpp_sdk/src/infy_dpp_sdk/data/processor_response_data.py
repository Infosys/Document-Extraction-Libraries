# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

from typing import List

from pydantic import BaseModel

from ..data.document_data import DocumentData
from ..data.message_data import MessageData


class ProcessorResponseData(BaseModel):
    document_data: DocumentData = None
    context_data: dict = None
    message_data: List[MessageData] = None

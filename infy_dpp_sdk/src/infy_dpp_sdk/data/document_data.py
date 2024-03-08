# ===============================================================================================================#
# Copyright 2022 Infosys Ltd.                                                                                   #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import uuid
from typing import List

from pydantic import BaseModel, ValidationError, validator

from ..data.meta_data import MetaData
from ..data.page_data import PageData
from ..data.raw_data import RawData
from ..data.text_data import TextData


class DocumentData(BaseModel):
    """Document Data class"""
    document_id: str = None
    metadata: MetaData = None
    page_data: List[PageData] = None
    business_attribute_data: list = None
    text_data: List[TextData] = None
    raw_data: RawData = None

    @validator('document_id', always=True)
    def validate_document_id(cls, v):
        """Validate document_id"""
        if not v:
            return str(uuid.uuid4())
        else:
            return v

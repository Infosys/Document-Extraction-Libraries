# ===============================================================================================================#
# Copyright 2022 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import uuid
from typing import List
from pydantic import BaseModel, field_validator, Field
from ..data.meta_data import MetaData
from ..data.page_data import PageData
from ..data.raw_data import RawData
from ..data.text_data import TextData


class DocumentData(BaseModel):
    """Document data class"""
    document_id: str | None = Field(default=None, validate_default=True)
    metadata: MetaData | None = None
    page_data: List[PageData] | None = None
    business_attribute_data: list | None = None
    text_data: List[TextData] | None = None
    raw_data: RawData | None = None

    @field_validator('document_id', mode='before')
    @classmethod
    def validate_document_id(cls, v):
        """Validate document_id"""
        if not v:
            return str(uuid.uuid4())
        else:
            return v

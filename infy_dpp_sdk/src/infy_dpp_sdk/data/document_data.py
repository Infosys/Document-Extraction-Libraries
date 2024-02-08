# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

from typing import List

from pydantic import BaseModel

from ..data.meta_data import MetaData
from ..data.page_data import PageData
from ..data.raw_data import RawData
from ..data.text_data import TextData


class DocumentData(BaseModel):
    document_id: str = None
    metadata: MetaData = None
    page_data: List[PageData] = None
    business_attribute_data: list = None
    text_data: List[TextData] = None
    raw_data: RawData = None

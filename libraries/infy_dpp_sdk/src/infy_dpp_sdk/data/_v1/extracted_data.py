# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

from typing import List
from pydantic import BaseModel

from .value_data import ValueData


class ExtractedData(BaseModel):
    # Dynamic fields allowed in this model
    languages: List[ValueData] = None
    document_type: ValueData = None

    class Config:
        # allow arbitrary fields in the model
        extra = "allow"

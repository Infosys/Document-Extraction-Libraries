# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

from typing import List
from pydantic import BaseModel, ConfigDict
from ..data.value_data import ValueData


class ExtractedData(BaseModel):
    """Extracted data class"""
    # Dynamic fields allowed in this model
    languages: List[ValueData] | None = None
    document_type: ValueData | None = None

    model_config = ConfigDict(extra='allow')

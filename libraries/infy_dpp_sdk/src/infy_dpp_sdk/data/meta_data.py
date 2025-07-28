# ===============================================================================================================#
# Copyright 2022 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#
from pydantic import BaseModel

from ..data.standard_data import StandardData
from ..data.extracted_data import ExtractedData


class MetaData(BaseModel):
    """Meta data class"""
    standard_data: StandardData | None = None
    extracted_data: ExtractedData | None = None

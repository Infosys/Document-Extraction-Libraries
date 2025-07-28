# ===============================================================================================================#
# Copyright 2022 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#
from pydantic import BaseModel

from ..data.meta_data import MetaData


class PageData(BaseModel):
    """Page data class"""
    page: int | None = None
    metadata: MetaData | None = None

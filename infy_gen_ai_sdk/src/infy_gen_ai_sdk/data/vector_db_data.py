# ===============================================================================================================#
# Copyright 2022 Infosys Ltd.                                                                                   #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

from pydantic import BaseModel


class BaseVectorDbRecordData(BaseModel):
    """Base class for embedding provider config data"""
    id: str = None
    content: str = None
    metadata: dict = None


class BaseVectorDbQueryParamsData(BaseModel):
    """Base class for storing query params for Vector DB search"""
    query: str = None
    filter_metadata: dict = None
    top_k: int   # Max number of matching records to return
    # Number of documents to fetch before filtering.
    pre_filter_fetch_k: int

# ===============================================================================================================#
# Copyright 2022 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

from typing import Optional
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


class OnlineVectorDbConfigData(BaseModel):
    """Base class for online provider config data"""
    db_service_url: str = None
    model_name: str = None
    index_id: Optional[str] = None
    collection_name: str = None
    collection_secret_key: str = None

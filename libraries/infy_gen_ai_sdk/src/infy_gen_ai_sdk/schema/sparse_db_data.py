# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

from typing import Optional
try:
    from pydantic.v1 import BaseModel
except ImportError:
    from pydantic import BaseModel


class BaseSparseDbConfigData(BaseModel):
    """Base class for Sparse provider config data"""
    db_folder_path: str
    db_index_name: str
    db_index_secret_key: Optional[str] = None


class BaseSparseDbSaveRecordData(BaseModel):
    """Base class for storing records to Sparse DB"""
    content_file_path: str
    metadata: dict = None


class BaseSparseDbRecordData(BaseModel):
    """Base class for storing records to Sparse DB"""
    content: str = None
    metadata: dict = None


class BaseSparseDbQueryParamsData(BaseModel):
    """Base class for storing query params for Sparse DB"""
    query: str = None
    top_k: int
    pre_filter_fetch_k: int
    filter_metadata: dict = None


class BaseSparseDbMacthesData(BaseModel):
    """Base class for fetching mathes from Sparse DB search"""
    db_folder_path: str = None
    content: str = None
    metadata: dict = None
    score: float = None


class OnlineSparseDbConfigData(BaseModel):
    """Base class for online provider config data"""
    db_service_url: str = None
    method_name: str = None
    index_id: Optional[str] = None
    collection_name: str = None
    collection_secret_key: str = None

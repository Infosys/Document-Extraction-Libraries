# ===============================================================================================================#
# Copyright 2022 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

from typing import List
import pydantic
from pydantic import BaseModel, root_validator


class SnapshotData(BaseModel):
    """Request file snapshot"""
    document_data_file_path: str = None
    context_data_file_path: str = None
    message_data_file_path: str = None

    class Config:
        """Config"""
        extra = pydantic.Extra.forbid


class ProcessorFilterData(BaseModel):
    """Processor filters"""
    includes: List[str] = []
    excludes: List[str] = []

    class Config:
        """Config"""
        extra = pydantic.Extra.forbid

    @root_validator(pre=False, allow_reuse=True)
    def check(cls, values):
        """Validate filter"""
        if values.get('includes') and values.get('excludes'):
            raise ValueError(
                'Specify either includes OR excludes but NOT both')
        return values


class RecordData(BaseModel):
    """Request file record"""
    document_id: str = None
    snapshot: SnapshotData = None

    class Config:
        """Config"""
        extra = pydantic.Extra.forbid


class ControllerRequestData(BaseModel):
    """Controller request data"""
    dpp_version: str = None
    request_id: str = None
    description: str = None
    input_config_file_path: str = None
    processor_filter: ProcessorFilterData = None
    context: dict = None
    snapshot_dir_root_path: str = None
    records: List[RecordData] = None

    class Config:
        """Config"""
        extra = pydantic.Extra.forbid

    @root_validator(pre=False, allow_reuse=True)
    def check(cls, values):
        """Validate filter"""
        if values.get('context'):
            count = len(values.get('context').keys())
            if count > 1:
                raise ValueError(
                    f'Context should have only 1 root key. Found {count} keys')
        return values


class ControllerResponseData(ControllerRequestData):
    """Controller response data"""
    class Config:
        """Config"""
        extra = pydantic.Extra.forbid

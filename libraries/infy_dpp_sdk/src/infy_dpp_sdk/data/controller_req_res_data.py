# ===============================================================================================================#
# Copyright 2022 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

from typing import List
from pydantic import BaseModel, model_validator, ConfigDict, Field


class SnapshotData(BaseModel):
    """Snapshot data class"""
    document_data_file_path: str | None = None
    context_data_file_path: str | None = None
    message_data_file_path: str | None = None

    model_config = ConfigDict(extra='forbid')


class ProcessorFilterData(BaseModel):
    """Processor filter data class"""
    includes: List[str] = []
    excludes: List[str] = []

    model_config = ConfigDict(extra='forbid')

    @model_validator(mode='before')
    @classmethod
    def check(cls, values):
        """Validate filter"""
        if values.get('includes') and values.get('excludes'):
            raise ValueError(
                'Specify either includes OR excludes but NOT both')
        return values


class RecordData(BaseModel):
    """Record data class"""
    document_id: str | None = None
    snapshot: SnapshotData | None = None

    model_config = ConfigDict(extra='forbid')


class ControllerRequestData(BaseModel):
    """Controller request data class"""
    dpp_version: str | None = None
    request_id: str | None = None
    description: str | None = None
    input_config_file_path: str | None = None
    processor_filter: ProcessorFilterData | None = None
    context: dict | None = None
    snapshot_dir_root_path: str | None = None
    records: List[RecordData] | None = Field(default=None)

    model_config = ConfigDict(extra='forbid')

    @model_validator(mode='before')
    @classmethod
    def check(cls, values):
        """Validate filter"""
        if values.get('context'):
            count = len(values.get('context').keys())
            if count > 1:
                raise ValueError(
                    f'Context should have only 1 root key. Found {count} keys')
        return values


class ControllerResponseData(ControllerRequestData):
    """Controller response data class"""
    model_config = ConfigDict(extra='forbid')

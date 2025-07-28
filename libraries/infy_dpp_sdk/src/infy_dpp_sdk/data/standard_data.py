# ===============================================================================================================#
# Copyright 2022 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#
import math
import mimetypes
import os
from datetime import datetime
import infy_fs_utils
from pydantic import BaseModel, field_validator, Field, ValidationInfo
from ..common import Constants
from ..data.value_data import ValueData


class StandardData(BaseModel):
    """Standard data class"""
    filepath: ValueData | None = Field(default=None, validate_default=True)
    filename: ValueData | None = Field(default=None, validate_default=True)
    size: ValueData | None = Field(default=None, validate_default=True)
    created_dtm: ValueData | None = Field(default=None, validate_default=True)
    modified_dtm: ValueData | None = Field(default=None, validate_default=True)
    mime_type: ValueData | None = Field(default=None, validate_default=True)
    width: ValueData | None = None
    height: ValueData | None = None

    @field_validator('filepath', mode='before')
    @classmethod
    def validate_filepath(cls, v):
        """Validate file path"""
        if not v:
            raise ValueError('filepath is required')
        else:
            return v

    @field_validator('filename', mode='before')
    @classmethod
    def update_filename_based_on_filepath(cls, v, values: ValidationInfo):
        """Update filename based on filepath"""
        filepath_val = values.data['filepath'].value
        if not v:
            try:
                # fs_handler: infy_fs_utils.interface.IFileSystemHandler = infy_fs_utils.manager.FileSystemManager().get_fs_handler(
                #     Constants.FSH_DPP)
                # file_info = fs_handler.get_info(filepath_val)
                return ValueData(value=(os.path.basename(filepath_val)))
            except Exception:
                return v
        else:
            return v

    @field_validator('size', mode='before')
    @classmethod
    def update_size_based_on_filepath(cls, v, values: ValidationInfo):
        """Update size based on filepath"""
        filepath_val = values.data['filepath'].value
        if not v:
            try:
                return ValueData(value=(cls.__get_file_size_in_human_readable(
                    filepath_val)))
            except Exception:
                return v
        else:
            return v

    @field_validator('created_dtm', mode='before')
    @classmethod
    def update_cdtm_based_on_filepath(cls, v, values: ValidationInfo):
        """Update created date time based on filepath"""
        filepath_val = values.data['filepath'].value
        if not v:
            try:
                fs_handler: infy_fs_utils.interface.IFileSystemHandler = infy_fs_utils.manager.FileSystemManager(
                ).get_fs_handler(Constants.FSH_DPP)
                file_info = fs_handler.get_info(filepath_val)

                return ValueData(value=(datetime.fromtimestamp(file_info['created']).strftime('%Y-%m-%d %H:%M:%S')))
            except Exception:
                return v
        else:
            return v

    @field_validator('modified_dtm', mode='before')
    @classmethod
    def update_mdtm_based_on_filepath(cls, v, values: ValidationInfo):
        """Update modified date time based on filepath"""
        filepath_val = values.data['filepath'].value
        if not v:
            try:
                fs_handler: infy_fs_utils.interface.IFileSystemHandler = infy_fs_utils.manager.FileSystemManager(
                ).get_fs_handler(Constants.FSH_DPP)
                file_info = fs_handler.get_info(filepath_val)
                return ValueData(value=(datetime.fromtimestamp(file_info['mtime']).strftime('%Y-%m-%d %H:%M:%S')))
            except Exception:
                return v
        else:
            return v

    @field_validator('mime_type', mode='before')
    @classmethod
    def update_mime_based_on_filepath(cls, v, values: ValidationInfo):
        """Update mime type based on filepath"""
        filepath_val = values.data['filepath'].value
        if not v:
            try:
                return ValueData(value=(mimetypes.guess_type(filepath_val)[0]))
            except Exception:
                return v
        else:
            return v

    @ classmethod
    def __get_file_size_in_human_readable(cls, file_path: str) -> str:
        fs_handler: infy_fs_utils.interface.IFileSystemHandler = infy_fs_utils.manager.FileSystemManager(
        ).get_fs_handler(Constants.FSH_DPP)
        file_info = fs_handler.get_info(file_path)

        # size_in_bytes = os.path.getsize(file_path)
        size_in_bytes = file_info['size']
        if size_in_bytes == 0:
            return "0"
        size_name = ("B", "KB", "MB", "GB")
        i = int(math.floor(math.log(abs(size_in_bytes), 1024)))
        p = math.pow(1024, i)
        s = round(size_in_bytes / p, 2)
        return "%s %s" % (s, size_name[i])

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
from ...common import Constants

from pydantic import BaseModel, ValidationError, validator

from .value_data import ValueData


class StandardData(BaseModel):
    filepath: ValueData
    filename: ValueData = None
    size: ValueData = None
    created_dtm: ValueData = None
    modified_dtm: ValueData = None
    mime_type: ValueData = None
    width: ValueData = None
    height: ValueData = None

    @validator('filepath', pre=True)
    def validate_filepath(cls, v):
        if not v:
            raise ValidationError('filepath is required')
        else:
            return v

    @validator('filename', always=True)
    def update_filename_based_on_filepath(cls, v, values):
        filepath_val = values['filepath'].value
        if not v:
            try:
                # fs_handler: infy_fs_utils.interface.IFileSystemHandler = infy_fs_utils.manager.FileSystemManager().get_fs_handler(
                #     Constants.FSH_DPP)
                # file_info = fs_handler.get_info(filepath_val)
                return ValueData(value=(os.path.basename(filepath_val)))
            except:
                return v
        else:
            return v

    @validator('size', always=True)
    def update_size_based_on_filepath(cls, v, values):
        filepath_val = values['filepath'].value
        if not v:
            try:
                return ValueData(value=(cls.__get_file_size_in_human_readable(
                    filepath_val)))
            except:
                return v
        else:
            return v

    @validator('created_dtm', always=True)
    def update_cdtm_based_on_filepath(cls, v, values):
        filepath_val = values['filepath'].value
        if not v:
            try:
                fs_handler: infy_fs_utils.interface.IFileSystemHandler = infy_fs_utils.manager.FileSystemManager().get_fs_handler(
                    Constants.FSH_DPP)
                file_info = fs_handler.get_info(filepath_val)

                return ValueData(value=(datetime.fromtimestamp(file_info['created']).strftime('%Y-%m-%d %H:%M:%S')))
            except:
                return v
        else:
            return v

    @validator('modified_dtm', always=True)
    def update_mdtm_based_on_filepath(cls, v, values):
        filepath_val = values['filepath'].value
        if not v:
            try:
                fs_handler: infy_fs_utils.interface.IFileSystemHandler = infy_fs_utils.manager.FileSystemManager().get_fs_handler(
                    Constants.FSH_DPP)
                file_info = fs_handler.get_info(filepath_val)
                return ValueData(value=(datetime.fromtimestamp(file_info['mtime']).strftime('%Y-%m-%d %H:%M:%S')))
            except:
                return v
        else:
            return v

    @validator('mime_type', always=True)
    def update_mime_based_on_filepath(cls, v, values):
        filepath_val = values['filepath'].value
        if not v:
            try:
                return ValueData(value=(mimetypes.guess_type(filepath_val)[0]))
            except:
                return v
        else:
            return v

    @ classmethod
    def __get_file_size_in_human_readable(cls, file_path: str) -> str:
        fs_handler: infy_fs_utils.interface.IFileSystemHandler = infy_fs_utils.manager.FileSystemManager().get_fs_handler(
            Constants.FSH_DPP)
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

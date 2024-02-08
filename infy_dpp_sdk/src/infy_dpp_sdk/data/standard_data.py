# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#
import math
import mimetypes
import os
import pathlib
from datetime import datetime

from pydantic import BaseModel, ValidationError, validator

from ..data.value_data import ValueData


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
                return ValueData(value=(datetime.fromtimestamp(pathlib.Path(
                    filepath_val).stat().st_ctime).strftime('%Y-%m-%d %H:%M:%S')))
            except:
                return v
        else:
            return v

    @validator('modified_dtm', always=True)
    def update_mdtm_based_on_filepath(cls, v, values):
        filepath_val = values['filepath'].value
        if not v:
            try:
                return ValueData(value=(datetime.fromtimestamp(pathlib.Path(
                    filepath_val).stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')))
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
        size_in_bytes = os.path.getsize(file_path)
        if size_in_bytes == 0:
            return "0"
        size_name = ("B", "KB", "MB", "GB")
        i = int(math.floor(math.log(abs(size_in_bytes), 1024)))
        p = math.pow(1024, i)
        s = round(size_in_bytes / p, 2)
        return "%s %s" % (s, size_name[i])

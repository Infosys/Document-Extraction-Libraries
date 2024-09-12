# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                   #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import socket
import time
try:
    from pydantic.v1 import BaseModel, ValidationError, validator
except ImportError:
    from pydantic import BaseModel, ValidationError, validator


class LogFileData(BaseModel):
    """Log file data"""
    log_dir_path: str = None
    log_file_name_prefix: str = None
    log_file_name_suffix: str = None
    log_file_extension: str = None

    @validator('log_dir_path', always=True)
    def validate_log_dir_path1(cls, v):
        """Validate log_dir_path"""
        if not v:
            return '/logs'
        return v

    @validator('log_file_name_prefix', always=True)
    def validate_log_file_name_prefix(cls, v):
        """Validate log_file_name_prefix"""
        if not v:
            raise ValidationError('log_file_name_prefix is mandatory')
        return v

    @validator('log_file_name_suffix', always=True)
    def validate_log_file_name_suffix(cls, v):
        """Validate log_file_name_suffix"""
        if isinstance(v, None.__class__):
            timestr = time.strftime("%Y%m%d")
            return f"_{socket.gethostname()}_{timestr}"
        return v

    @validator('log_file_extension', always=True)
    def validate_log_file_extension(cls, v):
        """Validate log_file_extension"""
        if not v:
            return '.log'
        return v


class LoggingConfigData(BaseModel):
    """Logging configuration data"""
    # Use logger_group_name to group loggers so that they all log the same events
    logger_group_name: str = None
    logging_level: int = None
    logging_format: str = None
    logging_timestamp_format: str = None
    log_file_data: LogFileData = None

    @validator('logging_level', always=True)
    def validate_logging_level(cls, v):
        """Validate logging_level"""
        # Possible Values for logging_level
        LOGGING_LEVELS = [[10, 'DEBUG'], [20, 'INFO'], [
            30, 'WARNING'], [40, 'ERROR'], [50, 'CRITICAL']]
        if not v:
            return LOGGING_LEVELS[0][0]
        if not v in [x[0] for x in LOGGING_LEVELS]:
            raise ValidationError(
                f'logging_level should be one of {LOGGING_LEVELS}')
        return v

    @validator('logging_format', always=True)
    def validate_logging_format(cls, v):
        """Validate logging_format"""
        __LOG_FORMAT = '%(asctime)s.%(msecs)03d %(levelname)s [%(threadName)s] '
        __LOG_FORMAT += '[%(module)s] [%(funcName)s:%(lineno)d] %(message)s'
        if not v:
            return __LOG_FORMAT
        return v

    @validator('logging_timestamp_format', always=True)
    def validate_logging_timestamp_format(cls, v):
        """Validate logging_timestamp_format"""
        __TIMESTAMP_FORMAT = '%Y-%m-%d %H:%M:%S'
        if not v:
            return __TIMESTAMP_FORMAT
        return v

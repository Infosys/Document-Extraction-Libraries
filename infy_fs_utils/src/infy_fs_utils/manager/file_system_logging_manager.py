# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                   #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

"""Module containing FileSystemLoggingManager"""

from typing import Dict
from ..common.singleton import Singleton
from ..interface.i_file_system_logging_handler import IFileSystemLoggingHandler


class FileSystemLoggingManager(metaclass=Singleton):
    """Factory class to get singleton logger object at application level"""

    __file_sys_logging_handler_dict: Dict[str,
                                          IFileSystemLoggingHandler] = None

    def __init__(self) -> None:
        self.__file_sys_logging_handler_dict: {}

    def has_fs_logging_handler(self, name: str = 'default') -> bool:
        """Returns True if an instance of IFileSystemLoggingHandler exists"""
        if self.__file_sys_logging_handler_dict:
            return name in self.__file_sys_logging_handler_dict.keys()
        return False

    def get_fs_logging_handler(self, name: str = 'default') -> IFileSystemLoggingHandler:
        """Returns an instance of IFileSystemLoggingHandler"""
        if self.__file_sys_logging_handler_dict:
            return self.__file_sys_logging_handler_dict.get(name, None)
        return None

    def delete_fs_logging_handler(self, name: str = 'default') -> bool:
        """Deletes an instance of IFileSystemLoggingHandler"""
        if self.__file_sys_logging_handler_dict and self.__file_sys_logging_handler_dict.get(name, None):
            obj: IFileSystemLoggingHandler = self.__file_sys_logging_handler_dict.pop(
                name)
            obj.unset_handler()
            del obj
            return True
        return False

    def add_fs_logging_handler(self, file_sys_logging_handler: IFileSystemLoggingHandler, name: str = 'default') -> None:
        """Adds an instance of IFileSystemLoggingHandler"""
        if not isinstance(file_sys_logging_handler, IFileSystemLoggingHandler):
            message = f"{file_sys_logging_handler} is not an instance of IFileSystemLoggingHandler."
            raise ValueError(message)
        existing_keys = []
        if self.__file_sys_logging_handler_dict:
            existing_keys = list(self.__file_sys_logging_handler_dict.keys())
            if name in existing_keys:
                raise ValueError(
                    f"Duplicate key={name} found. Please provide unique keys.")
            self.__file_sys_logging_handler_dict[name] = file_sys_logging_handler
        else:
            self.__file_sys_logging_handler_dict = {
                name: file_sys_logging_handler}

    def add_fs_logging_handlers(self, file_sys_logging_handler_dict: Dict[str, IFileSystemLoggingHandler]) -> None:
        """Adds one or more instances of IFileSystemLoggingHandler"""
        if file_sys_logging_handler_dict:
            for key, value in file_sys_logging_handler_dict.items():
                if not isinstance(value, IFileSystemLoggingHandler):
                    message = f"For key={key}, the value={value} is not an instance of IFileSystemLoggingHandler."
                    raise ValueError(message)
            if not self.__file_sys_logging_handler_dict:
                self.__file_sys_logging_handler_dict = file_sys_logging_handler_dict
                return
            existing_keys = list(self.__file_sys_logging_handler_dict.keys())
            new_keys = list(file_sys_logging_handler_dict.keys())
            duplicate_keys = [x for x in new_keys if x in existing_keys]
            if duplicate_keys:
                raise ValueError(
                    f"Duplicate keys={duplicate_keys} found. Please provide unique keys.")
            self.__file_sys_logging_handler_dict.update(
                file_sys_logging_handler_dict)

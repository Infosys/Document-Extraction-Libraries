# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                   #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

"""Module containing FileSystemManager"""

from typing import Dict
from ..common.singleton import Singleton
from ..interface.i_file_system_handler import IFileSystemHandler


class FileSystemManager(metaclass=Singleton):
    """Class for creating a singleton instance of FileSystemHandler at application level."""

    __file_sys_handler_dict: Dict[str, IFileSystemHandler] = None

    def __init__(self) -> None:
        self.__file_sys_handler_dict: {}

    def has_fs_handler(self, name: str = 'default') -> bool:
        """Returns True if an instance of IFileSystemHandler exists"""
        if self.__file_sys_handler_dict:
            return name in self.__file_sys_handler_dict.keys()
        return False

    def get_fs_handler(self, name: str = 'default') -> IFileSystemHandler:
        """Returns an instance of IFileSystemHandler"""
        if self.__file_sys_handler_dict:
            return self.__file_sys_handler_dict.get(name, None)
        return None

    def delete_fs_handler(self, name: str = 'default') -> bool:
        """Deletes an instance of IFileSystemHandler"""
        if self.__file_sys_handler_dict.get(name):
            del self.__file_sys_handler_dict[name]
            return True
        return False

    def add_fs_handler(self, file_sys_handler: IFileSystemHandler, name: str = 'default') -> None:
        """Adds an instance of IFileSystemHandler"""
        if not isinstance(file_sys_handler, IFileSystemHandler):
            message = f"{file_sys_handler} is not an instance of IFileSystemHandler."
            raise ValueError(message)
        existing_keys = []
        if self.__file_sys_handler_dict:
            existing_keys = list(self.__file_sys_handler_dict.keys())
            if name in existing_keys:
                raise ValueError(
                    f"Duplicate key={name} found. Please provide unique keys.")
            self.__file_sys_handler_dict[name] = file_sys_handler
        else:
            self.__file_sys_handler_dict = {name: file_sys_handler}

    def add_fs_handlers(self, file_sys_handler_dict: Dict[str, IFileSystemHandler]) -> None:
        """Adds one or more instances of IFileSystemHandler"""
        if file_sys_handler_dict:
            for key, value in file_sys_handler_dict.items():
                if not isinstance(value, IFileSystemHandler):
                    message = f"For key={key}, the value={value} is not an instance of IFileSystemHandler."
                    raise ValueError(message)
            if not self.__file_sys_handler_dict:
                self.__file_sys_handler_dict = file_sys_handler_dict
                return
            existing_keys = list(self.__file_sys_handler_dict.keys())
            new_keys = list(file_sys_handler_dict.keys())
            duplicate_keys = [x for x in new_keys if x in existing_keys]
            if duplicate_keys:
                raise ValueError(
                    f"Duplicate keys={duplicate_keys} found. Please provide unique keys.")
            self.__file_sys_handler_dict.update(file_sys_handler_dict)

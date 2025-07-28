# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

"""Module containing FileSystemManager"""

from typing import Dict
from .._common.singleton import Singleton
from ..interface.i_file_system_handler import IFileSystemHandler


class FileSystemManager(metaclass=Singleton):
    """Class for creating a singleton instance of FileSystemHandler at application level."""

    __file_sys_handler_dict: Dict[str, IFileSystemHandler] = None
    __root_handler_name = None

    def __init__(self) -> None:
        self.__file_sys_handler_dict: {}

    def set_root_handler_name(self, name: str) -> None:
        """
        Sets the root handler name.

        Args:
            name (str): The name of the root handler.

        Example:
            >>> fs_manager = FileSystemManager()
            >>> fs_manager.set_root_handler_name('root_handler')
            >>> fs_manager._FileSystemManager__root_handler_name
            'root_handler'
        """
        self.__root_handler_name = name

    def has_fs_handler(self, name: str = 'default') -> bool:
        """
        Check if an instance of IFileSystemHandler exists.

        Args:
            name (str): The name of the file system handler. Default is 'default'.

        Returns:
            bool: True if an instance exists, False otherwise.
        Examples:
            >>> fsm = FileSystemManager()
            >>> fsm.has_fs_handler()
            False
            >>> class MockIFileSystemHandler(IFileSystemHandler):
            ...     def __init__(self): pass
            ...     def append_file(self): pass
            ...     def copy_file(self): pass
            ...     def create_folders(self): pass
            ...     def delete_file(self): pass
            ...     def delete_folder(self): pass
            ...     def exists(self): pass
            ...     def get_file(self): pass
            ...     def get_file_object(self): pass
            ...     def get_folder(self): pass
            ...     def get_info(self): pass
            ...     def get_instance(self): pass
            ...     def list_files(self): pass
            ...     def move_file(self): pass
            ...     def move_folder(self): pass
            ...     def put_file(self): pass
            ...     def put_folder(self): pass
            ...     def write_file(self): pass
            >>> handler = MockIFileSystemHandler()
            >>> fsm.add_fs_handler(handler, name='unique_handler_1')
            >>> fsm.has_fs_handler('unique_handler_1')
            True
        """
        _name = self.__root_handler_name if self.__root_handler_name else name
        if self.__file_sys_handler_dict:
            return _name in self.__file_sys_handler_dict.keys()
        return False

    def get_fs_handler(self, name: str = 'default') -> IFileSystemHandler:
        """
        Get an instance of IFileSystemHandler.

        Args:
            name (str): The name of the file system handler. Default is 'default'.

        Returns:
            IFileSystemHandler: The file system handler instance.
        Examples:
            >>> fsm = FileSystemManager()
            >>> class MockIFileSystemHandler(IFileSystemHandler):
            ...     def __init__(self): pass
            ...     def append_file(self): pass
            ...     def copy_file(self): pass
            ...     def create_folders(self): pass
            ...     def delete_file(self): pass
            ...     def delete_folder(self): pass
            ...     def exists(self): pass
            ...     def get_file(self): pass
            ...     def get_file_object(self): pass
            ...     def get_folder(self): pass
            ...     def get_info(self): pass
            ...     def get_instance(self): pass
            ...     def list_files(self): pass
            ...     def move_file(self): pass
            ...     def move_folder(self): pass
            ...     def put_file(self): pass
            ...     def put_folder(self): pass
            ...     def write_file(self): pass
            >>> handler = MockIFileSystemHandler()
            >>> fsm.add_fs_handler(handler, name='unique_handler_2')
            >>> fsm.get_fs_handler('unique_handler_2') == handler
            True
        """
        _name = self.__root_handler_name if self.__root_handler_name else name
        if self.__file_sys_handler_dict:
            return self.__file_sys_handler_dict.get(_name, None)
        return None

    def delete_fs_handler(self, name: str = 'default') -> bool:
        """
        Delete an instance of IFileSystemHandler.

        Args:
            name (str): The name of the file system handler. Default is 'default'.

        Returns:
            bool: True if the instance was deleted, False otherwise.
        Examples:
            >>> fsm = FileSystemManager()
            >>> class MockIFileSystemHandler(IFileSystemHandler):
            ...     def __init__(self): pass
            ...     def append_file(self): pass
            ...     def copy_file(self): pass
            ...     def create_folders(self): pass
            ...     def delete_file(self): pass
            ...     def delete_folder(self): pass
            ...     def exists(self): pass
            ...     def get_file(self): pass
            ...     def get_file_object(self): pass
            ...     def get_folder(self): pass
            ...     def get_info(self): pass
            ...     def get_instance(self): pass
            ...     def list_files(self): pass
            ...     def move_file(self): pass
            ...     def move_folder(self): pass
            ...     def put_file(self): pass
            ...     def put_folder(self): pass
            ...     def write_file(self): pass
            >>> handler = MockIFileSystemHandler()
            >>> fsm.add_fs_handler(handler, name='unique_handler_3')
            >>> fsm.delete_fs_handler('unique_handler_3')
            True
            >>> fsm.has_fs_handler('unique_handler_3')
            False
        """
        _name = self.__root_handler_name if self.__root_handler_name else name
        if self.__file_sys_handler_dict.get(_name):
            del self.__file_sys_handler_dict[_name]
            return True
        return False

    def add_fs_handler(self, file_sys_handler: IFileSystemHandler, name: str = 'default') -> None:
        """
        Add an instance of IFileSystemHandler.

        Args:
            file_sys_handler (IFileSystemHandler): The file system handler instance to add.
            name (str): The name of the file system handler. Default is 'default'.

        Raises:
            ValueError: If the provided handler is not an instance of IFileSystemHandler or if a duplicate key is found.
        Examples:
            >>> fsm = FileSystemManager()
            >>> class MockIFileSystemHandler(IFileSystemHandler):
            ...     def __init__(self): pass
            ...     def append_file(self): pass
            ...     def copy_file(self): pass
            ...     def create_folders(self): pass
            ...     def delete_file(self): pass
            ...     def delete_folder(self): pass
            ...     def exists(self): pass
            ...     def get_file(self): pass
            ...     def get_file_object(self): pass
            ...     def get_folder(self): pass
            ...     def get_info(self): pass
            ...     def get_instance(self): pass
            ...     def list_files(self): pass
            ...     def move_file(self): pass
            ...     def move_folder(self): pass
            ...     def put_file(self): pass
            ...     def put_folder(self): pass
            ...     def write_file(self): pass
            >>> handler = MockIFileSystemHandler()
            >>> fsm.add_fs_handler(handler, name='unique_handler_4')
            >>> fsm.has_fs_handler('unique_handler_4')
            True
        """
        _name = self.__root_handler_name if self.__root_handler_name else name
        if not isinstance(file_sys_handler, IFileSystemHandler):
            message = f"{file_sys_handler} is not an instance of IFileSystemHandler."
            raise ValueError(message)
        existing_keys = []
        if self.__file_sys_handler_dict:
            existing_keys = list(self.__file_sys_handler_dict.keys())
            if _name in existing_keys:
                raise ValueError(
                    f"Duplicate key={_name} found. Please provide unique keys.")
            self.__file_sys_handler_dict[_name] = file_sys_handler
        else:
            self.__file_sys_handler_dict = {_name: file_sys_handler}

    def add_fs_handlers(self, file_sys_handler_dict: Dict[str, IFileSystemHandler]) -> None:
        """
        Add one or more instances of IFileSystemHandler.

        Args:
            file_sys_handler_dict (Dict[str, IFileSystemHandler]): Dictionary of file system handler instances to add.

        Raises:
            ValueError: If any provided handler is not an instance of IFileSystemHandler or if duplicate keys are found.
        Examples:
            >>> fsm = FileSystemManager()
            >>> class MockIFileSystemHandler(IFileSystemHandler):
            ...     def __init__(self): pass
            ...     def append_file(self): pass
            ...     def copy_file(self): pass
            ...     def create_folders(self): pass
            ...     def delete_file(self): pass
            ...     def delete_folder(self): pass
            ...     def exists(self): pass
            ...     def get_file(self): pass
            ...     def get_file_object(self): pass
            ...     def get_folder(self): pass
            ...     def get_info(self): pass
            ...     def get_instance(self): pass
            ...     def list_files(self): pass
            ...     def move_file(self): pass
            ...     def move_folder(self): pass
            ...     def put_file(self): pass
            ...     def put_folder(self): pass
            ...     def write_file(self): pass
            >>> handler1 = MockIFileSystemHandler()
            >>> handler2 = MockIFileSystemHandler()
            >>> fsm.add_fs_handlers({'handler1': handler1, 'handler2': handler2})
            >>> fsm.has_fs_handler('handler1')
            True
            >>> fsm.has_fs_handler('handler2')
            True
        """
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

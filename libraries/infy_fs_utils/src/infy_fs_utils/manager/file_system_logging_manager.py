# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

"""Module containing FileSystemLoggingManager"""

from typing import Dict
from .._common.singleton import Singleton
from ..interface.i_file_system_logging_handler import IFileSystemLoggingHandler


class FileSystemLoggingManager(metaclass=Singleton):
    """
    Factory class to get singleton logger object at application level.

    This class manages instances of IFileSystemLoggingHandler and ensures that only one instance
    of each handler exists at any given time.

    Attributes:
        __file_sys_logging_handler_dict (Dict[str, IFileSystemLoggingHandler]): Dictionary to store logging handlers.
    """

    __file_sys_logging_handler_dict: Dict[str,
                                          IFileSystemLoggingHandler] = None
    __root_handler_name = None

    def __init__(self) -> None:
        """
        Constructor for FileSystemLoggingManager.
        Example:
            >>> manager = FileSystemLoggingManager()
            >>> isinstance(manager, FileSystemLoggingManager)
            True
        """
        self.__file_sys_logging_handler_dict: {}

    def set_root_handler_name(self, name: str) -> None:
        """
        Sets the root handler name.

        Args:
            name (str): The name to set as the root handler name.

        Example:
            >>> from infy_fs_utils.manager.file_system_manager import FileSystemManager
            >>> fsm = FileSystemManager()
            >>> fsm.set_root_handler_name('root')
            >>> fsm._FileSystemManager__root_handler_name
            'root'
        """
        self.__root_handler_name = name

    def has_fs_logging_handler(self, name: str = 'default') -> bool:
        """
        Returns True if an instance of IFileSystemHandler exists.

        Args:
            name (str): The name of the file system handler. Defaults to 'default'.

        Returns:
            bool: True if the handler exists, False otherwise.

        Example:
            >>> from infy_fs_utils.manager.file_system_manager import FileSystemManager
            >>> from infy_fs_utils.interface.i_file_system_handler import IFileSystemHandler
            >>> FileSystemManager._instances = {}  # Reset the singleton instance
            >>> fsm = FileSystemManager()
            >>> fsm.has_fs_handler()
            False
            >>> class MockHandler(IFileSystemHandler):
            ...     def __init__(self, storage_config_data): pass
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
            >>> handler = MockHandler(storage_config_data={})
            >>> fsm.add_fs_handler(handler, name='unique_key')
            >>> fsm.has_fs_handler('unique_key')
            True
    """
        _name = self.__root_handler_name if self.__root_handler_name else name
        if self.__file_sys_logging_handler_dict:
            return _name in self.__file_sys_logging_handler_dict.keys()
        return False

    def get_fs_logging_handler(self, name: str = 'default') -> IFileSystemLoggingHandler:
        """
        Example:
            >>> from infy_fs_utils.manager.file_system_manager import FileSystemManager
            >>> from infy_fs_utils.interface.i_file_system_handler import IFileSystemHandler
            >>> fsm = FileSystemManager()
            >>> fsm.get_fs_handler() is None
            False
            >>> class MockHandler(IFileSystemHandler):
            ...     def __init__(self, storage_config_data): pass
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
            >>> handler = MockHandler(storage_config_data={})
            >>> fsm.add_fs_handler(handler, name='unique_key')
            >>> fsm.get_fs_handler('unique_key') is handler
            True
        """
        _name = self.__root_handler_name if self.__root_handler_name else name
        if self.__file_sys_logging_handler_dict:
            return self.__file_sys_logging_handler_dict.get(_name, None)
        return None

    def delete_fs_logging_handler(self, name: str = 'default') -> bool:
        """
        Deletes an instance of IFileSystemHandler.

        Args:
            name (str): The name of the file system handler. Defaults to 'default'.

        Returns:
            bool: True if the handler was deleted, False otherwise.

        Example:
            >>> from infy_fs_utils.manager.file_system_manager import FileSystemManager
            >>> from infy_fs_utils.interface.i_file_system_handler import IFileSystemHandler
            >>> fsm = FileSystemManager()
            >>> class MockHandler(IFileSystemHandler):
            ...     def __init__(self, storage_config_data): pass
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
            >>> handler = MockHandler(storage_config_data={})
            >>> fsm.add_fs_handler(handler, name='unique_key')
            >>> fsm.delete_fs_handler('unique_key')
            True
            >>> fsm.delete_fs_handler('unique_key')
            False
        """
        _name = self.__root_handler_name if self.__root_handler_name else name
        if self.__file_sys_logging_handler_dict and self.__file_sys_logging_handler_dict.get(_name, None):
            obj: IFileSystemLoggingHandler = self.__file_sys_logging_handler_dict.pop(
                _name)
            obj.unset_handler()
            del obj
            return True
        return False

    def add_fs_logging_handler(self, file_sys_logging_handler: IFileSystemLoggingHandler,
                               name: str = 'default') -> None:
        """
        Adds an instance of IFileSystemHandler.

        Args:
            file_sys_handler (IFileSystemHandler): The file system handler instance to add.
            name (str): The name of the file system handler. Defaults to 'default'.

        Raises:
            ValueError: If the handler is not an instance of IFileSystemHandler or if a duplicate key is found.

        Example:
            >>> from infy_fs_utils.manager.file_system_manager import FileSystemManager
            >>> from infy_fs_utils.interface.i_file_system_handler import IFileSystemHandler
            >>> fsm = FileSystemManager()
            >>> class MockHandler(IFileSystemHandler):
            ...     def __init__(self, storage_config_data): pass
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
            >>> handler = MockHandler(storage_config_data={})
            >>> fsm.add_fs_handler(handler)
            >>> fsm.has_fs_handler()
            True
            >>> fsm.add_fs_handler(handler)  # Attempt to add duplicate
            Traceback (most recent call last):
                ...
            ValueError: Duplicate key=default found. Please provide unique keys.
        """
        _name = self.__root_handler_name if self.__root_handler_name else name
        if not isinstance(file_sys_logging_handler, IFileSystemLoggingHandler):
            message = f"{file_sys_logging_handler} is not an instance of IFileSystemLoggingHandler."
            raise ValueError(message)
        existing_keys = []
        if self.__file_sys_logging_handler_dict:
            existing_keys = list(self.__file_sys_logging_handler_dict.keys())
            if _name in existing_keys:
                raise ValueError(
                    f"Duplicate key={_name} found. Please provide unique keys.")
            self.__file_sys_logging_handler_dict[_name] = file_sys_logging_handler
        else:
            self.__file_sys_logging_handler_dict = {
                _name: file_sys_logging_handler}

    def add_fs_logging_handlers(self, file_sys_logging_handler_dict: Dict[str, IFileSystemLoggingHandler]) -> None:
        """
        Adds one or more instances of IFileSystemHandler.

        Args:
            file_sys_handler_dict (Dict[str, IFileSystemHandler]): A dictionary of file system handlers to add.

        Raises:
            ValueError: If any handler is not an instance of IFileSystemHandler or if duplicate keys are found.

        Example:
            >>> from infy_fs_utils.manager.file_system_manager import FileSystemManager
            >>> from infy_fs_utils.interface.i_file_system_handler import IFileSystemHandler
            >>> fsm = FileSystemManager()
            >>> class MockHandler(IFileSystemHandler):
            ...     def __init__(self, storage_config_data): pass
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
            >>> handler_dict = {'handler1': MockHandler(storage_config_data={}), 'handler2': MockHandler(storage_config_data={})}
            >>> fsm.add_fs_handlers(handler_dict)
            >>> fsm.has_fs_handler('handler1')
            True
            >>> fsm.has_fs_handler('handler2')
            True
            >>> duplicate_dict = {'handler1': MockHandler(storage_config_data={})}
            >>> fsm.add_fs_handlers(duplicate_dict)  # Attempt to add duplicate
            Traceback (most recent call last):
                ...
            ValueError: Duplicate keys=['handler1'] found. Please provide unique keys.
        """
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

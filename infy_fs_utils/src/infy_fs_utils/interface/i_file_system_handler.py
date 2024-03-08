# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                   #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

"""Module containing IFileSystemHandler class"""

from abc import ABC, abstractmethod
from urllib.parse import urlparse
from ..data import StorageConfigData


class IFileSystemHandler(ABC):
    """Interface for abstracting file system operations."""

    SCHEME_TYPE_FILE = 'file'
    __scheme = None
    __storage_root_uri = None
    __bucket_name = None

    def __init__(self, storage_config_data: StorageConfigData):
        self.__storage_root_uri = storage_config_data.storage_root_uri
        parsed_url = urlparse(self.__storage_root_uri)
        self.__scheme = parsed_url.scheme
        self.__bucket_name = parsed_url.netloc+parsed_url.path
        self.__storage_config_data=storage_config_data

    @abstractmethod
    def get_instance(self):
        """Return instance of fsspec"""
        raise NotImplementedError

    @abstractmethod
    def get_file_object(self, file_path, mode='rb'):
        """Return file object"""
        raise NotImplementedError

    def read_file(self, file_path, mode='r', encoding='utf8'):
        """Returns content of a file"""
        raise NotImplementedError

    @abstractmethod
    def write_file(self, file_path, data, encoding='utf8'):
        """Writes/overwrites content to a given file"""
        raise NotImplementedError

    @abstractmethod
    def append_file(self, file_path, data, encoding='utf8'):
        """Appends content to a given file"""
        raise NotImplementedError

    @abstractmethod
    def delete_file(self, file_path):
        """Deletes a given file"""
        raise NotImplementedError

    @abstractmethod
    def list_files(self, directory_path, file_filter='*.*'):
        """Returns the list of files in a given directory"""
        raise NotImplementedError

    @abstractmethod
    def get_folder(self, source_dir, target_dir, recursive=True):
        """Downloads files from remote folder `source_dir` to local folder `target_dir`."""
        raise NotImplementedError

    @abstractmethod
    def put_folder(self, source_dir, target_dir, recursive=True):
        """Uploads files from local folder `source_dir` to remote folder `target_dir`."""
        raise NotImplementedError

    @abstractmethod
    def create_folders(self, dir_path, create_parents=True):
        """Create directory and parent directories if `create_parents=True`"""
        raise NotImplementedError

    @abstractmethod
    def move_file(self, source_path, target_path) -> str:
        """Moves a file from `source_path` to `target_path`."""
        raise NotImplementedError

    @abstractmethod
    def copy_file(self, source_path, target_path) -> str:
        """Copies a file from `source_path` to `target_path`."""
        raise NotImplementedError

    @abstractmethod
    def get_info(self, resource_path) -> dict:
        """Returns information about a resource."""
        raise NotImplementedError

    @abstractmethod
    def exists(self, resource_path) -> bool:
        """Returns True if resource exists."""
        raise NotImplementedError

    def get_scheme(self):
        """Returns scheme from `storage_root_uri`"""
        return self.__scheme

    def get_storage_root_uri(self):
        """Returns value of `storage_root_uri` set during initialization."""
        return self.__storage_root_uri

    def get_bucket_name(self):
        """Returns value of `bucket_name`."""
        return self.__bucket_name

    def get_abs_path(self, rel_path, include_scheme=True):
        """Returns absolute path for given `rel_path`"""
        scheme = self.__scheme if include_scheme else ''
        return scheme + self.__storage_root_uri + rel_path

    def get_storage_config_data(self):
        """Returns value of `storage_config_data` set during initialization."""
        return self.__storage_config_data
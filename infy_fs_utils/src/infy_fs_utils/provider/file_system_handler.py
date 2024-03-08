# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                   #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

"""Module containing FileSystemHandler class"""

import os
import uuid
import fsspec
from ..interface.i_file_system_handler import IFileSystemHandler
from ..data import StorageConfigData


class FileSystemHandler(IFileSystemHandler):
    """Class for abstracting file system operations using fsspec library"""

    def __init__(self, storage_config_data: StorageConfigData):
        super().__init__(storage_config_data)
        # Map to fsspec
        config_data = {
            'endpoint_url': storage_config_data.storage_server_url,
            'key': storage_config_data.storage_access_key,
            'secret': storage_config_data.storage_secret_key
        }
        self.__fs = fsspec.filesystem(
            self.get_scheme(), **config_data if config_data else {})

    def get_instance(self):
        """Return instance of fsspec"""
        return self.__fs

    def get_file_object(self, file_path, mode='rb'):
        """Return file object"""
        return self.__fs.open(self.__prepare_uri(file_path), mode)

    def read_file(self, file_path, mode='r', encoding='utf8'):
        """Returns content of a file"""
        with self.__fs.open(self.__prepare_uri(file_path), mode, encoding=encoding) as file:
            return file.read()

    def write_file(self, file_path, data, encoding='utf8'):
        """Writes/overwrites content to a given file"""
        # If the context finishes due to an (uncaught) exception, then the files are discarded and the
        # file target locations untouched.
        # Here move is added so that files have the read access . with only write there is no group read access
        mode = 'w'
        u_id = self.__get_uuid()[:5]
        temp_file_path = f'{os.path.dirname(file_path)}/{u_id}_{os.path.basename(file_path)}'
        with self.__fs.transaction:
            with self.__fs.open(self.__prepare_uri(temp_file_path), mode, encoding=encoding) as file:
                file.write(data)
        self.move_file(temp_file_path, file_path)

    def append_file(self, file_path, data, encoding='utf8'):
        """Appends content to a given file"""
        with self.__fs.open(self.__prepare_uri(file_path), 'a', encoding=encoding) as file:
            file.write(data)

    def delete_file(self, file_path):
        """Deletes a given file"""
        self.__fs.rm(self.__prepare_uri(file_path))

    def list_files(self, directory_path, file_filter=None):
        """Returns the list of files in a given directory"""
        if file_filter is None:
            return self.__list_all_files(directory_path)
        file_list = self.__fs.glob(self.__prepare_uri(
            f"{directory_path}/{file_filter}"))
        file_list = [self.__unprepare_uri(file) for file in file_list]
        return file_list

    def __list_all_files(self, file_path):
        """Returns the list of files in a given directory"""
        _file_path = self.__prepare_uri(file_path)
        file_list = []
        for root, _, files in self.__fs.walk(_file_path):
            for file in files:
                file_path = root + '/' + file
                file_list.append(file_path)
        file_list = [self.__unprepare_uri(file) for file in file_list]
        return file_list

    def get_folder(self, source_dir, target_dir, recursive=True):
        """Downloads files from remote folder `source_dir` to local folder `target_dir`."""
        self.__fs.get(self.__prepare_uri(source_dir),
                      target_dir, recursive=recursive)

    def put_folder(self, source_dir, target_dir, recursive=True):
        """Uploads files from local folder `source_dir` to remote folder `target_dir`."""
        self.__fs.put(os.path.abspath(source_dir),
                      self.__prepare_uri(target_dir), recursive=recursive)

    def create_folders(self, dir_path, create_parents=True):
        """Create directory and parent directories if `create_parents=True`"""
        self.__fs.mkdirs(self.__prepare_uri(dir_path), create_parents)

    def move_file(self, source_path, target_path) -> str:
        """Moves a file from `source_path` to `target_path`."""
        self.__fs.move(self.__prepare_uri(source_path),
                       self.__prepare_uri(target_path))
        return target_path + '/' + os.path.basename(source_path)

    def copy_file(self, source_path, target_path) -> str:
        """Copies a file from `source_path` to `target_path`."""
        self.__fs.copy(self.__prepare_uri(source_path),
                       self.__prepare_uri(target_path))
        return target_path + '/' + os.path.basename(source_path)

    def get_info(self, resource_path) -> dict:
        """Returns information about a resource."""
        return self.__fs.info(self.__prepare_uri(resource_path))

    def exists(self, resource_path) -> bool:
        """Returns True if resource exists."""
        try:
            # exists = self.__fs.exists(self.__prepare_uri(resource_path))
            _ = self.__fs.info(self.__prepare_uri(resource_path))
            return True
        except FileNotFoundError:
            pass
        return False
    # ----- private methods -----

    def __prepare_uri(self, path):

        _path = path.lstrip('/').replace('\\', '/').replace('//', '/')
        _path_delimit = "" if self.get_storage_root_uri().endswith("/") else "/"
        _new_path = f"{self.get_storage_root_uri()}{_path_delimit}{_path}"
        # _new_path = ''
        # for x in _path.split(":",1):
        #     if not _new_path:
        #         _new_path = x + "://"
        #     else:
        #         _new_path += x.lstrip('/').replace('\\',
        #                                            '/').replace('//', '/')
        return _new_path

    def __unprepare_uri(self, path):
        _path = path.replace(self.get_bucket_name(), "")
        return _path

    def __get_uuid(self):
        return str(uuid.uuid4())

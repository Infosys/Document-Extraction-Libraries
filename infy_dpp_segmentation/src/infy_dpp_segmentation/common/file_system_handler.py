# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#


"""Module containing FileSystemHandler class"""

import os
import uuid
from urllib.parse import urlparse
import fsspec

VERSION = "1.1.2"


class FileSystemHandler:
    """Class for abstracting file system operations using fsspec library"""

    SCHEME_TYPE_FILE = 'file'

    def __init__(self, storage_uri, config=None):
        parsed_url = urlparse(storage_uri)
        self.__storage_uri = storage_uri
        self.__fs = fsspec.filesystem(
            parsed_url.scheme, **config if config else {})
        self.__bucket_name = parsed_url.netloc+parsed_url.path
        self.__scheme = parsed_url.scheme

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

    def list_files(self, directory_path, file_filter='*.*'):
        """Returns the list of files in a given directory"""
        # TODO: to remove bucket name [self.__unprepare_uri(file) for file in self.__fs.glob(self.__prepare_uri(f"{directory_path}/{file_filter}")) ]
        return self.__fs.glob(self.__prepare_uri(f"{directory_path}/{file_filter}"))

    def list_files1(self, file_path):
        """Returns the list of files in a given directory"""
        _file_path = self.__prepare_uri(file_path)
        file_list = []
        for root, _, files in self.__fs.walk(_file_path):
            for file in files:
                file_path = os.path.join(root, file)
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

    def move_file(self, source_path, target_path):
        """Moves a file from `source_path` to `target_path`."""
        self.__fs.move(self.__prepare_uri(source_path),
                       self.__prepare_uri(target_path))

    def copy_file(self, source_path, target_path):
        """Copies a file from `source_path` to `target_path`."""
        self.__fs.copy(self.__prepare_uri(source_path),
                       self.__prepare_uri(target_path))

    def get_scheme(self):
        """Returns scheme from `storage_uri`"""
        return self.__scheme

    def get_storage_uri(self):
        """Returns value of `storage_uri` set during initialization."""
        return self.__storage_uri

    def get_abs_path(self, rel_path, include_scheme=True):
        """Returns absolute path for given `rel_path`"""
        scheme = self.__scheme if include_scheme else ''
        return scheme + self.__storage_uri + rel_path

    # ----- private methods -----
    def __prepare_uri(self, path):

        _path = path.lstrip('/').replace('\\', '/').replace('//', '/')
        _path_delimit = "" if self.__storage_uri.endswith("/") else "/"
        _new_path = f"{self.__storage_uri}{_path_delimit}{_path}"
        # _new_path = ''
        # for x in _path.split(":",1):
        #     if not _new_path:
        #         _new_path = x + "://"
        #     else:
        #         _new_path += x.lstrip('/').replace('\\',
        #                                            '/').replace('//', '/')
        return _new_path

    def __unprepare_uri(self, path):
        _path = path.replace(self.__bucket_name, "")
        return _path

    def __get_uuid(self):
        return str(uuid.uuid4())

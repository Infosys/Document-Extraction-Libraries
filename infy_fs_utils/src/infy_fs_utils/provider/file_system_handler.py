# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                   #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

"""Module containing FileSystemHandler class"""
import glob
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
        u_id = self.__get_uuid()
        temp_file_path = f'{os.path.dirname(file_path)}/{u_id}_{os.path.basename(file_path)}.tmp'
        self.__create_missing_parents(temp_file_path)
        # with self.__fs.transaction:
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

    def list_files(self, directory_path, file_filter=None, empty_file_name='empty.fsh'):
        """Returns the list of files in a given directory"""
        if file_filter is None:
            file_list = self.__list_all_files(directory_path)
        else:
            file_list = self.__fs.glob(self.__prepare_uri(
                f"{directory_path}/{file_filter}"))
            file_list = [self.__unprepare_uri(file) for file in file_list]
        if self.get_scheme() != 'file':
            file_list = [x for x in file_list if not os.path.basename(
                x) == empty_file_name]
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

    def get_folder(self, source_dir, target_dir, recursive=True, empty_file_name='empty.fsh'):
        """Downloads files from remote folder `source_dir` to local folder `target_dir`."""
        self.__fs.get(self.__prepare_uri(source_dir),
                      target_dir, recursive=recursive)
        if self.get_scheme() != 'file' and empty_file_name:
            for root, _, files in os.walk(target_dir):
                for file in files:
                    if file == empty_file_name:
                        os.remove(os.path.join(root, file))

    def put_folder(self, source_dir, target_dir, recursive=True):
        """Uploads files from local folder `source_dir` to remote folder `target_dir`."""
        if self.exists(target_dir):
            files_list = glob.glob(source_dir+'/**', recursive=True)
            for file in files_list:
                if os.path.isfile(file):
                    self.put_file(file, target_dir+'/' +
                                  os.path.relpath(file, source_dir))
        else:
            self.__fs.put(os.path.abspath(source_dir),
                          self.__prepare_uri(target_dir), recursive=recursive)

    def move_folder(self, source_dir, target_dir, recursive=True):
        """Moves files from remote folder `source_dir` to remote folder `target_dir`."""
        self.__fs.mv(self.__prepare_uri(source_dir),
                     self.__prepare_uri(target_dir), recursive)

    def delete_folder(self, dir_path, recursive=True):
        """Deletes a given directory"""
        self.__fs.rm(self.__prepare_uri(dir_path), recursive)

    def create_folders(self, dir_path, create_parents=True, empty_file_name='empty.fsh'):
        """Create directory and parent directories if `create_parents=True`"""
        if self.get_scheme() == 'file':
            self.__fs.mkdirs(self.__prepare_uri(dir_path), create_parents)
        else:  # Write an empty system file to create the directory
            dir_name_list = dir_path.split('/')
            dir_sub_path = ''
            for dir_name in dir_name_list:
                if dir_name:
                    dir_sub_path += '/' + dir_name
                    self.write_file(dir_sub_path + '/' + empty_file_name, '')

            # self.write_file(dir_path + '/' + empty_file_name, '')

    def move_file(self, source_path, target_path) -> str:
        """Moves a file from `source_path` to `target_path`."""
        # self.__my_print("move_file() ", threading.current_thread().name,
        #                 f"source_path: {self.__prepare_uri(source_path)}, target_path: {self.__prepare_uri(target_path)}")
        # try:
        self.__fs.move(self.__prepare_uri(source_path),
                       self.__prepare_uri(target_path))
        # except Exception as e:
        #     self.__my_print("move_file() Error:", threading.current_thread().name,
        #                     f"Exception: {e}\n", "Traceback:", traceback.format_exc())
        return target_path + '/' + os.path.basename(source_path)

    # def __my_print(self, *values: object):
    #     lock = threading.Lock()
    #     with lock:
    #         print(str(datetime.datetime.now()), values)

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

    def put_file(self, source_file, target_file):
        """Uploads a file from local `source_file` to remote `target_file`."""
        self.__create_missing_parents(target_file)
        self.__fs.put(source_file, self.__prepare_uri(target_file))

    def get_file(self, source_file, target_file):
        """Downloads a file from remote `source_file` to local `target_file`."""
        self.__fs.get(self.__prepare_uri(source_file), target_file)

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

    def __create_missing_parents(self, file_path):
        """Create parent directories if not exists only for local filesystem"""
        file_path = file_path.lstrip('/').replace('\\', '/').replace('//', '/')
        if self.get_scheme() == 'file':
            # If local file system, create parent directories because fsspec does not
            parent_dir_path = os.path.dirname(file_path)
            if not self.exists(parent_dir_path):
                self.create_folders(parent_dir_path)

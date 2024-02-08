# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import errno
import glob
import hashlib
import json
import math
import os
from pathlib import PurePath
import shutil
import time
import uuid
import zipfile
from datetime import datetime
from os import path
import mimetypes


class FileUtil:

    @staticmethod
    def get_file_exe(fullpath):
        return str(path.splitext(path.split(fullpath)[1])[1])

    @staticmethod
    def get_file_size_in_mb(doc):
        return round(os.path.getsize(doc)*0.000001, 2)

    @staticmethod
    def get_file_size_in_human_readable(file_path: str) -> str:
        size_in_bytes = os.path.getsize(file_path)
        if size_in_bytes == 0:
            return "0"
        size_name = ("B", "KB", "MB", "GB")
        i = int(math.floor(math.log(abs(size_in_bytes), 1024)))
        p = math.pow(1024, i)
        s = round(size_in_bytes / p, 2)
        return "%s %s" % (s, size_name[i])

    @staticmethod
    def get_files(folderpath, file_format, recursive=False, sort_by_date=None):
        '''
        Param:
            folderpath: str
            desc: root folder path to find the file_format type files

            file_format: str
            desc: one or comma separated values

        '''
        found_files = []
        for type in str(file_format).split(","):
            found_files += glob.glob(
                f"{folderpath}/*.{type}", recursive=recursive)
        if sort_by_date:
            found_files.sort(key=sort_by_date)
        return found_files

    @staticmethod
    def get_file(folderpath, file_wild_name, file_format="pdf"):
        return glob.glob(folderpath + "/*"+file_wild_name+"."+file_format)

    @staticmethod
    def read_file():
        pass

    @staticmethod
    def delete_file(file):
        os.remove(file)

    @staticmethod
    def create_dirs_if_absent(dir_name):
        '''
        Creates directories recursively if it doesn't exist.
        The dir_name can be relative or absolute

        Parameters:
            dir_name (string): Relative or absolute path of the directory
        '''
        dir_path = dir_name
        if not path.isdir(dir_path):
            os.makedirs(dir_path)

        return dir_path

    @staticmethod
    def load_json(file_path):
        data = None
        with open(file_path, encoding='utf-8') as file:
            data = json.load(file)

        if (not data):
            raise Exception('error is template dictionary json load')
        return data

    @classmethod
    def get_pages_from_filename(cls, image_file_path):
        try:
            pages_temp = int(os.path.basename(
                image_file_path).rsplit(".", 1)[0])
        except:
            pages_temp = "1"
        return pages_temp

    @staticmethod
    def get_uuid():
        return str(uuid.uuid4())

    @staticmethod
    def write_bytes_to_file(bytes, output_file):
        with open(output_file, "wb") as f:
            f.write(bytes)
        return

    @staticmethod
    def write_to_file(content, output_file, mode="w"):
        with open(output_file, mode) as f:
            f.write(content)
        return

    @staticmethod
    def copy_recursively(source, destination):
        try:
            shutil.copytree(source, destination)
        except OSError as err:
            # error caused if the source was not a directory
            if err.errno == errno.ENOTDIR:
                shutil.copy2(source, destination)

    @staticmethod
    def move_all(source, destination):
        for file in glob.glob(source+"/*.*"):
            FileUtil.move_file(file, destination)

    @staticmethod
    def move_file(source, destination):
        derived_file = destination + "/"+path.split(source)[1]
        error_val = None
        try:
            shutil.move(source, destination)
        except Exception as e:
            derived_file = None
            error_val = e.args
        return derived_file, error_val

    @staticmethod
    def copy_file(source, destination):
        derived_file = destination
        error_val = None
        try:
            if os.path.realpath(source) != os.path.realpath(destination):
                shutil.copy(source, destination)
        except Exception as e:
            derived_file = None
            error_val = e.args
        return derived_file, error_val

    @staticmethod
    def copy_tree(source, destination):
        if os.path.realpath(source) != os.path.realpath(destination):
            shutil.copytree(source, destination)

    @staticmethod
    def copy_to_work_dir(work_input_location, uuid, sub_path, doc_file):
        work_input_location, _ = FileUtil.create_uuid_dir(
            work_input_location, uuid)
        derived_file = work_input_location + \
            "/"+sub_path if sub_path != '' else work_input_location + "/" + \
            os.path.basename(doc_file)
        if sub_path != '':
            FileUtil.create_dirs_if_absent(os.path.dirname(derived_file))
        return FileUtil.copy_file(doc_file, derived_file)

    @staticmethod
    def create_uuid_dir(work_input_location, uuid=None):
        if not uuid:
            uuid = FileUtil.get_uuid()
        work_input_location = FileUtil.create_dirs_if_absent(
            work_input_location + "/" + uuid)
        return work_input_location, uuid

    @staticmethod
    def is_file_path_valid(file_path):
        file_path_abs = file_path
        if not path.isabs(file_path_abs):
            file_path_abs = path.abspath(file_path_abs)
        return path.isfile(file_path_abs)

    @staticmethod
    def get_time_str(format="%Y-%m-%d %H:%M:%S"):
        return time.strftime(format)

    @staticmethod
    def get_datetime_str(format="%Y%m%d_%H%M%S_%f"):
        return datetime.now().strftime(format)[:-3]

    @staticmethod
    def get_current_datetime():
        return FileUtil.get_datetime_str(format="%Y-%m-%d %H:%M:%S.%f")

    @classmethod
    def archive_file(cls, output_file_path, ext=".json"):
        try:
            if os.path.exists(output_file_path):
                suffix = FileUtil.get_datetime_str() + ext
                new_name = f'{output_file_path.replace(ext,"")}_{suffix}'
                os.rename(output_file_path, new_name)
        except Exception as e:
            print(e)

    @classmethod
    def save_to_json(cls, output_file_path, json_data, is_exist_archive=False):
        if is_exist_archive:
            FileUtil.archive_file(output_file_path)
        try:
            with open(output_file_path, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(e)

    @classmethod
    def unzip_file_to_path(cls, zip_file_path, output_folder_path):
        def get_folder_statistics(folder_path):
            folder_count = 0
            file_count = 0
            for root, dirnames, filenames in os.walk(folder_path):
                for dirname in dirnames:
                    folder_count += 1
                for filename in filenames:
                    file_count += 1
            folder_count -= 1  # Remove root folder
            return folder_count, file_count

        def get_file_stats(file_path):
            return {
                'size': str(round(os.path.getsize(file_path) / (1024 * 1024), 1)) + ' MB',
                'created_on': time.ctime(os.path.getctime(file_path)),
                'last_modified_on': time.ctime(os.path.getmtime(file_path))
            }

        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            zip_ref.extractall(output_folder_path)
            folder_count, file_count = get_folder_statistics(
                output_folder_path)
        return [f'{output_folder_path}/{filename}' for filename in zip_ref.namelist()]

    @staticmethod
    def get_file_hash_value(file_path: str) -> str:
        hash_lib = hashlib.sha1()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_lib.update(chunk)
        return hash_lib.hexdigest()

    @staticmethod
    def get_file_mime_type(filepath: str):
        # https://docs.python.org/3/library/mimetypes.html
        mtype = mimetypes.guess_type(filepath)[0]
        return mtype

    @classmethod
    def get_new_short_uuid(cls):
        return FileUtil.get_uuid()[:8]

    @classmethod
    def get_attr_id(cls, doc_id: str):
        return f"{doc_id[:8]}_{FileUtil.get_new_short_uuid()}"

    @classmethod
    def get_attr_val_id(cls, attr_id: str):
        return f"{attr_id}_{FileUtil.get_new_short_uuid()}"

    @staticmethod
    def get_file_path_detail(input_file_path):
        file_dir_path, file_name = os.path.split(input_file_path)
        file_name_no_ext, file_ext = os.path.splitext(file_name)
        file_dir = os.path.split(file_dir_path)[1]
        return {"fileDirPath": str(file_dir_path),
                "fileDir": str(file_dir),
                "fileName": str(file_name),
                "fileExtension": str(file_ext),
                "fileNameWithoutExt": str(file_name_no_ext)}
    @classmethod
    def write_output(cls, data_dict, root_path=""):
        """
        Breaks up a dictionary to individual key-value files where key is name of the file
        and value is content of the file. 
        root_path = `` leave as blank when app is running inside a container so that `ContainerOp` 
                       can read the value
        """

        try:
            # This path should not be changed as it's required for K8S ContainerOp to work
            output_file_list=[]
            for key in data_dict.keys():
                output_file_path = f'{root_path}/{key}.txt'
                cls.__write_to_text_file(output_file_path, data_dict[key])
                print('Output written to', output_file_path)
                output_file_list.append(output_file_path)
            return output_file_list    
        except Exception as ex:
            print('Error occurred in write_output()', ex)
    @classmethod
    def __write_to_text_file(cls, output_file_path, data):
        try:
            with open(output_file_path, "w", encoding="utf-8") as file:
                file.write(data)
        except Exception as ex:
            message = 'Error occurred in __write_to_text_file()'
            print(message, ex)
            raise ValueError(message, ex)

    @classmethod
    def empty_dir(cls,folder):
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e)) 

    @classmethod
    def safe_file_path(cls, file_path):
        return file_path.replace("\\","/").replace("//","/")
    
    @classmethod
    def get_file_path_str_hash_value(cls, file_path: str) -> str:
        # Assumes the default UTF-8
        hash_object = hashlib.md5(str(PurePath(file_path)).encode())
        return hash_object.hexdigest()
    
    @classmethod
    def generate_file_lock(cls, file_path, queue_path, fs_handler):
        is_locked = False
        processed_files_unique_value = FileUtil.get_file_path_str_hash_value(
            file_path)
        fs_handler.create_folders(queue_path)
        processed_files_list = [os.path.basename(f) for f in fs_handler.list_files1(queue_path) ]
        if processed_files_unique_value not in processed_files_list:
            fs_handler.write_file(f"{queue_path}/{processed_files_unique_value}", data=file_path)
            is_locked = True
        return is_locked
    
    @classmethod
    def unlock_file(cls, file_path, queue_path, fs_handler):
        try:
            processed_files_unique_value = FileUtil.get_file_path_str_hash_value(
                file_path)
            fs_handler.delete_file(f"{queue_path}/{processed_files_unique_value}")
        except:
            pass

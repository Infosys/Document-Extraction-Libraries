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
import shutil
import time
import uuid
import zipfile
from datetime import datetime
from os import path
from pathlib import PurePath


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
            found_files = [file_path for file_path in glob.glob(
                f"{folderpath}/{type}", recursive=recursive) if os.path.isfile(file_path)]

        if sort_by_date:
            found_files.sort(key=sort_by_date)
        return found_files

    @staticmethod
    def get_file(folderpath, file_wild_name, file_format="pdf"):
        return glob.glob(folderpath + "/*"+file_wild_name+"."+file_format)

    @staticmethod
    def read_file(file_path):
        with open(file_path, encoding='utf-8') as f:
            contents = f.read()
        return contents

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
        with open(file_path) as file:
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
    def get_hex_uuid():
        return str(uuid.uuid4().hex)

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
        error_val = None
        try:
            destination_cp = destination
            if os.path.isdir(destination):
                filename = os.path.basename(source)
                destination = os.path.join(destination, filename)
            if os.path.isfile(source):
                shutil.move(source, destination)
            else:
                shutil.rmtree(destination, ignore_errors=True)
                shutil.move(source, destination_cp)
        except Exception as e:
            destination = None
            error_val = e.args
        return destination, error_val

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
    def create_uuid_dir(work_input_location, uuid):
        # if not uuid:
        #     uuid = FileUtil.get_uuid()
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
            with open(output_file_path, 'w') as f:
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
        return [f'{output_folder_path}/{filename}' for filename in zip_ref.namelist() if os.path.isfile(f'{output_folder_path}/{filename}')]

    @staticmethod
    def get_file_hash_value(file_path: str) -> str:
        hash_lib = hashlib.sha1()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_lib.update(chunk)
        return hash_lib.hexdigest()

    @staticmethod
    def get_file_path_str_hash_value(file_path: str) -> str:
        # Assumes the default UTF-8
        hash_object = hashlib.md5(str(PurePath(file_path)).encode())
        return hash_object.hexdigest()

    @staticmethod
    def remove_files(file_list):
        for file in file_list:
            if file:
                os.remove(file)

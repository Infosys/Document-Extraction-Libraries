# ===============================================================================================================#
# Copyright 2020 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import os
from os import path
import shutil
import json
import hashlib


class TestUtil:

    @staticmethod
    def create_dirs_if_absent(dir_name):
        '''
        Creates directories recursively if it doesn't exist.
        The dir_name can be relative or absolute

        Parameters:
            dir_name (string): Relative or absolute path of the directory
        '''
        dir_path = dir_name
        try:
            if not path.isabs(dir_path):
                dir_path = path.abspath(dir_path)
            if not path.isdir(dir_path):
                os.makedirs(dir_path)
        except Exception:
            pass

        return dir_path

    @staticmethod
    def remove_files(file_list):
        """Removes file from path"""
        for file in file_list:
            if os.path.exists(file):
                os.remove(file)

    @staticmethod
    def save_to_json(out_file, data):
        """This methos saves data to json file"""
        is_saved, error = True, None
        try:
            with open(out_file, "w") as f:
                json.dump(data, f, indent=4)
        except Exception as ex:
            is_saved, error = False, ex.args[0]
        return is_saved, error

    @staticmethod
    def copy_files(source_path, destination_path):
        # Check if source path IS folder THEN copy all files
        if path.isdir(source_path):
            files = os.listdir(source_path)
            for file_name in files:
                full_file_name = os.path.join(source_path, file_name)
                if os.path.isfile(full_file_name):
                    shutil.copy(full_file_name, destination_path)
        else:
            # Check if destination path IS folder THEN create target file name
            _destination_path = destination_path
            file_name = os.path.basename(source_path)
            if path.isdir(_destination_path):
                _destination_path = path.join(_destination_path, file_name)

            shutil.copyfile(source_path, _destination_path)

    @staticmethod
    def load_json(file_path):
        data = None
        with open(file_path, encoding='utf-8') as file:
            data = json.load(file)

        if (not data):
            raise Exception('error is template dictionary json load')
        return data

    @staticmethod
    def get_file_hash_value(file_path: str) -> str:
        hash_lib = hashlib.sha1()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_lib.update(chunk)
        return hash_lib.hexdigest()

    @staticmethod
    def compare_json_file(file_path_1, file_path_2):
        """Compare two JSON files and return if same or different"""
        if TestUtil.get_file_hash_value(file_path_1) == TestUtil.get_file_hash_value(file_path_2):
            return True
        return False

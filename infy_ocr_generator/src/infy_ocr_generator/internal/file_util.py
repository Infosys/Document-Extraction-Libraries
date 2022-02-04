# ===============================================================================================================#
#
# Copyright 2021 Infosys Ltd.
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at
# http://www.apache.org/licenses/
#
# ===============================================================================================================#

import os
from os import path
import json
import copy


class FileUtil:

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
        for file in file_list:
            os.remove(file)

    @staticmethod
    def save_to_json(out_file, data):
        is_saved, error = True, None
        try:
            with open(out_file, "w") as f:
                json.dump(data, f, indent=4)
        except Exception as ex:
            is_saved, error = False, ex.args[0]
        return is_saved, error

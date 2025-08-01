# ===============================================================================================================#
# Copyright 2020 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import os
import json
import copy
import shutil
from os import path


class FileUtil:
    "Util class for file activities"
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
        except:
            pass

        return dir_path

    @staticmethod
    def remove_files(file_list):
        """Remove files"""
        for file in file_list:
            os.remove(file)

    @staticmethod
    def save_to_json(out_file, data):
        """Save json files"""
        is_saved, error = True, None
        try:
            with open(out_file, "w") as f:
                json.dump(data, f, indent=4)
        except Exception as ex:
            is_saved, error = False, ex.args[0]
        return is_saved, error

    @staticmethod
    def get_updated_config_dict(from_dict, default_dict):
        """compare input config and update missing default keys"""
        config_dict_temp = copy.deepcopy(default_dict)
        for key in from_dict:
            if isinstance(from_dict[key], dict):
                config_dict_temp[key] = FileUtil.get_updated_config_dict(
                    from_dict[key], config_dict_temp[key])
            else:
                config_dict_temp[key] = from_dict[key]
        return config_dict_temp

    @staticmethod
    def move(src, dst):
        """Method to move file"""
        shutil.move(src, dst)

    @staticmethod
    def copy(src, dst):
        """Mathod to copy file"""
        shutil.copy(src, dst)

# ===============================================================================================================#
#
# Copyright 2021 Infosys Ltd.
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at
# http://www.apache.org/licenses/
#
# ===============================================================================================================#

import os
import re
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

    @staticmethod
    def load_json(file_path):
        data = None
        with open(file_path, encoding='utf-8') as file:
            data = json.load(file)

        if (not data):
            raise Exception('error is template dictionary json load')
        return data

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
    def lookp_up_page(total_pages, page_list):
        pages = []
        for pnum in page_list:
            pnum = pnum if (isinstance(pnum, str) and ((
                ":" in pnum) or ("-" in pnum))) else int(pnum)
            if isinstance(pnum, str):
                num_arr = [int(num)
                           for num in re.split('-|:', pnum) if len(num) > 0]
                if bool(re.match(r'^-?[0-9]+\:{1}-?[0-9]+$', pnum)):
                    page_arr = FileUtil.__get_range_val(total_pages+1)
                    if (num_arr[0] < 0 and num_arr[1] < 0) or (num_arr[0] > 0 and num_arr[1] > 0):
                        num_arr.sort()
                    num_arr[0] = num_arr[0] if num_arr[0] > 0 else num_arr[0]-1
                    num_arr[1] = num_arr[1] + \
                        1 if num_arr[1] > 0 else num_arr[1]

                    pages += page_arr[num_arr[0]: num_arr[1]]
                elif bool(re.match(r'^-?[0-9]+\:{1}$', pnum)):
                    page_arr = FileUtil.__get_range_val(total_pages)
                    pages += page_arr[num_arr[0]:]
                elif bool(re.match(r'^\:{1}-?[0-9]+$', pnum)):
                    page_arr = FileUtil.__get_range_val(
                        total_pages+1, position=1)
                    pages += page_arr[:num_arr[0]]
                else:
                    raise Exception
            elif pnum < 0:
                pages += [FileUtil.__get_range_val(
                    total_pages, position=1)[pnum]]
            elif pnum > 0:
                pages.append(pnum)
            else:
                raise Exception
        return pages

    def __get_range_val(n, position=0):
        return [i for i in range(position, n+1)]

    @staticmethod
    def get_updated_within_box(within_bbox, scaling_factor):
        if(len(within_bbox) > 0):
            for i in [0, 2]:
                within_bbox[i] = round(
                    within_bbox[i] * scaling_factor.get('hor', 1))
            for i in [1, 3]:
                within_bbox[i] = round(
                    within_bbox[i] * scaling_factor.get('ver', 1))
        return within_bbox

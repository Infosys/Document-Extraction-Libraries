# ===============================================================================================================#
# Copyright 2020 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import json
import glob
import shutil
import os
from urllib.request import pathname2url


class TestingUtils:
    @staticmethod
    def load_json(file_path):
        data = None
        with open(file_path) as file:
            data = json.load(file)
        return data

    @staticmethod
    def save_file(data, output_file, is_json=False):
        content = data
        if (is_json and content):
            content = json.dumps(data, indent=3)

        with open(output_file, "w") as f:
            f.write(content)
        return

    @staticmethod
    def get_files(folderpath, file_format="*.jpg", sort_key=None, is_recursive=False):
        files = glob.glob(folderpath + "/"+file_format, recursive=is_recursive)
        if (sort_key):
            files.sort(key=sort_key)
        return files

    @staticmethod
    def create_dirs_if_absent(dir_name):
        '''
        Creates directories recursively if it doesn't exist.
        The dir_name can be relative or absolute

        Parameters:
            dir_name (string): Relative or absolute path of the directory
        '''
        dir_path = dir_name
        if not os.path.isabs(dir_path):
            dir_path = os.path.abspath(dir_path)
        if not os.path.isdir(dir_path):
            os.makedirs(dir_path)

        return dir_path

    # @staticmethod
    # def save_as_html_using_template(template_file_path, data_dict, output_file_path):
    #     ## install it manually ##
    #     # from jinja2 import Template
    #     with open(template_file_path) as file_:
    #         template = Template(file_.read())
    #         html_data = template.render(
    #             data_dict)
    #     TestingUtils.save_file(html_data, output_file_path, is_json=False)

    @staticmethod
    def copy_file(source_file_path, destination_file_path):
        shutil.copyfile(source_file_path, destination_file_path)

    @staticmethod
    def copy_folder(source_folder, destination_folder):
        shutil.copytree(source_folder, destination_folder)

    @staticmethod
    def move_folder(source_folder, destination_folder):
        shutil.move(source_folder, destination_folder)

    @staticmethod
    def encode_path(path_raw):
        return pathname2url(path_raw)

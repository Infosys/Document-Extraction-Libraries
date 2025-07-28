# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

"""Module for global fixtures"""

import shutil
import glob
import time
import json
import os
import pytest

version = "0.0.1"


@pytest.fixture(scope="module")
def create_root_folders():
    """Create root folder for testing"""
    return __create_folders


@pytest.fixture(scope="module")
def copy_files_to_root_folder() -> []:
    """Create root folder for testing"""
    return __copy_files_to_root_folder


@pytest.fixture(scope="module")
def update_json_file() -> []:
    """Update json file"""
    return __update_json_file


@pytest.fixture(scope="module")
def backup_folder():
    """Backup folder for testing"""
    return __backup_folder


@pytest.fixture(scope="module")
def restore_folder():
    """Backup folder for testing"""
    return __restore_folder


#### Private methods ####
def __copy_files_to_root_folder(files_to_copy: [], limit: int = -1):
    __files_expanded = []
    for file_to_copy in files_to_copy:
        if "*" in file_to_copy[0]:
            all_files = glob.glob(
                file_to_copy[1] + '/**/' + file_to_copy[0], recursive=True)
            all_files = [[os.path.basename(x), os.path.dirname(x),
                          file_to_copy[2] + '/' + os.path.dirname(os.path.relpath(x, file_to_copy[1]))]
                         for x in all_files]
            __files_expanded.extend(all_files)
        else:
            __files_expanded.append(file_to_copy)
    if limit > 0:
        __files_expanded = __files_expanded[:limit]

    for file_to_copy in __files_expanded:
        file1 = os.path.abspath(file_to_copy[1] + '/' + file_to_copy[0])
        file2 = os.path.abspath(file_to_copy[2] + '/' + file_to_copy[0])
        if os.path.exists(file2):
            os.remove(file2)
        os.makedirs(os.path.dirname(file2), exist_ok=True)
        shutil.copy(file1, file2)
    return __files_expanded


def __create_folders(folder_paths: []):
    for folder_path in folder_paths:
        __create_folder(folder_path)


def __create_folder(folder_path: str):
    # If folder already exists, archive it
    if os.path.exists(folder_path):
        try:
            folder_name = os.path.basename(folder_path)
            new_folder_name = folder_name + "_" + \
                time.strftime("%Y%m%d_%H%M%S")
            new_folder_path = os.path.dirname(
                folder_path) + "/_ARCHIVE/" + new_folder_name
            shutil.move(folder_path, new_folder_path)
        except OSError as error:
            message = "Cannot archive folder: " + folder_path + str(error.args)
            raise ValueError(message) from error
    os.makedirs(folder_path)


def __update_json_file(file_path, key_path, value):
    with open(file_path, 'r', encoding='utf-8') as f:
        input_config_data = json.load(f)
        keys = key_path.split('.')
        temp = input_config_data
        for key in keys[:-1]:
            temp = temp[key]
        temp[keys[-1]] = value
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(input_config_data, f, indent=4)


def __backup_folder(source_root_folder_path, backup_folder_path):
    if os.path.exists(source_root_folder_path):
        try:
            folder_name = os.path.basename(source_root_folder_path)
            new_folder_path = backup_folder_path + "/" + folder_name
            # delete old backup first
            if os.path.exists(new_folder_path):
                shutil.rmtree(new_folder_path)
            # backup
            shutil.move(source_root_folder_path, new_folder_path)
        except OSError as error:
            message = "Cannot backup folder: " + \
                source_root_folder_path + str(error.args)
            raise ValueError(message) from error


def __restore_folder(backup_folder_path, source_root_folder_path):
    try:
        shutil.copytree(backup_folder_path, source_root_folder_path)
    except OSError as error:
        message = "Cannot restore folder: " + \
            backup_folder_path + str(error.args)
        raise ValueError(message) from error

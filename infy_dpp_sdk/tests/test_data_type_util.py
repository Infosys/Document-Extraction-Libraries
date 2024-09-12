# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

"""Testing module"""

import json
import pytest
from infy_dpp_sdk.common.data_type_util import DataTypeUtil

DATA_DICT = None
SAMPLE_FILE_PATH = r".\data\sample\config\dpp_pipeline1_input_config.json"


@pytest.fixture(scope='module', autouse=True)
def pre_test():
    """Initialization method"""


def test_get_by_key_path_1():
    """Test method"""
    with open(SAMPLE_FILE_PATH, encoding='utf-8') as f1:
        data_dict = json.load(f1)
    value = DataTypeUtil().get_by_key_path(
        data_dict, 'processor_list[2].enabled', raise_error=True)
    assert value is True


def test_update_by_key_path_1():
    """Test method"""
    with open(SAMPLE_FILE_PATH, encoding='utf-8') as f1:
        data_dict = json.load(f1)
    assert data_dict['processor_list'][2]['enabled'] is True
    DataTypeUtil().update_by_key_path(
        data_dict, 'processor_list[2].enabled', False, raise_error=True)
    assert data_dict['processor_list'][2]['enabled'] is False


def test_get_all_key_paths_1():
    """Test method"""
    with open(SAMPLE_FILE_PATH, encoding='utf-8') as f1:
        data_dict = json.load(f1)
    key_paths = DataTypeUtil().get_all_key_paths(data_dict)
    assert len(key_paths) == 31
    assert key_paths[0] == ['name', 'pipeline1']

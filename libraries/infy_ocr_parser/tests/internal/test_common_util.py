# ===============================================================================================================#
# Copyright 2020 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import pytest
from infy_ocr_parser._internal.common_util import CommonUtil
# pages_lst = [1 to 15]. len 15
pages_lst = [{"page": i, "bbox": [0, 0, 0, 0]} for i in range(1, 16)]


def test_page_range_1():
    reg_def_obj = {
        "pageNum": [2]
    }
    pages = CommonUtil.get_lookup_pages(reg_def_obj, pages_lst)
    assert pages == [2]


def test_page_range_2():
    reg_def_obj = {
        "pageNum": [-10]
    }
    pages_1 = CommonUtil.get_lookup_pages(reg_def_obj, pages_lst)
    reg_def_obj = {
        "pageNum": ["-10"]
    }
    pages_2 = CommonUtil.get_lookup_pages(reg_def_obj, pages_lst)
    assert pages_1 == pages_2 and pages_1 == [6]


def test_page_range_3():
    reg_def_obj = {
        "pageNum": ["10:-5"]
    }
    pages = CommonUtil.get_lookup_pages(reg_def_obj, pages_lst)
    assert pages == [10, 11]


def test_page_range_4():
    reg_def_obj = {
        "pageNum": ["10:"]
    }
    pages = CommonUtil.get_lookup_pages(reg_def_obj, pages_lst)
    assert pages == [10, 11, 12, 13, 14, 15]


def test_page_range_5():
    reg_def_obj = {
        "pageNum": [":5", "6:9", 10, "11:"]
    }
    pages = CommonUtil.get_lookup_pages(reg_def_obj, pages_lst)
    assert pages == [page_dict['page']
                     for page_dict in pages_lst]


def test_page_range_6():
    reg_def_obj = {
        "pageNum": []
    }
    pages = CommonUtil.get_lookup_pages(reg_def_obj, pages_lst)
    assert pages == [page_dict['page']
                     for page_dict in pages_lst]


def test_page_range_7():
    reg_def_obj = {
        "pageNum": ["a-5"]
    }
    with pytest.raises(Exception):
        pages = CommonUtil.get_lookup_pages(reg_def_obj, pages_lst)


def test_page_range_8():
    reg_def_obj = {
        "pageNum": ["--5"]
    }
    with pytest.raises(Exception):
        pages = CommonUtil.get_lookup_pages(reg_def_obj, pages_lst)


def test_page_range_9():
    reg_def_obj = {
        "pageNum": ["-5:-1"]
    }
    pages = CommonUtil.get_lookup_pages(reg_def_obj, pages_lst)
    assert pages == [11, 12, 13, 14, 15]


def test_page_range_9_1():
    reg_def_obj = {
        "pageNum": ["-1:-5"]
    }
    pages = CommonUtil.get_lookup_pages(reg_def_obj, pages_lst)
    assert pages == [11, 12, 13, 14, 15]


def test_page_range_10():
    reg_def_obj = {
        "pageNum": ["-1:-1"]
    }
    pages = CommonUtil.get_lookup_pages(reg_def_obj, pages_lst)
    assert pages == [15]


def test_page_range_11():
    reg_def_obj = {
        "pageNum": ["-6:11"]
    }
    pages = CommonUtil.get_lookup_pages(reg_def_obj, pages_lst)
    assert pages == [10, 11]


def test_page_range_12():
    reg_def_obj = {
        "pageNum": ["10:11"]
    }
    pages = CommonUtil.get_lookup_pages(reg_def_obj, pages_lst)
    assert pages == [10, 11]


def test_page_range_13():
    reg_def_obj = {
        "pageNum": ["11:10"]
    }
    pages = CommonUtil.get_lookup_pages(reg_def_obj, pages_lst)
    assert pages == [10, 11]


def test_invalid_keys_present():
    truth_data_dict = {'a': 1, 'b': 2}
    test_data_dict = {'a': 1, 'b': 2, 'c': 3}
    invalid_keys = CommonUtil.get_invalid_keys(truth_data_dict, test_data_dict)
    assert invalid_keys == ['c']


def test_invalid_keys_absent():
    truth_data_dict = {'a': 1, 'b': 2}
    test_data_dict = {'a': 1, 'b': 2}
    invalid_keys = CommonUtil.get_invalid_keys(truth_data_dict, test_data_dict)
    assert invalid_keys == []

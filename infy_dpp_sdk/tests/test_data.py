# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                   #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import infy_dpp_sdk


def test_config_data_1():
    """Test method"""
    result = infy_dpp_sdk.data.ConfigData(config_data=None)
    assert None is result.config_data


def test_document_data_1():
    """Test method"""
    metadata_dict = {
        'standard_data': {
            "filepath": {
                "value": r"docs\dummy.pdf"
            }
        },
        'extracted_data': None}
    page_data = [{'page': '1'}]
    result = infy_dpp_sdk.data.DocumentData(
        metadata=metadata_dict, page_data=page_data)
    assert "dummy.pdf" == result.metadata.standard_data.filename.value and 1 == result.page_data[
        0].page


def test_extracted_data_1():
    """Test method"""
    extracted_data = infy_dpp_sdk.data.ExtractedData()
    extracted_data.handwritten = False
    assert False is extracted_data.handwritten


def test_page_data_1():
    """Test method"""
    result = infy_dpp_sdk.data.PageData(page="1", metadata=None)
    assert 1 == result.page


def test_page_data_2():
    """Test method"""
    metadata_dict = {
        'standard_data': None,
        'extracted_data': None}
    result = infy_dpp_sdk.data.PageData(
        page="1", metadata=metadata_dict)
    assert None is result.metadata.standard_data


def test_page_data_3():
    """Test method"""
    metadata_dict = {
        'standard_data': {
            "filepath": {
                "value": r"docs\dummy.pdf"
            }
        },
        'extracted_data': None}
    result = infy_dpp_sdk.data.PageData(
        page="1", metadata=metadata_dict)
    assert "dummy.pdf" == result.metadata.standard_data.filename.value

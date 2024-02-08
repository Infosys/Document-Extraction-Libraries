# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import infy_dpp_sdk


def test_generate_schema():
    """Test method"""
    result = infy_dpp_sdk.data.document_data.DocumentData.schema_json(indent=2)
    with open("./docs/document_data_schema.json", "w", encoding='utf-8') as file:
        file.write(result)
    assert result is not None


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
    result = infy_dpp_sdk.data.document_data.DocumentData(
        metadata=metadata_dict, page_data=page_data)
    assert "dummy.pdf" == result.metadata.standard_data.filename.value and 1 == result.page_data[
        0].page

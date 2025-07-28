# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import infy_dpp_sdk


def test_generate_schema():
    """Test method"""
    result = infy_dpp_sdk.data.DocumentData.schema_json(indent=2)
    with open("./docs/document_data_schema.json", "w", encoding='utf-8') as file:
        file.write(result)
    assert result is not None

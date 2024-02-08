# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import infy_dpp_sdk


def test_extracted_data_1():
    """Test method"""
    extracted_data = infy_dpp_sdk.data.extracted_data.ExtractedData()
    extracted_data.handwritten = False
    assert False is extracted_data.handwritten

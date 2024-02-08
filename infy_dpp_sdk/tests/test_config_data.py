# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import infy_dpp_sdk


def test_config_data_1():
    """Test method"""
    result = infy_dpp_sdk.data.config_data.ConfigData(config_data=None)
    assert None is result.config_data

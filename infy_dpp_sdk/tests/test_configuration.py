# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                   #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

"""Testing module"""

import pytest
import infy_dpp_sdk

CONTAINER_ROOT_PATH = f"C:/temp/unittest/infy_dpp_sdk/{__name__}/CONTAINER"


@pytest.fixture(scope='module', autouse=True)
def pre_test():
    """Initialization method"""
    # Configure client properties
    client_config_data = infy_dpp_sdk.ClientConfigData(
        **{
            "container_data": {
                "container_root_path": f"{CONTAINER_ROOT_PATH}",
            }
        })
    infy_dpp_sdk.ClientConfigManager().load(client_config_data)


def test_client_config_manager():
    """Test method"""
    # Retrieve back values set through ClientConfigManager just for validation.
    client_config_data = infy_dpp_sdk.ClientConfigManager().get()
    assert client_config_data
    print(client_config_data.dict())


def test_app_config_manager():
    """Test method"""
    # The values provided through ClientConfigManager should be reflected in AppConfigManager.
    # AppConfigManager is available globally both inside the SDK and outside (via namespace).
    app_config = infy_dpp_sdk.common.AppConfigManager().get_app_config()
    assert app_config is not None
    assert app_config['CONTAINER']['CONTAINER_ROOT_PATH'] == f"{CONTAINER_ROOT_PATH}"

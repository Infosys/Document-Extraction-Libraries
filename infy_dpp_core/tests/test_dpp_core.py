# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import pytest
import os
import infy_dpp_sdk
import infy_dpp_core

# use sample1 for pdf and sample2 for image
DATA_FOLDER_PATH = os.path.abspath('./data/test')
# for pdf use this
PROCESSOR_INPUT_CONFIG_PATH_PDF = os.path.abspath(
    './data/test/config/sample1_pipeline_input_config_data.json')
# for image use this
PROCESSOR_INPUT_CONFIG_PATH_IMG = os.path.abspath(
    './data/test/config/sample2_pipeline_input_config_data.json')
TEST_OUTPUT_FOLDER_PATH = os.path.abspath('./data/test/output')


@pytest.fixture(scope='module', autouse=True)
def pre_test():
    """Initialization method"""
    os.chdir('src')
    # Configure client properties
    CLIENT_CONFIG_DATA_DICT = {
        "storage_data": {
            "storage_uri": f"file://{DATA_FOLDER_PATH}",
            "storage_server_url": None,
            "storage_access_key": None,
            "storage_secret_key": None
        },
        "container_data": {
            "container_root_path": f"{DATA_FOLDER_PATH}",
        }
    }
    infy_dpp_core.ConfigurationManager().load(
        infy_dpp_core.ClientConfigData(**CLIENT_CONFIG_DATA_DICT))


def test_dpp_core_1():
    """
        Test case for dpp_core pdf
    """
    # -------- Config Data -----------
    config_data_json = infy_dpp_core.common.FileUtil.load_json(
        PROCESSOR_INPUT_CONFIG_PATH_PDF)

    # --------- Run the pipeline ------------
    orchestrator_native_obj: infy_dpp_sdk.interface.i_orchestrator_native.IOrchestratorNative = None
    orchestrator_native_obj = infy_dpp_sdk.orchestrator.controller.OrchestratorNativeBasic(
        config_data_json)
    response_data_list = orchestrator_native_obj.run_batch()

    assert response_data_list[0].context_data.get('request_closer') is not None


def test_dpp_core_2():
    """
        Test case for dpp_core image
    """
    # -------- Config Data -----------
    config_data_json = infy_dpp_core.common.FileUtil.load_json(
        PROCESSOR_INPUT_CONFIG_PATH_IMG)

    # --------- Run the pipeline ------------
    orchestrator_native_obj: infy_dpp_sdk.interface.i_orchestrator_native.IOrchestratorNative = None
    orchestrator_native_obj = infy_dpp_sdk.orchestrator.controller.OrchestratorNativeBasic(
        config_data_json)
    response_data_list = orchestrator_native_obj.run_batch()

    assert response_data_list[0].context_data.get('request_closer') is not None

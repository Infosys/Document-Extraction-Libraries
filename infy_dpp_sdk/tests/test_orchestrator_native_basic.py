# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import os
import infy_dpp_sdk

DATA_FOLDER_PATH = os.path.abspath('./data')
PROCESSOR_INPUT_CONFIG_PATH = f'{DATA_FOLDER_PATH}/config/uc_01_pipeline_input_config.json'


def test_page_data_1():
    """Test method"""
    orchestrator_native_obj = infy_dpp_sdk.orchestrator.controller.OrchestratorNativeBasic(
        pipeline_input_config_file_path=PROCESSOR_INPUT_CONFIG_PATH)
    response_data_list = orchestrator_native_obj.run_batch()
    print(response_data_list)

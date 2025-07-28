# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

"""Module containing Constants class"""
import importlib.metadata


class Constants():
    """Constants class"""
    FSH_DPP = 'dpp-fsh'
    FSLH_DPP = 'dpp-fslh'

    # ----- Private Constants ----- #
    try:
        _DPP_VERSION = importlib.metadata.version('infy_dpp_sdk')
    except importlib.metadata.PackageNotFoundError:
        _DPP_VERSION = "0.0.0"
    _ORCHESTRATOR_ROOT_PATH = '/data/temp/work/dpp_orchestrator'
    _ORCHESTRATOR_SNAPSHOT_PATH = _ORCHESTRATOR_ROOT_PATH + '/snapshots'
    _SYS_CONTROLLER_REQ_FILE_PATH = "SYS_CONTROLLER_REQ_FILE_PATH"
    _SYS_CONTROLLER_RES_FILE_PATH = "SYS_CONTROLLER_RES_FILE_PATH"
    _CONTROLLER_REQUEST_FILE_NAME_SUFFIX = "_dpp_controller_request.json"
    _CONTROLLER_RESPONSE_FILE_NAME_SUFFIX = "_dpp_controller_response.json"
    _SYS_ENV_VAR_DPP_STORAGE_ROOT_URI = "DPP_STORAGE_ROOT_URI"
    _SYS_ENV_VAR_DPP_STORAGE_SERVER_URL = "DPP_STORAGE_SERVER_URL"
    _SYS_ENV_VAR_DPP_STORAGE_ACCESS_KEY = "DPP_STORAGE_ACCESS_KEY"
    _SYS_ENV_VAR_DPP_STORAGE_SECRET_KEY = "DPP_STORAGE_SECRET_KEY"
    _FILE_NAME_DOCUMENT_DATA = "document_data.json"
    _FILE_NAME_CONTEXT_DATA = "context_data.json"
    _FILE_NAME_MESSAGE_DATA = "message_data.json"

# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

"""Module containing Constants class"""
import importlib.metadata


class Constants():
    """Constants class"""
    FSH_DPP = 'dpp'
    FSLH_DPP = 'dpp'
    try:
        DPP_VERSION = importlib.metadata.version('infy_dpp_sdk')
    except importlib.metadata.PackageNotFoundError:
        DPP_VERSION = "0.0.0"
    ORCHESTRATOR_ROOT_PATH = '/data/temp/work/dpp_orchestrator'
    ORCHESTRATOR_SNAPSHOT_PATH = ORCHESTRATOR_ROOT_PATH + '/snapshots'
    SYS_CONTROLLER_REQ_FILE_PATH = "SYS_CONTROLLER_REQ_FILE_PATH"
    SYS_CONTROLLER_RES_FILE_PATH = "SYS_CONTROLLER_RES_FILE_PATH"
    CONTROLLER_REQUEST_FILE_NAME_SUFFIX = "_dpp_controller_request.json"
    CONTROLLER_RESPONSE_FILE_NAME_SUFFIX = "_dpp_controller_response.json"
    SYS_ENV_VAR_DPP_STORAGE_ROOT_URI = "DPP_STORAGE_ROOT_URI"
    SYS_ENV_VAR_DPP_STORAGE_SERVER_URL = "DPP_STORAGE_SERVER_URL"
    SYS_ENV_VAR_DPP_STORAGE_ACCESS_KEY = "DPP_STORAGE_ACCESS_KEY"
    SYS_ENV_VAR_DPP_STORAGE_SECRET_KEY = "DPP_STORAGE_SECRET_KEY"
    FILE_NAME_DOCUMENT_DATA = "document_data.json"
    FILE_NAME_CONTEXT_DATA = "context_data.json"
    FILE_NAME_MESSAGE_DATA = "message_data.json"

# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import os
import json
from fastapi import HTTPException
from fastapi.responses import FileResponse
from pydantic import ValidationError
import infy_fs_utils
import infy_dpp_sdk
from schema.document_req_res_data import (DownloadDocumentRequestData)
from .b_controller import BController
from common.app_config_manager import AppConfigManager


class DocumentController(BController):
    """Handle documents"""

    __CONTROLLER_PATH = "/document"

    def __init__(self, context_root_path: str = ''):
        super().__init__(context_root_path=context_root_path,
                         controller_path=self.__CONTROLLER_PATH)

        self.get_router().add_api_route(
            "/download", self.download_document, methods=["POST"], summary="Download a document",
            tags=["document"])

    def download_document(self, file_name: DownloadDocumentRequestData):
        try:
            if not file_name.file_name:
                raise HTTPException(
                    status_code=400, detail="File name is required")
            if '.' not in file_name.file_name:
                raise HTTPException(
                    status_code=400, detail="Provide file name along with its extension")

            app_config = AppConfigManager().get_app_config()
            file_sys_handler = infy_fs_utils.manager.FileSystemManager(
            ).get_fs_handler(infy_dpp_sdk.common.Constants.FSH_DPP)
            config_file_path = app_config['STORAGE']["dpp_input_config_file_path"]
            input_config_data = json.loads(
                file_sys_handler.read_file(config_file_path))
            folder_path = input_config_data['variables']['RESOURCE_PATH']
            storage_root_path = app_config['STORAGE']['STORAGE_ROOT_PATH']

            file_path = os.path.join(
                storage_root_path, folder_path.lstrip('/'), file_name.file_name)
            file_path = os.path.normpath(file_path)

            if not os.path.exists(file_path):
                raise HTTPException(status_code=404, detail="File not found")

            file_name = os.path.basename(file_path)
            file_header = f'inline; filename="{file_name}"'
            return FileResponse(file_path, media_type='application/octet-stream', headers={'Content-Disposition': file_header})
        except ValidationError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail="File not found")

# ===============================================================================================================#
# Copyright 2025 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import os
import time
from typing import List
from datetime import datetime, timezone
from fastapi import File, UploadFile
from fastapi.responses import FileResponse
from schema.resource_res_data import ResourceResponseData, FetchResourceRequestData, ResourceResponseData
from schema.base_req_res_data import (ResponseCode, ResponseMessage)
from .b_controller import BController
from common.app_config_manager import AppConfigManager

class ResourceController(BController):
    """Resource Controller Class"""

    __CONTROLLER_PATH = "/resource"

    def __init__(self, context_root_path: str = ''):
        super().__init__(context_root_path=context_root_path,
                         controller_path=self.__CONTROLLER_PATH)
        self.get_router().add_api_route(
            "/upload_file", self.uploadFile, methods=["POST"], summary="Upload file to server",
            tags=["Resource"],
            response_model=ResourceResponseData)
        self.get_router().add_api_route(
            "/fetch_file", self.fetchFile, methods=["POST"], summary="Fetch file from server",
            tags=["Resource"],
            response_model=FetchResourceRequestData)

    async def uploadFile(self,  file: UploadFile = File(...)):
        app_config = AppConfigManager().get_app_config()
        
        start_time = time.time()
        date = datetime.now(timezone.utc)
        date_time_stamp = date.strftime("%Y-%m-%d %I:%M:%S %p")        
        
        resource_storage_path = app_config['STORAGE']['STORAGE_ROOT_PATH']
    
        file_name = file.filename if file.filename else ''
        file_location = os.path.join(resource_storage_path, file_name)

        if not file:
            response_data = None
            response_cde = ResponseCode.CLIENT_FAILURE
            response_msg = "Please provide Resource File."
        if os.path.exists(file_location):
            response_data = None
            response_cde = ResponseCode.CLIENT_FAILURE
            response_msg = f"File '{file_name}' already exists."
        else:
            try:
                with open(file_location, "wb") as buffer:
                    buffer.write(file.file.read())
            except Exception as e:
                response_data = None
                response_cde = ResponseCode.SERVER_FAILURE
                response_msg = f"{str(e)}"
            else:
                response_data = f"Resource:'{file_name}' successfully saved at resource location."
                response_cde = ResponseCode.SUCCESS
                response_msg = ResponseMessage.SUCCESS
                
            
        elapsed_time = round(time.time() - start_time, 3)
            
        response = ResourceResponseData(response=response_data,
                                            responseCde=response_cde,
                                            responseMsg=str(response_msg),timestamp=date_time_stamp,
                                            responseTimeInSecs=(elapsed_time))

        return response

    async def fetchFile(self, resource_request: FetchResourceRequestData):
        app_config = AppConfigManager().get_app_config()
        
        start_time = time.time()
        date = datetime.now(timezone.utc)
        date_time_stamp = date.strftime("%Y-%m-%d %I:%M:%S %p")   
        
        STORAGE_ROOT_PATH = app_config['STORAGE']['STORAGE_ROOT_PATH']
        
        input_data = resource_request.dict()
        resource_file_name = input_data.get('resource_file_name','')
        
        if not resource_file_name:
            response_data = None
            response_cde = ResponseCode.CLIENT_FAILURE
            response_msg = "Please provide Resource File Name."
        if '.' not in resource_file_name:    
            response_data = None
            response_cde = ResponseCode.CLIENT_FAILURE
            response_msg = "Please provide Resource File Name along with its extension."
        else:
            try:
                
                file_path = os.path.join(STORAGE_ROOT_PATH, resource_file_name)
                file_path = os.path.normpath(file_path)

                if os.path.exists(file_path):
                    file_name = os.path.basename(file_path)
                    file_header = f'inline; filename="{file_name}"'
                    return FileResponse(file_path, media_type='application/octet-stream', headers={'Content-Disposition': file_header})
                else:
                    response_data = None
                    response_cde = ResponseCode.CLIENT_FAILURE
                    response_msg = f"File '{resource_file_name}' not found."
            except Exception as e:
                response_data = None
                response_cde = ResponseCode.SERVER_FAILURE
                response_msg = f"{str(e)}"
                
        elapsed_time = round(time.time() - start_time, 3)
            
        response = ResourceResponseData(response=response_data,
                                            responseCde=response_cde,
                                            responseMsg=str(response_msg),timestamp=date_time_stamp,
                                            responseTimeInSecs=(elapsed_time))

        return response

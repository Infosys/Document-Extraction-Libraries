# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import os
import sys
import json
import uuid
from ray import serve
from common.app_config_manager import AppConfigManager
from starlette.requests import Request
from starlette.responses import JSONResponse
from service.yolox_td_service import YoloxTdService
from fastapi import FastAPI, File, UploadFile
from schema.yolox_data import YoloxTdRequestData, YoloxTdResponseData
app_fastapi = FastAPI()
app_config = AppConfigManager().get_app_config()


@serve.ingress(app_fastapi)
class YoloxTableDetectorBaseApp:
    def __init__(self):
        self.__model_name = app_config['MODEL_PATHS']['yolox_model_name']
        self.__model_path = app_config['MODEL_PATHS']['yolox_model_path']
        self.__yolox_td_service = YoloxTdService(model_name=self.__model_name,
                                                 model_home_path=self.__model_path)
        # Define the directory where files will be saved
        self.__UPLOAD_DIRECTORY = app_config['DEFAULT']['APP_DIR_TEMP_PATH']

    @app_fastapi.post("/detect")
    async def detect_table(self, file: UploadFile = File(...)) -> YoloxTdResponseData:
        file_data = await file.read()
        file_name = ''
        if hasattr(file, 'filename'):
            file_name = file.filename
        else:
            file_name = file.name

        unique_id = str(uuid.uuid4())
        temp_file_dir = f"{self.__UPLOAD_DIRECTORY}/yolox_{unique_id}"
        # Ensure the upload directory exists
        if not os.path.exists(temp_file_dir):
            os.makedirs(temp_file_dir)
        file_path = f"{temp_file_dir}/{os.path.basename(file_name)}"

        # Save the uploaded file to the local file path
        with open(file_path, "wb") as buffer:
            buffer.write(file_data)

        # Process the file
        response: YoloxTdResponseData = self.__yolox_td_service.detect_table_yolox(
            YoloxTdRequestData(**{"image_file_path": file_path}))

        os.remove(file_path)
        return response


if not 'pytest' in sys.modules:
    @serve.deployment()
    class YoloxTableDetectorApp(YoloxTableDetectorBaseApp):
        pass
    app = YoloxTableDetectorApp.bind()

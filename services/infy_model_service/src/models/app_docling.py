# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import sys
import os
import json
import uuid
from ray import serve
from common.app_config_manager import AppConfigManager
from io import BytesIO
from docling_core.types.io import DocumentStream
from service.docling_service import DoclingService
from schema.docling_document_data import DoclingDocumentData
from fastapi import FastAPI, File, UploadFile, Body
app_fastapi = FastAPI()

app_config = AppConfigManager().get_app_config()


@serve.ingress(app_fastapi)
class DoclingBaseApp:
    def __init__(self):
        self.__docling_service = DoclingService()

    @app_fastapi.post("/extract/")
    async def extract_from_file_obj(self, file: UploadFile = File(...)):
        file_data = await file.read()
        file_name = ''
        if hasattr(file, 'filename'):
            file_name = file.filename
        document_stream = DocumentStream(
            name=file_name, stream=BytesIO(file_data))
        response = self.__docling_service.convert_document(document_stream)
        result = DoclingDocumentData(
            document_data=response.get("document_data"),
            document_data_html=response.get("document_data_html"),
            table_data_html=response.get("table_data_html")
        )
        unique_id = str(uuid.uuid4())
        json_storage_folder_path = app_config['DEFAULT']['JSON_STORAGE_FOLDER_PATH']
        if not os.path.exists(json_storage_folder_path):
            os.makedirs(json_storage_folder_path)
        json_file_path = os.path.join(
            json_storage_folder_path, f"{unique_id}.json")
        with open(json_file_path, "w") as json_file:
            json.dump(result.dict(), json_file, indent=4)
        result = {
            "unique_id": unique_id,
            "document_data": response.get("document_data"),
        }
        return result

    @app_fastapi.post("/retrieve/")
    def retrieve_html_data(self, unique_id: str = Body(..., embed=True),
                           document_html: bool = Body(..., embed=True),
                           table_html: bool = Body(..., embed=True)) -> dict:
        json_storage_folder_path = app_config['DEFAULT']['JSON_STORAGE_FOLDER_PATH']
        json_file_path = os.path.join(
            json_storage_folder_path, f"{unique_id}.json")
        custom_result = {}
        with open(json_file_path, 'r') as json_file:
            response = json.load(json_file)
        # print(result.dict())
        if document_html:
            custom_result = {
                "document_data_html": response.get("document_data_html"),
            }
        elif table_html:
            custom_result = {
                "table_data_html": response.get("table_data_html"),
            }
        return custom_result


if not 'pytest' in sys.modules:
    @serve.deployment()
    class DoclingApp(DoclingBaseApp):
        pass
    app = DoclingApp.bind()

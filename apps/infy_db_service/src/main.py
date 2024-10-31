# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import infy_fs_utils
import infy_dpp_sdk
import infy_gen_ai_sdk
import uvicorn
import fastapi
from fastapi.middleware.cors import CORSMiddleware
from controller.vectordb_controller import VectordbController
from controller.sparsedb_controller import SparsedbController
from common.app_config_manager import AppConfigManager
from common.ainauto_logger_factory import AinautoLoggerFactory

CONTEXT_ROOT_PATH = "/api/v1"

app_config = AppConfigManager().get_app_config()
logger = AinautoLoggerFactory().get_logger()

STORAGE_ROOT_PATH = app_config['STORAGE']['STORAGE_ROOT_PATH']
CONTAINER_ROOT_PATH = app_config['CONTAINER']['CONTAINER_ROOT_PATH']
storage_config_data = infy_fs_utils.data.StorageConfigData(
    **{
        "storage_root_uri": f"file://{STORAGE_ROOT_PATH}",
        "storage_server_url": "",
        "storage_access_key": "",
        "storage_secret_key": ""
    })

if not infy_fs_utils.manager.FileSystemManager().has_fs_handler(infy_gen_ai_sdk.common.Constants.FSH_GEN_AI_SDK):
    infy_fs_utils.manager.FileSystemManager().add_fs_handler(
        infy_fs_utils.provider.FileSystemHandler(storage_config_data), infy_gen_ai_sdk.common.Constants.FSH_GEN_AI_SDK)
# Configure client properties
client_config_data = infy_dpp_sdk.ClientConfigData(
    **{
        "container_data": {
            "container_root_path": f"{CONTAINER_ROOT_PATH}",
        }
    })
infy_dpp_sdk.ClientConfigManager().load(client_config_data)

app = fastapi.FastAPI(title='Infosys DB Service',
                      #   dependencies=[Depends(basic_authorize)],
                      openapi_url=f"{CONTEXT_ROOT_PATH}/openapi.json",
                      docs_url=f"{CONTEXT_ROOT_PATH}/docs",
                      description="Infosys DB Service",
                      version=app_config['DEFAULT']['service_version'])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

"""VectorDB Controller"""
vectordb_controller_rest = VectordbController(
    context_root_path=CONTEXT_ROOT_PATH)
app.include_router(vectordb_controller_rest.get_router())

"""SparseDB Controller"""
sparsedb_controller_rest = SparsedbController(
    context_root_path=CONTEXT_ROOT_PATH)
app.include_router(sparsedb_controller_rest.get_router())

if __name__ == '__main__':
    logger.info("App is starting....")
    uvicorn.run("main:app", host="0.0.0.0", port=8005,
                log_level=10, reload=True)

# ===============================================================================================================#
# Copyright 2025 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import uvicorn
import fastapi
from fastapi.middleware.cors import CORSMiddleware
from controller.resource_controller import ResourceController
from common.app_config_manager import AppConfigManager

CONTEXT_ROOT_PATH = "/resourceservice/api/v1"

app_config = AppConfigManager().get_app_config()

STORAGE_ROOT_PATH = app_config['STORAGE']['STORAGE_ROOT_PATH']
CONTAINER_ROOT_PATH = app_config['CONTAINER']['CONTAINER_ROOT_PATH']

app = fastapi.FastAPI(title='Infosys Resource Service',
                      openapi_url=f"{CONTEXT_ROOT_PATH}/openapi.json",
                      docs_url=f"{CONTEXT_ROOT_PATH}/docs",
                      description="Infosys Resource Service",
                      version=app_config['DEFAULT']['service_version'])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

"""Resource Controller"""
resource_controller_rest = ResourceController(
    context_root_path=CONTEXT_ROOT_PATH)
app.include_router(resource_controller_rest.get_router())


if __name__ == '__main__':
    uvicorn.run("main:app", host="0.0.0.0", port=8006,
                log_level=10, reload=True)

# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import uvicorn
import fastapi
from fastapi.middleware.cors import CORSMiddleware
import infy_dpp_sdk

CONTEXT_PATH = "/api/v1/dpp"

app = fastapi.FastAPI(title='DPP service',
                      #   dependencies=[Depends(basic_authorize)],
                      openapi_url=f"{CONTEXT_PATH}/openapi.json", docs_url=f"{CONTEXT_PATH}/docs",
                      description="Infosys model service",
                      version='0.0.1')

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

controller_rest = infy_dpp_sdk.controller.ControllerHTTP(
    prefix=CONTEXT_PATH)
app.include_router(controller_rest.router)

if __name__ == '__main__':
    uvicorn.run("app_dpp_service:app", host="0.0.0.0", port=8901,
                log_level=10, reload=True)
    # logger.info("App is running....")

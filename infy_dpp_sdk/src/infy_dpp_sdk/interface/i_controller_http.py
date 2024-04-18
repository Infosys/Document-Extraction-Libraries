# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

from abc import ABC, abstractmethod
from typing import Union
from typing_extensions import Annotated
import fastapi
from ..data import (ControllerRequestData, ControllerResponseData)


class IControllerHTTP(ABC):
    """Interface for executing processor(s) when orchestrator makes HTTP API calls."""

    @abstractmethod
    def receive_and_respond(self, controller_request_data: ControllerRequestData,
                            request: fastapi.Request,
                            DPP_STORAGE_ROOT_URI: Annotated[Union[str, None],
                                                            fastapi.Header()] = None,
                            DPP_STORAGE_SERVER_URL: Annotated[Union[str, None],
                                                              fastapi.Header()] = None,
                            DPP_STORAGE_ACCESS_KEY: Annotated[Union[str, None],
                                                              fastapi.Header()] = None,
                            DPP_STORAGE_SECRET_KEY: Annotated[Union[str, None],
                                                              fastapi.Header()] = None,
                            ) -> ControllerResponseData:
        """Receive the request, do processing and send response"""
        raise NotImplementedError

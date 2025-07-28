# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#


from typing import Union
from typing_extensions import Annotated
try:
    import fastapi
except ImportError:
    # This is optional component only required for implementing HTTP controller
    # Create a pseudo class to avoid ImportError
    class fastapi():
        """Pseudo class"""
        class Request():
            """Pseudo class"""

        class Header():
            """Pseudo class"""

        def APIRouter(self, prefix):
            """Pseudo method"""
import infy_fs_utils
from ..data import (ControllerRequestData, ControllerResponseData)
from ..common import Constants
from ._internal.b_controller import BController
from ..interface import IControllerHTTP


class ControllerHTTP(IControllerHTTP):
    """Controller to receive request via HTTP"""

    def __init__(self, prefix: str = ''):
        super().__init__()
        self.router = fastapi.APIRouter(prefix=prefix)
        self.router.add_api_route(
            "/execute", self.receive_and_respond, methods=["POST"],
            response_model=ControllerResponseData)

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
                            ):
        """
        Receive request and respond via HTTP.

        Args:
            controller_request_data (ControllerRequestData): The controller request data.
            request (fastapi.Request): The FastAPI request object.
            DPP_STORAGE_ROOT_URI (str, optional): Storage root URI from header.
            DPP_STORAGE_SERVER_URL (str, optional): Storage server URL from header.
            DPP_STORAGE_ACCESS_KEY (str, optional): Storage access key from header.
            DPP_STORAGE_SECRET_KEY (str, optional): Storage secret key from header.

        Returns:
            ControllerResponseData: The controller response data.
        """
        print('Entering')
        controller_response_data = ControllerResponseData()
        print(controller_request_data)
        storage_config_data = infy_fs_utils.data.StorageConfigData(
            **{
                "storage_root_uri": DPP_STORAGE_ROOT_URI,
                "storage_server_url": DPP_STORAGE_SERVER_URL,
                "storage_access_key": DPP_STORAGE_ACCESS_KEY,
                "storage_secret_key": DPP_STORAGE_SECRET_KEY,
            })

        infy_fs_utils.manager.FileSystemManager().add_fs_handler(
            infy_fs_utils.provider.FileSystemHandler(storage_config_data),
            Constants.FSH_DPP)
        try:
            b_controller = BController()
            controller_response_data: ControllerResponseData = b_controller.do_execute_batch(
                controller_request_data)
        except Exception as e:
            print(e)
        finally:
            infy_fs_utils.manager.FileSystemManager().delete_fs_handler(
                Constants.FSH_DPP)
        return controller_response_data

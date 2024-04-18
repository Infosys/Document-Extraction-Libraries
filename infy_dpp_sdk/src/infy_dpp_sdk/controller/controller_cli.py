# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import argparse
import json
import os
import infy_fs_utils
from ..data import (ControllerRequestData, ControllerResponseData)
from ..common import Constants
from .b_controller import BController
from ..interface import IControllerCLI


class ControllerCLI(BController, IControllerCLI):
    """Controller to receive request via CLI"""

    __fs_handler: infy_fs_utils.interface.IFileSystemHandler = None
    __request_file_path = None

    def __init__(self):
        super().__init__()
        self.__fs_handler = infy_fs_utils.manager.FileSystemManager(
        ).get_fs_handler(Constants.FSH_DPP)

    def receive_request(self) -> ControllerRequestData:
        """Request is received as a CLI argument containing path of request file"""
        request_file_path = self.__get_request_file_path_from_cli()
        request_file_data = json.loads(self.__fs_handler.read_file(
            request_file_path))
        controller_request_data = ControllerRequestData(
            **request_file_data)
        self.__request_file_path = request_file_path
        return controller_request_data

    def send_response(self, controller_response_data: ControllerResponseData) -> any:
        """Response is sent as a console statement containing path of response file"""
        request_file_path = self.__request_file_path
        response_file_path = self.__generate_response_file_name(
            request_file_path)

        data_as_json_str = controller_response_data.json(indent=4)
        self.__fs_handler.write_file(
            response_file_path, data_as_json_str, encoding='utf-8')

        print('status=success')
        print("response_file_path=" + response_file_path)
        return response_file_path

    # --------- Private Methods -------------

    def __get_request_file_path_from_cli(self) -> str:
        parser = argparse.ArgumentParser()
        parser.add_argument("--request_file_path", default=None, required=True)
        args = parser.parse_args()
        request_file_path = args.request_file_path
        return request_file_path

    def __generate_response_file_name(self, request_file_path):
        dir_path, file_name = os.path.split(request_file_path)
        new_file_name = None
        SUFFIX_REQUEST = "request.json"
        SUFFIX_RESPONSE = "response.json"
        if file_name.lower().endswith(SUFFIX_REQUEST):
            temp = file_name.lower().split(
                SUFFIX_REQUEST)[0]
            new_file_name = file_name[:len(temp)] + SUFFIX_RESPONSE
        else:
            new_file_name = file_name + '_' + SUFFIX_RESPONSE
        return dir_path + '/' + new_file_name

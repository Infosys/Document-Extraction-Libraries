# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import json
from typing import List
import infy_fs_utils
from ..data import (ControllerRequestData,
                    ControllerResponseData, ProcessorResponseData)
from ..interface import IController
from ..common import Constants
from ..common.snapshot_util import SnapshotUtil


class BController(IController):
    """Base class for controller"""

    __fs_handler: infy_fs_utils.interface.IFileSystemHandler = None

    def __init__(self):
        super().__init__()
        self.__fs_handler = infy_fs_utils.manager.FileSystemManager(
        ).get_fs_handler(Constants.FSH_DPP)

    def do_execute_batch(self, controller_request_data: ControllerRequestData) -> ControllerResponseData:
        print("Executing BController...")
        return super().do_execute_batch(controller_request_data)

    def load_config_data(self, controller_request_data: ControllerRequestData) -> dict:
        input_config_file_path = controller_request_data.input_config_file_path
        input_config_data = self.__load_json(
            input_config_file_path)
        return input_config_data

    def load_snapshots(self, controller_request_data: ControllerRequestData):
        return SnapshotUtil().load_snapshots(controller_request_data)

    def save_snapshots(self, controller_request_data: ControllerRequestData,
                       processor_response_data_list: List[ProcessorResponseData]) \
            -> ControllerResponseData:
        return SnapshotUtil().save_snapshots(controller_request_data, processor_response_data_list)

    # --------- Private Methods -------------
    def __load_json(self, file_path) -> any:
        data = json.loads(self.__fs_handler.read_file(
            file_path))
        return data

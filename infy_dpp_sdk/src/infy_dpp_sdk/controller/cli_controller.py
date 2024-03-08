# ===============================================================================================================#
# Copyright 2022 Infosys Ltd.                                                                                   #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import argparse
import json
import os
from typing import List
import infy_fs_utils
from ..data import (DocumentData, ControllerRequestData, SnapshotData,
                    RecordData, ControllerResponseData, ProcessorResponseData)
from ..interface import IController
from ..common import Constants


class CliController(IController):
    """Processor App that can be invoked from command line"""

    __fs_handler: infy_fs_utils.interface.IFileSystemHandler = None
    __request_file_path = None

    def __init__(self):
        super().__init__()
        self.__fs_handler = infy_fs_utils.manager.FileSystemManager(
        ).get_fs_handler(Constants.FSH_DPP)

    def do_execute_batch(self, controller_request_data: ControllerRequestData) -> ControllerResponseData:
        print("Executing CLI Controller...")
        return super().do_execute_batch(controller_request_data)

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

    def load_config_data(self, controller_request_data: ControllerRequestData) -> dict:
        input_config_file_path = controller_request_data.input_config_file_path
        input_config_data = self.__load_json(
            input_config_file_path)
        return input_config_data

    def load_snapshots(self, controller_request_data: ControllerRequestData):
        snapshot_dir_root_path = controller_request_data.snapshot_dir_root_path
        document_data_list: List[DocumentData] = []
        context_data_list: List[dict] = []
        if controller_request_data.records:
            for record in controller_request_data.records:
                record: RecordData = record
                if record.snapshot.document_data_file_path:
                    document_data: DocumentData = DocumentData(**self.__load_json(
                        snapshot_dir_root_path + "/" + record.snapshot.document_data_file_path))
                    document_data_list.append(document_data)
                    context_data: dict = self.__load_json(
                        snapshot_dir_root_path + "/" + record.snapshot.context_data_file_path)
                    context_data_list.append(context_data)
        if not document_data_list and controller_request_data.context:
            # This should run only first time when there are no records and context is present
            context_data_list.append(controller_request_data.context)

        return document_data_list, context_data_list

    def save_snapshots(self, controller_request_data: ControllerRequestData,
                       processor_response_data_list: List[ProcessorResponseData]) \
            -> ControllerResponseData:
        snapshot_dir_root_path = controller_request_data.snapshot_dir_root_path
        self.__fs_handler.create_folders(snapshot_dir_root_path)
        incoming_request_records: List[RecordData] = controller_request_data.records or [
        ]
        new_records: List[RecordData] = []
        # Copy all data from incoming app request to app response object
        controller_response_data: ControllerResponseData = controller_request_data.copy()
        for processor_response_data in processor_response_data_list:

            document_data: DocumentData = processor_response_data.document_data
            context_data: dict = processor_response_data.context_data
            request_id = controller_request_data.request_id
            document_id = document_data.document_id
            # Generate file names based on request id and document id combination
            document_data_file_path = f"{request_id}_{document_id}.document_data.json"
            context_data_file_path = f"{request_id}_{document_id}.context_data.json"

            incoming_record = [
                x for x in incoming_request_records if x.document_id == document_id]
            if len(incoming_record) > 1:
                message = f"Duplicate records found for document_id: {document_id}"
                raise ValueError(message)
            if len(incoming_record) == 1:
                record: RecordData = incoming_record[0]
                record.snapshot.document_data_file_path = document_data_file_path
                record.snapshot.context_data_file_path = context_data_file_path
            else:
                record = RecordData(document_id=document_id)
                record.snapshot = SnapshotData(document_data_file_path=document_data_file_path,
                                               context_data_file_path=context_data_file_path)
                new_records.append(record)

            data_as_json_str = document_data.json(indent=4)
            self.__fs_handler.write_file(
                snapshot_dir_root_path + "/" + document_data_file_path, data_as_json_str, encoding='utf-8')
            data_as_json_str = json.dumps(context_data, indent=4)
            self.__fs_handler.write_file(
                snapshot_dir_root_path + "/" + context_data_file_path, data_as_json_str, encoding='utf-8')

        if not controller_response_data.records:
            controller_response_data.records = []
        controller_response_data.records.extend(new_records)
        return controller_response_data

    # --------- Private Methods -------------

    def __get_request_file_path_from_cli(self) -> str:
        parser = argparse.ArgumentParser()
        parser.add_argument("--request_file_path", default=None, required=True)
        args = parser.parse_args()
        request_file_path = args.request_file_path
        return request_file_path

    def __load_json(self, file_path) -> any:
        data = json.loads(self.__fs_handler.read_file(
            file_path))
        return data

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

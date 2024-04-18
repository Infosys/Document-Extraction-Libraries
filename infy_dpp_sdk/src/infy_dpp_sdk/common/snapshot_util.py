# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import json
from typing import List
import infy_fs_utils
from ..data import (DocumentData, ControllerRequestData, SnapshotData,
                    RecordData, ControllerResponseData, ProcessorResponseData,
                    MessageData)
from ..common import Constants


class SnapshotUtil():
    """Util class for snapshot operations"""

    __fs_handler: infy_fs_utils.interface.IFileSystemHandler = None

    def __init__(self):
        self.__fs_handler = infy_fs_utils.manager.FileSystemManager(
        ).get_fs_handler(Constants.FSH_DPP)

    def create_processor_response_data_list(self,
                                            controller_response_data: ControllerResponseData
                                            ) -> List[ProcessorResponseData]:
        """Create ProcessorResponseData list from ControllerResponseData"""
        processor_response_data_list: List[ProcessorResponseData] = []
        document_data_list, context_data_list, message_data_list = self.load_snapshots(
            controller_response_data)

        for document_data, context_data, message_data in zip(document_data_list,
                                                             context_data_list, message_data_list):
            processor_response_data = ProcessorResponseData(
                document_data=document_data, context_data=context_data,
                message_data=message_data)
            processor_response_data_list.append(processor_response_data)
        return processor_response_data_list

    def load_snapshots(self, controller_request_data: ControllerRequestData):
        """Load snapshot(s) to memory"""
        snapshot_dir_root_path = controller_request_data.snapshot_dir_root_path
        document_data_list: List[DocumentData] = []
        context_data_list: List[dict] = []
        message_data_list: List[MessageData] = []
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
                    message_data = None
                    if record.snapshot.message_data_file_path:
                        message_data: MessageData = MessageData(**self.__load_json(
                            snapshot_dir_root_path + "/" + record.snapshot.message_data_file_path))
                    message_data_list.append(message_data)
        if not document_data_list and controller_request_data.context:
            # This should run only first time when there are no records and context is present
            context_data_list.append(controller_request_data.context)

        return document_data_list, context_data_list, message_data_list

    def save_snapshots(self, controller_request_data: ControllerRequestData,
                       processor_response_data_list: List[ProcessorResponseData]) \
            -> ControllerResponseData:
        """Save snapshot(s) to storage"""
        snapshot_dir_root_path = controller_request_data.snapshot_dir_root_path
        self.__fs_handler.create_folders(snapshot_dir_root_path)
        incoming_request_records: List[RecordData] = controller_request_data.records or [
        ]
        new_records: List[RecordData] = []
        # Copy all data from incoming app request to app response object
        controller_response_data: ControllerResponseData = controller_request_data.copy()
        controller_response_data.dpp_version = Constants.DPP_VERSION
        for processor_response_data in processor_response_data_list:

            document_data: DocumentData = processor_response_data.document_data
            context_data: dict = processor_response_data.context_data
            message_data: MessageData = processor_response_data.message_data
            request_id = controller_request_data.request_id
            document_id = document_data.document_id
            # Generate file names based on request id and document id combination
            document_data_file_path = f"{request_id}_{document_id}.document_data.json"
            context_data_file_path = f"{request_id}_{document_id}.context_data.json"
            message_data_file_path = None
            if message_data:
                message_data_file_path = f"{request_id}_{document_id}.message_data.json"

            incoming_record = [
                x for x in incoming_request_records if x.document_id == document_id]
            if len(incoming_record) > 1:
                message = f"Duplicate records found for document_id: {document_id}"
                raise ValueError(message)
            if len(incoming_record) == 1:
                record: RecordData = incoming_record[0]
                record.snapshot.document_data_file_path = document_data_file_path
                record.snapshot.context_data_file_path = context_data_file_path
                record.snapshot.message_data_file_path = message_data_file_path
            else:
                record = RecordData(document_id=document_id)
                record.snapshot = SnapshotData(document_data_file_path=document_data_file_path,
                                               context_data_file_path=context_data_file_path,
                                               message_data_file_path=message_data_file_path)
                new_records.append(record)

            data_as_json_str = document_data.json(indent=4)
            self.__fs_handler.write_file(
                snapshot_dir_root_path + "/" + document_data_file_path, data_as_json_str, encoding='utf-8')
            data_as_json_str = json.dumps(context_data, indent=4)
            self.__fs_handler.write_file(
                snapshot_dir_root_path + "/" + context_data_file_path, data_as_json_str, encoding='utf-8')
            if message_data:
                data_as_json_str = message_data.json(indent=4)
                self.__fs_handler.write_file(
                    snapshot_dir_root_path + "/" + message_data_file_path, data_as_json_str, encoding='utf-8')

        if not controller_response_data.records:
            controller_response_data.records = []
        controller_response_data.records.extend(new_records)
        return controller_response_data

    # --------- Private Methods -------------
    def __load_json(self, file_path) -> any:
        data = json.loads(self.__fs_handler.read_file(
            file_path))
        return data

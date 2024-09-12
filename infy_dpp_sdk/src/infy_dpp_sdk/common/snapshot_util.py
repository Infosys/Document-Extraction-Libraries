# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import json
import logging
from typing import List
import infy_fs_utils
from .singleton import Singleton
from ..data import (DocumentData, ControllerRequestData, SnapshotData,
                    RecordData, ControllerResponseData, ProcessorResponseData,
                    MessageData)
from ..common.dpp_json_encoder import DppJSONEncoder
from ..common import Constants


class SnapshotUtil(metaclass=Singleton):
    """Util class for snapshot operations"""

    __fs_handler: infy_fs_utils.interface.IFileSystemHandler = None

    def __init__(self):
        self.__fs_handler = infy_fs_utils.manager.FileSystemManager(
        ).get_fs_handler(Constants.FSH_DPP)
        if infy_fs_utils.manager.FileSystemLoggingManager().has_fs_logging_handler(Constants.FSLH_DPP):
            self.__logger = infy_fs_utils.manager.FileSystemLoggingManager(
            ).get_fs_logging_handler(Constants.FSLH_DPP).get_logger()
        else:
            self.__logger = logging.getLogger(__name__)

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
            document_data_file_path = f"{request_id}_{document_id}.{Constants.FILE_NAME_DOCUMENT_DATA}"
            context_data_file_path = f"{request_id}_{document_id}.{Constants.FILE_NAME_CONTEXT_DATA}"
            message_data_file_path = None
            if message_data:
                message_data_file_path = f"{request_id}_{document_id}.{Constants.FILE_NAME_MESSAGE_DATA}"

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

    def read_controller_response_data(self, controller_res_file_path) -> ControllerResponseData:
        """Read ControllerResponseData from file"""
        controller_response_data: ControllerResponseData = None
        if controller_res_file_path:
            # TODO M: Handle multiple controller response files
            if isinstance(controller_res_file_path, list):
                controller_res_file_path = controller_res_file_path[0]
            data = json.loads(self.__fs_handler.read_file(
                controller_res_file_path))
            controller_response_data = ControllerResponseData(**data)
        return controller_response_data

    def save_controller_response_data(self, controller_response_data: ControllerResponseData):
        """Create ControllerResponseData file"""
        temp_folder_path = Constants.ORCHESTRATOR_ROOT_PATH
        request_id = controller_response_data.request_id
        self.__fs_handler.create_folders(temp_folder_path)
        json_file_path = f"{temp_folder_path}/{request_id}{Constants.CONTROLLER_RESPONSE_FILE_NAME_SUFFIX}"
        self.__logger.info("Processor input config file path - %s",
                           json_file_path)
        # Due to TypeError: Object of type ProcessorFilterData is not JSON serializable
        controller_response_data = json.loads(
            DppJSONEncoder().encode(controller_response_data))
        data_as_json_str = json.dumps(controller_response_data, indent=4)
        self.__fs_handler.write_file(
            json_file_path, data_as_json_str, encoding='utf-8')
        # rel_path = json_file_path.replace(data_root_path, "")
        # return rel_path
        return json_file_path

    def consolidate_controller_response_data(self, controller_res_file_path_list: list) \
            -> ControllerResponseData:
        """Consolidate ProcessorResponseData list"""
        document_id_list = []
        processor_filter_list = []
        merged_controller_response_data: ControllerResponseData = None
        document_snapshot_map = {}
        context_snapshot_map = {}
        message_snapshot_map = {}
        # Loop through all controller response files
        for idx, controller_res_file_path in enumerate(sorted(controller_res_file_path_list)):
            controller_resp_data = self.read_controller_response_data(
                controller_res_file_path)
            if idx == 0:
                merged_controller_response_data = controller_resp_data
                merged_controller_response_data.description = "Auto-consolidated by DPP orchestrator"
                merged_controller_response_data.request_id = merged_controller_response_data.request_id.split(".")[
                    0]
            processor_filter_list.extend(
                controller_resp_data.processor_filter.includes)
            document_data_list, context_data_list, message_data_list = self.load_snapshots(
                controller_resp_data)
            # Loop through all records in controller response file
            for document_data, context_data, message_data in zip(document_data_list,
                                                                 context_data_list, message_data_list):
                document_id = document_data.document_id
                if not document_id in document_snapshot_map:
                    document_id_list.append(document_id)
                    document_snapshot_map[document_id] = []
                    context_snapshot_map[document_id] = []
                    message_snapshot_map[document_id] = []

                document_snapshot_map[document_id].append(document_data)
                context_snapshot_map[document_id].append(context_data)
                message_snapshot_map[document_id].append(message_data)

        # Now we've snapshots for each document_id fetched from all the controller response files
        for document_id, snapshots in document_snapshot_map.items():
            document_data = self.__merge_objects(*snapshots)
            document_snapshot_map[document_id] = document_data

        for document_id, snapshots in context_snapshot_map.items():
            context_data = self.__merge_objects(*snapshots)
            context_snapshot_map[document_id] = context_data

        for document_id, snapshots in message_snapshot_map.items():
            message_data = self.__merge_objects(*snapshots)
            message_snapshot_map[document_id] = message_data

        # We can now create a new controller response data object
        processor_response_data_list: List[ProcessorResponseData] = []
        for document_id in document_id_list:
            processor_response_data = ProcessorResponseData(
                document_data=document_snapshot_map.get(document_id),
                context_data=context_snapshot_map.get(document_id),
                message_data=message_snapshot_map.get(document_id))
            processor_response_data_list.append(processor_response_data)

        merged_controller_response_data.processor_filter.includes = processor_filter_list
        merged_controller_response_data = self.save_snapshots(
            merged_controller_response_data,
            processor_response_data_list)

        return merged_controller_response_data, processor_response_data_list

    # --------- Private Methods -------------
    def __load_json(self, file_path) -> any:
        data = json.loads(self.__fs_handler.read_file(
            file_path))
        return data

    def __merge_objects(self, *objs: any):
        """Merge objects"""
        merged_obj = None
        if not objs:
            return merged_obj
        if isinstance(objs[0], dict):
            dicts = objs
        else:
            dicts = [obj.dict() for obj in objs if obj]
        merged_dict = {}
        if dicts:
            for d in dicts:
                merged_dict.update(d)
        if merged_dict:
            if isinstance(objs[0], DocumentData):
                merged_obj = DocumentData(**merged_dict)
            elif isinstance(objs[0], MessageData):
                merged_obj = MessageData(**merged_dict)
            else:
                merged_obj = merged_dict

        return merged_obj

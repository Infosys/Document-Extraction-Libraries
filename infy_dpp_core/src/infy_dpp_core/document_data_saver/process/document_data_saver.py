# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                   #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#
import infy_dpp_sdk
from infy_dpp_sdk.data.document_data import DocumentData
from infy_dpp_sdk.data.processor_response_data import ProcessorResponseData


class DocumentDataSaver(infy_dpp_sdk.interface.IProcessor):

    def __init__(self) -> None:
        self.__file_sys_handler = self.get_fs_handler()

    def do_execute(self, document_data: DocumentData, context_data: dict, config_data: dict) -> ProcessorResponseData:
        logger = self.get_logger()
        response_data = infy_dpp_sdk.data.ProcessorResponseData(
            document_data=document_data, context_data=context_data)
        if not document_data.document_id:
            return response_data
        processor_input_config = config_data.get('DocumentDataSaver', {})
        work_root_path = processor_input_config.get('work_root_path')
        filename = getattr(getattr(
            getattr(document_data, 'metadata', {}), 'standard_data', {}), 'filename', None)
        if filename:
            filename = document_data.metadata.standard_data.filename.value
            doc_work_location = f"{work_root_path}/D-{document_data.document_id}/{filename}_files"
        else:
            doc_work_location = f"{work_root_path}/D-{document_data.document_id}"
            self.__file_sys_handler.create_folders(doc_work_location)
        file_path = f"{doc_work_location}/processor_response_data.json"
        self.__file_sys_handler.write_file(
            file_path, response_data.json(indent=4))
        logger.debug(f"Wrote to file {file_path}")
        return response_data

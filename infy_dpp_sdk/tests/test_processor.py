# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import os
from typing import List
import infy_dpp_sdk
from .use_cases.uc_01.processors.document_downloader import DocumentDownloaderV1
from .use_cases.uc_01.processors.content_extractor import ContentExtractorV1
from .use_cases.uc_01.processors.attribute_extractor import AttributeExtractorV1
from .use_cases.uc_01.processors.document_uploader import DocumentUploaderV1

DATA_FOLDER_PATH = os.path.abspath('./data')


def test_single_processor():
    """Test method"""
    CONFIG_DATA = {
        "DocumentDownloader": {
            "readPath": f"{DATA_FOLDER_PATH}/input",
            "filter": {
                "include": [
                    "*.txt",
                    "*.jpg"
                ],
                "exclude": []
            },
            "writePath": f"{DATA_FOLDER_PATH}/work",
        }
    }
    processor_obj = DocumentDownloaderV1()
    processor_response_data_list = processor_obj.do_execute_batch(
        None, None, CONFIG_DATA)
    # Validate the response from first processor
    for processor_response_data in processor_response_data_list:
        document_data = processor_response_data.document_data
        assert document_data.document_id is not None
        orig_file_path = document_data.metadata.standard_data.filepath.value
        assert os.path.exists(orig_file_path)
        context_data = processor_response_data.context_data
        work_file_path = context_data.get(
            'DocumentDownloader', {}).get('work_file_path', None)
        assert os.path.exists(work_file_path)


def test_multiple_processors():
    """Test method"""
    CONFIG_DATA = {
        "DocumentDownloader": {
            "readPath": f"{DATA_FOLDER_PATH}/input",
            "filter": {
                "include": [
                    "*.txt",
                    "*.jpg"
                ],
                "exclude": []
            },
            "writePath": f"{DATA_FOLDER_PATH}/work",
        },
        "ContentExtractor": {
        },
        "AttributeExtractor": {
            "required_tokens": [
                {
                    "name": "Company Name",
                    "position": 5
                },
                {
                    "name": "Country",
                    "position": 9
                }
            ]
        },
        "DocumentUploader": {
            "writePath": f"{DATA_FOLDER_PATH}/output",
        }
    }

    # When dealing with multiple processors, always do it in a loop which is synonymous to pipeline
    my_processor_list = [DocumentDownloaderV1(), ContentExtractorV1(),
                         AttributeExtractorV1(), DocumentUploaderV1()]

    document_data_list, context_data_list = None, None
    processor_response_data_list: List[infy_dpp_sdk.data.ProcessorResponseData] = None
    for processor_obj in my_processor_list:
        # Typecast to IProcessor
        processor_obj: infy_dpp_sdk.interface.IProcessor = processor_obj
        processor_response_data_list = processor_obj.do_execute_batch(
            document_data_list, context_data_list, CONFIG_DATA)
        document_data_list = [
            x.document_data for x in processor_response_data_list]
        context_data_list = [
            x.context_data for x in processor_response_data_list]

    # Validate the response after final processor execution
    for processor_response_data in processor_response_data_list:
        # Assert document data expected values
        document_data = processor_response_data.document_data
        assert document_data.document_id is not None
        orig_file_path = document_data.metadata.standard_data.filepath.value
        assert os.path.exists(orig_file_path)

        # Assert context data expected values
        context_data = processor_response_data.context_data
        work_file_path = context_data.get(
            'DocumentDownloader', {}).get('work_file_path', None)
        assert os.path.exists(work_file_path)
        save_file_path = context_data.get(
            'DocumentUploader', {}).get('save_file_path', None)
        assert os.path.exists(save_file_path)

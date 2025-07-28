# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import sys
import os
import pickle
import hashlib
from common.app_config_manager import AppConfigManager
from common.singleton import Singleton
from docling.document_converter import DocumentConverter
from docling_core.types.io import DocumentStream
from docling.datamodel.pipeline_options import PdfPipelineOptions, EasyOcrOptions
from docling.datamodel.base_models import InputFormat
from docling.document_converter import DocumentConverter, PdfFormatOption, \
    ImageFormatOption, ExcelFormatOption, WordFormatOption, PowerpointFormatOption, \
    MarkdownFormatOption, AsciiDocFormatOption, HTMLFormatOption

app_config = AppConfigManager().get_app_config()


class DoclingService(metaclass=Singleton):
    def __init__(self):
        pipeline_options = PdfPipelineOptions(
            artifacts_path=app_config['MODEL_PATHS']['docling_model_artifacts_path'],
            ocr_options=EasyOcrOptions(
                model_storage_directory=app_config['MODEL_PATHS']['easyOCR_model_path'],
                download_enabled=False
            )
        )
        self.document_converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(
                    pipeline_options=pipeline_options),
                InputFormat.IMAGE: ImageFormatOption(
                    pipeline_options=pipeline_options),
                InputFormat.DOCX: WordFormatOption(
                    pipeline_options=pipeline_options),
                InputFormat.PPTX: PowerpointFormatOption(
                    pipeline_options=pipeline_options),
                InputFormat.XLSX: ExcelFormatOption(
                    pipeline_options=pipeline_options),
                InputFormat.HTML: HTMLFormatOption(
                    pipeline_options=pipeline_options),
                InputFormat.ASCIIDOC: AsciiDocFormatOption(
                    pipeline_options=pipeline_options),
                InputFormat.MD: MarkdownFormatOption(
                    pipeline_options=pipeline_options),
            }
        )

    def convert_document(self, document_stream: DocumentStream) -> dict:
        result = self.__access_cache(document_stream, is_read=True)
        if result:
            return result
        result = self.document_converter.convert(document_stream)
        document_data = result.document.export_to_dict()
        document_data_html = result.document.export_to_html()
        table_data_html = []
        for table in result.document.tables:
            table_data_html.append(
                {"table_ref": table.self_ref, "table_data_html": table.export_to_html()})
        response = {
            "document_data": document_data,
            "document_data_html": document_data_html,
            "table_data_html": table_data_html
        }
        self.__access_cache(document_stream, is_read=False, data=response)
        return response

    def __access_cache(self, document_stream: DocumentStream, is_read: bool, data=None):
        result = None
        if 'pytest' in sys.modules and os.environ.get('USE_DOCLING_CACHE', 'False'):
            hash_value = self.__get_stream_hash(document_stream)
            cache_file_path = app_config['DEFAULT']['APP_DIR_TEMP_PATH'] + \
                f"/{hash_value}.pkl"
            if is_read:  # Read mode
                if os.path.exists(cache_file_path):
                    with open(cache_file_path, "rb") as file:
                        result = pickle.load(file)
            else:  # Write mode
                if not os.path.exists(app_config['DEFAULT']['APP_DIR_TEMP_PATH']):
                    os.makedirs(app_config['DEFAULT']['APP_DIR_TEMP_PATH'])
                with open(cache_file_path, "wb") as file:
                    pickle.dump(data, file)

        return result

    def __get_stream_hash(self, document_stream: DocumentStream, hash_algorithm='sha256'):
        hash_func = hashlib.new(hash_algorithm)
        document_stream.stream.seek(0)  # Ensure the stream is at the beginning
        while chunk := document_stream.stream.read(8192):
            hash_func.update(chunk)
        # Reset the stream position to the beginning
        document_stream.stream.seek(0)
        return hash_func.hexdigest()

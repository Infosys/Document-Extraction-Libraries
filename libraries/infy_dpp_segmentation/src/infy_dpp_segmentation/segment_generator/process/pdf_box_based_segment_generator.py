# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

"""This python file is for native pdfs."""
import os
import json
from infy_ocr_generator import ocr_generator
from infy_ocr_generator.providers.apache_pdfbox_data_service_provider \
    import ApachePdfboxDataServiceProvider

from infy_dpp_segmentation.common.file_util import FileUtil
from infy_dpp_segmentation.segment_generator.service.image_generator_service import ImageGeneratorService
import infy_fs_utils
import infy_dpp_sdk

ENCODING_LIST = ['utf-8', 'ascii', 'ansi']


class PdfBoxBasedSegmentGenerator:
    '''for native pdfs'''

    def __init__(self, text_provider_dict, file_sys_handler, logger, app_config) -> None:
        self.__logger = logger
        self.__app_config = app_config
        self.__file_sys_handler = file_sys_handler

        self.__converter_path = text_provider_dict.get(
            'properties').get('format_converter_home', '')
        if self.__converter_path == '':
            raise Exception(
                'Format converter path is not configured in the config file')
        self.__extract_hyperlink = text_provider_dict.get(
            'properties').get('extract_hyperlink', False)
        self._org_pdf_file_path = None

    # def get_segment_data(self, from_files_full_path, out_file_full_path):
    def get_segment_data(self, from_files_full_path, out_file_full_path, ocr_files_path_list):
        '''getting segment data from pdf file'''
        self._org_pdf_file_path = from_files_full_path
        segment_data_list = self.get_segment_data_from_ocr(
            ocr_files_path_list)
        return segment_data_list

    def get_segment_data_from_ocr(self, ocr_file_path_list):
        '''getting segment data from ocr files'''
        segment_data_list = []
        for ocr_file_path in ocr_file_path_list:
            page_raw_segment_data = json.loads(self.__file_sys_handler.read_file(
                ocr_file_path))
            valid_token_list = [x['text']
                                for x in page_raw_segment_data['tokens'] if x['text'] != ' ']
            total_token_list = [x['text']
                                for x in page_raw_segment_data['tokens']]
            if len(valid_token_list) == 0 and len(total_token_list) in (0, 1):
                segment_data = {}
                segment_data["content_type"] = "line"
                segment_data["content"] = "[NO DATA FOUND]"
                segment_data["bbox_format"] = "X1,Y1,X2,Y2"
                segment_data["content_bbox"] = [
                    0, 0, page_raw_segment_data['width'], page_raw_segment_data['height']]
                segment_data["confidence_pct"] = -1
                segment_data["page"] = page_raw_segment_data["page"]
                segment_data["sequence"] = -1
                segment_data_list.append(segment_data)
            else:
                # for data in page_raw_segment_data:
                for token in page_raw_segment_data["tokens"]:
                    if token["text"] != ' ':
                        segment_data = {}
                        segment_data["content_type"] = "line"
                        if self.__extract_hyperlink:
                            segment_data["content"] = token["text"] if token.get(
                                "textHtml") is None else token["textHtml"]
                        else:
                            segment_data["content"] = token["text"]
                        segment_data["bbox_format"] = "X1,Y1,X2,Y2"
                        segment_data["content_bbox"] = token["bbox"]
                        segment_data["confidence_pct"] = -1
                        segment_data["page"] = page_raw_segment_data["page"]
                        segment_data["sequence"] = -1
                        segment_data_list.append(segment_data)
        return segment_data_list

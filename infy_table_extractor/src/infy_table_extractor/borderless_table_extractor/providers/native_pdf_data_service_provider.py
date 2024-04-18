# ===============================================================================================================#
# Copyright 2020 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import os

import cv2
import infy_common_utils.format_converter as format_converter
from infy_table_extractor.borderless_table_extractor.interface.data_service_provider_interface import \
    DataServiceProviderInterface


class NativePdfDataServiceProvider(DataServiceProviderInterface):
    """Data Service Provider to extract from NativePdf document."""

    def __init__(self, logger=None, log_level=None):
        super(NativePdfDataServiceProvider, self).__init__(logger, log_level)
        format_converter.format_converter_jar_home = os.environ['FORMAT_CONVERTER_HOME']
        self.logger.info("Initialized successfully")

    def get_enhanced_tokens(self, token_data_list: list,
                            image_file_path: str = None,
                            within_bbox: list = None,
                            file_data_list: list = None,) -> list:
        """Used FormatConverter(wrapper to `java pdfbox` tool) to extract text based on token's bbox
        and then enhanced it."""
        im_h, im_w = cv2.imread(image_file_path).shape[:2]
        pdf_file_list = None
        if file_data_list:
            pdf_file_list = [pdf_file_data for pdf_file_data in file_data_list if pdf_file_data["path"] and str(
                pdf_file_data["path"]).lower().endswith(".pdf")]
        if not pdf_file_list:
            raise FileNotFoundError("PDF file not found in 'file_data_list'")
        page_bboxes = []
        for item in token_data_list:
            startx, starty, endx, endy = item['bbox']
            startx = startx-20
            width = endx - startx
            height = endy - starty
            page_bboxes.append([startx, starty, width, height])

        config_param_dict = {
            "pages": pdf_file_list[0]['pages'],
            "bboxes": page_bboxes,
            "page_dimension": {"width": im_w, "height": im_h}
        }
        # PDF_TO_JSON
        extracted_fields, std_err = format_converter.FormatConverter.execute(
            pdf_file_list[0]["path"],
            convert_action=format_converter.ConvertAction.PDF_TO_JSON,
            config_param_dict=config_param_dict
        )

        if not std_err and extracted_fields:
            for region_data in extracted_fields[0]['regions']:
                new_value = region_data['text']
                if new_value != "":
                    startx, starty, width, height = region_data['bbox']
                    startx = startx+20
                    endx = width + startx
                    endy = height + starty
                    for item in token_data_list:
                        if item['bbox'] == [startx, starty, endx, endy]:
                            item['text'] = new_value
                            break
        return token_data_list

    def get_tokens(self, image_file_path: str,
                   token_type_value: int,
                   file_data_list: list = None,
                   additional_info: dict = None,
                   config_params_dict: dict = None) -> list:
        raise NotImplementedError

    def get_rows_cols(self, image_file_path: str,
                      token_type_value: int,
                      file_data_list: list = None,
                      additional_info: dict = None,
                      config_params_dict: dict = None) -> dict:
        raise NotImplementedError

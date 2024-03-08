# ===============================================================================================================#
# Copyright 2020 Infosys Ltd.                                                                                   #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import glob
import logging
import shutil
from os import path

import cv2
import infy_table_extractor as ite
import pandas as pd

import traceback

from infy_table_extractor.borderless_table_extractor.interface.data_service_provider_interface import \
    DataServiceProviderInterface
from infy_table_extractor.borderless_table_extractor.internal import (hocr_to_csv,
                                                                      image_ocr_content_extractor,
                                                                      internal_converter)
from infy_table_extractor.borderless_table_extractor.internal.extractor_util import ExtractorUtil
from infy_table_extractor.borderless_table_extractor.internal.image_parser_util import \
    ImageParserUtil
from infy_table_extractor.borderless_table_extractor.internal.statistic_util import StatisticUtil

CONFIG_PARAM_DICT = {
    'custom_cells': [{'rows': ['0:'], 'columns': ['0:']}],
    'col_header': {'use_first_row': True}
}


class BorderlessTableExtractor(ite.interface.ITableExtractor):
    """Class to Extract image table to html table"""

    def __init__(self, temp_file_dir: str,
                 token_rows_cols_provider: DataServiceProviderInterface,
                 token_detection_provider: DataServiceProviderInterface,
                 token_enhance_provider: DataServiceProviderInterface = None,
                 pytesseract_path: str = None,
                 logger: logging.Logger = None,
                 debug_mode_check: bool = False):
        """Creates an instance of Extractor class.

        Args:
            temp_file_dir (str): Path to temp folder
            token_rows_cols_provider (DataServiceProviderInterface):
                -Provider for finding the rows and cols from token.
            token_detection_provider (DataServiceProviderInterface):
                -Provider for finding tokens.
            token_enhance_provider (DataServiceProviderInterface, optional):
                -Provider for enhancing the tokens.
            pytesseract_path (str, optional): Pytesseract path. Defaults to None.
            logger (logging.Logger, optional): logger object. Defaults to None.
            debug_mode_check (bool, optional): debug mode enable flag. Defaults to False.
        """
        self.logger = logger
        self.temp_file_dir = temp_file_dir
        self.debug_mode_check = debug_mode_check
        self.token_rows_cols_provider = token_rows_cols_provider
        self.token_detection_provider = token_detection_provider
        self.token_enhance_provider = token_enhance_provider
        if logger is None:
            logging.basicConfig(
                level=logging.INFO, format='%(asctime)s.%(msecs)03d %(levelname)s'
                ' ainauto-tabula - %(module)s - %(funcName)s: %(message)s')
            logger = logging.getLogger()
            self.logger = logger
            logger.info('log initialized')
        self.__img_extractor_obj = image_ocr_content_extractor.ImageOCRContentExtractor(
            pytesseract_path, self.temp_file_dir, self.logger, debug_mode_check)

    def set_token_enchance_provider(self, token_enhance_provider: DataServiceProviderInterface):
        """Setter method to switch `token_enhance_provider` at runtime.

        Args:
            token_enhance_provider (DataServiceProviderInterface):
                -Provider for enhancing the tokens.
        """
        self.token_enhance_provider = token_enhance_provider

    def extract_all_fields(self, image_file_path: str, file_data_list: [ite.interface.FILE_DATA] = None,
                           within_bbox: list = None, config_param_dict: ite.interface.CONFIG_PARAM_DICT = None):
        """Extracts table data from an image and from optional supporting files those are in `file_data_list`
            returns as an json output and saves it as an html file.

        Args:
            image_file_path (str): Image file path for which table has to be extracted
            file_data_list (list): List of supporting files path and page numbers, if applicable.
                -Defaults to None.
            within_bbox (list, optional): Bounding box coordinates(x,y,width, height) of the table in the image.
                -Defaults to None.
            config_param_dict (CONFIG_PARAM_DICT, optional): [description]. Defaults to None.
                output: `path` to specify where to save the file and `format` for type of file to save the data
                table_organization_dict (dict, optional): [description]. Defaults to None.
                is_virtual_table_mode (bool, optional): [description]. Defaults to False.
                additional_info (ADDITIONAL_INFO, optional): Defaults to None.
                    Dictionary contains additional info about actual input provided.
                    For examples, `{'tesseract':'psm':''}` is about the *.hocr file psm
                    -of input provided in `file_data_list`.
        """
        config_param_dict = ExtractorUtil.get_updated_config_dict(
            config_param_dict, CONFIG_PARAM_DICT)
        response = self.__extract_all_fields(
            image_file_path, None, config_param_dict.get(
                'table_organization_dict'),
            within_bbox, config_param_dict, config_param_dict.get(
                'is_virtual_table_mode'), file_data_list,
            config_param_dict.get('ocr_tool_settings'))
        return response

    def __extract_all_fields(self, image_file_path: str,
                             output_dir: str,
                             table_organization_dict: dict = None,
                             within_bbox: list = None,
                             config_param_dict: dict = None,
                             is_virtual_table_mode: bool = False,
                             file_data_list: list = None,
                             additional_info: dict = None):
        def _crop_img(img_file_path, within_bbox):
            # name_with_bbox = "_".join([str(x) for x in within_bbox])
            image = cv2.imread(img_file_path)
            x, y, w, h = within_bbox
            new_shape_img = image[y:y+h, x:x+w]
            # img_file_path, ext = path.splitext(img_file_path)
            # img_file_path = f"{img_file_path}_{path.basename(img_file_path)}{ext}"
            cv2.imwrite(img_file_path, new_shape_img)
            return img_file_path

        def _copy_doc_to_temp(doc_file, temp_folder_path):
            file_name = path.basename(doc_file)
            new_image_file_path = f"{temp_folder_path}/{file_name}"
            shutil.copy(doc_file, new_image_file_path)
            return new_image_file_path

        error = None
        if not image_file_path:
            error = 'image_file_path is empty'
        if error:
            return {"fields": None, "error": error}
        self.logger.info('extraction started')
        fields, processing_msg, conf_score = [], [], {'row': 0, "column": 0}
        try:
            response, error = None, None
            temp_folder_path = ExtractorUtil.create_temp_dir(
                self.debug_mode_check, self.temp_file_dir, path.basename(image_file_path))
            new_image_file_path = _copy_doc_to_temp(
                image_file_path, temp_folder_path)
            file_name = path.basename(new_image_file_path)
            debug_location = None
            if within_bbox:
                # crop orginal image first when `within_bbox` given to get better outcome
                # small region gives better result compare to full document
                new_image_file_path = _crop_img(
                    new_image_file_path, within_bbox)

            if is_virtual_table_mode:
                # Convert image to gray scale and get max horizontal and vertical line positions
                img_bin, debug_location = ImageParserUtil.get_grayscale_and_noborder_img(
                    new_image_file_path, is_debug_mode=self.debug_mode_check, debug_path=temp_folder_path)
                # new_image_file_path, ext = path.splitext(new_image_file_path)
                # new_image_file_path = f"{new_image_file_path}_vtm{ext}"
                img_bin.save(new_image_file_path)

                # provider calls starts
                # provider can skip irrelavent config params sent to it.
                ocr_predicted_line_pos_dict = self.token_rows_cols_provider.get_rows_cols(
                    new_image_file_path,
                    2,
                    within_bbox,
                    file_data_list,
                    additional_info,
                    {'tesseract': {'psm': '12'}}
                )
                ocr_detected_tokens = self.token_detection_provider.get_tokens(
                    new_image_file_path,
                    1,
                    within_bbox,
                    file_data_list,
                    additional_info,
                    {'tesseract': {'psm': '3'}}
                )
                if self.token_enhance_provider:
                    ocr_detected_tokens = self.token_enhance_provider.get_enhanced_tokens(
                        ocr_detected_tokens,
                        new_image_file_path,
                        within_bbox,
                        file_data_list
                    )
                # provider calls ends

                out_file_name = f"{output_dir}/{file_name}.html" if output_dir else None
                csv_file_path = f"{temp_folder_path}/{file_name}_phrase_bbox.csv"
                phrase_token_data = []
                phrase_token_data = ExtractorUtil.get_phrases_from_words(
                    ocr_detected_tokens)
                if not phrase_token_data:
                    phrase_token_data = ocr_detected_tokens
                pd.DataFrame(phrase_token_data).to_csv(
                    csv_file_path, header=False)

                # Image line detection logics
                img_predicted_line_pos, debug_location = ImageParserUtil.get_line_position(
                    new_image_file_path, is_debug_mode=self.debug_mode_check, debug_path=debug_location)

                row_score, col_score = StatisticUtil.get_confidence_score(
                    ocr_predicted_line_pos_dict, img_predicted_line_pos)
                conf_score['row'] = row_score
                conf_score['column'] = col_score
                if self.debug_mode_check:
                    ImageParserUtil.draw_line_position(
                        new_image_file_path, img_predicted_line_pos, debug_location, "image_predicted")
                    ImageParserUtil.draw_line_position(
                        new_image_file_path, ocr_predicted_line_pos_dict, debug_location, "ocr_predicted")

                merged_line_pos = ExtractorUtil.merge_img_hocr_position(
                    img_predicted_line_pos, ocr_predicted_line_pos_dict)

                if self.debug_mode_check:
                    ImageParserUtil.draw_line_position(
                        new_image_file_path, merged_line_pos, debug_location, "ocr_img_merged")

                response = ExtractorUtil.convert_to_other(
                    phrase_token_data, merged_line_pos, out_file_name,
                    [ocr_predicted_line_pos_dict, img_predicted_line_pos],
                    [row_score, col_score], config_param_dict
                )
            else:
                new_image_file_path_tmp = new_image_file_path
                if self.debug_mode_check and not path.isdir(new_image_file_path):
                    new_image_file_path = path.dirname(new_image_file_path)

                enhan_hocr_file_path = glob.glob(
                    f"{new_image_file_path}/*_enhanced.hocr")
                # This condition will helps to avoid repeated hocr call in debug mode
                if not enhan_hocr_file_path:
                    enhan_hocr_file_path, debug_location, error = self.__img_extractor_obj.extract_enhanced_ocr(
                        new_image_file_path_tmp, temp_folder_path, processing_msg, psm='6'
                    )
                else:
                    enhan_hocr_file_path = enhan_hocr_file_path[0]
                # Amit and Prasanna logics
                new_image_file_path = path.dirname(new_image_file_path) if not path.isdir(
                    new_image_file_path) else new_image_file_path
                csv_file_path = f"{new_image_file_path}/{file_name}_word_bbox.csv"
                hocr_to_csv.HOCRToCSV.convert(
                    enhan_hocr_file_path, csv_file_path, processing_msg)
                response = internal_converter.convert_coordinates_to_html_table(
                    self.logger, [
                        csv_file_path], output_dir, table_organization_dict,
                    config_param_dict, processing_msg
                )
            fields.append(
                {'conf_score': conf_score, 'table_value': response, 'error': error,
                 'table_value_bbox': within_bbox, 'warning': None, 'processing_msg': processing_msg,
                 'debug_path': temp_folder_path}
            )
        except Exception as e:
            full_trace_error = traceback.format_exc()
            self.logger.error(full_trace_error)
            fields.append(
                {'conf_score': conf_score, 'table_value': None, 'error': e.args[0],
                 'table_value_bbox': within_bbox}
            )
        return {"fields": fields, "error": error}

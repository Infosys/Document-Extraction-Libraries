# ===============================================================================================================#
# Copyright 2021 Infosys Ltd.
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at
# http://www.apache.org/licenses/
# ===============================================================================================================#

import logging
import os
import enum
import sys
import traceback
from infy_bordered_table_extractor.internal import image_table_border_reader
from infy_bordered_table_extractor.internal.bordered_table_helper import TableHelper
from infy_bordered_table_extractor.interface.data_service_provider_interface import DataServiceProviderInterface


class LineDetectionMethod(enum.Enum):
    """enum class: To choose which line detection method to be used for extraction. """
    RGB_LINE_DETECT = 1
    OPENCV_LINE_DETECT = 2


class RgbSkewDetectionMethod(enum.Enum):
    """enum class: To choose which method to be used for skew detection, when using
    RGB_LINE_DETECT line detection method"""
    CONVOLUTION_CONTRAST_METHOD = 1
    ADAPTIVE_CONTRAST_METHOD = 2


class OutputFileFormat(enum.Enum):
    """ENUM class: to choose which format the output has to be saved"""
    EXCEL = 1


CONFIG_PARAM_DICT = {
    'custom_cells': [{'rows': [], 'columns':[]}],
    'col_header': {'use_first_row': True, 'values': []},
    'deskew_image_reqd': False,
    'image_cell_cleanup_reqd': True,
    'output': {
        'path': None,
        'format': None
    },
    'rgb_line_skew_detection_method': [RgbSkewDetectionMethod.CONVOLUTION_CONTRAST_METHOD],
    'line_detection_method': [LineDetectionMethod.RGB_LINE_DETECT],
}

FILE_DATA = {
    'path': '',
    'pages': []
}


class BorderedTableExtractor:
    """`Class containing APIs for data extraction from bordered table."""

    def __init__(self, table_detection_provider: DataServiceProviderInterface,
                 cell_extraction_provider: DataServiceProviderInterface,
                 temp_folderpath: str, logger: logging.Logger = None,
                 debug_mode_check: bool = False):
        """Creates an instance of Bordered Table Extractor.

        Args:
            table_detection_provider (DataServiceProviderInterface): Provider for table detection
            cell_extraction_provider (DataServiceProviderInterface): Provider for cell data extraction
            temp_folderpath (str): Path to temp folder
            logger (logging.Logger, optional): Path to store all the debug info files. Defaults to None.
            debug_mode_check (bool, optional): To get debug info while using the API. Defaults to False.

        Raises:
            Exception: tesseract_path provided doesn't exist.
            Exception: temp_folderpath provided doesn't exist
        """

        self.debug_mode_check = debug_mode_check
        self.temp_folderpath = temp_folderpath
        self.table_detection_provider = table_detection_provider
        self.cell_extraction_provider = cell_extraction_provider
        if not os.path.exists(temp_folderpath):
            raise Exception("temp_folderpath provided doesn't exist")
        self.logger = logger
        LOG_FORMAT = logging.Formatter(
            '%(asctime)s.%(msecs)03d %(levelname)s [%(threadName)s] [%(module)s] [%(funcName)s:%(lineno)d] %(message)s')
        if logger is None:
            LOG_LEVEL = logging.INFO

            self.logger = logging.getLogger(__name__)
            self.logger.setLevel(LOG_LEVEL)
            # Add sysout hander
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(LOG_LEVEL)
            console_handler.setFormatter(LOG_FORMAT)
            self.logger.addHandler(console_handler)
            self.logger.info('log initialized')
        else:
            hndlr = self.logger.handlers[0]
            hndlr.setFormatter(LOG_FORMAT)
            self.logger.info('Formatter updated')
        try:
            self.image_reader_obj = image_table_border_reader.ImageTableBorderReader(
                table_detection_provider, cell_extraction_provider, temp_folderpath,
                self.logger, debug_mode_check, LineDetectionMethod,
                RgbSkewDetectionMethod, OutputFileFormat)
        except Exception as ex:
            raise Exception(ex)

    def extract_all_fields(self, image_file: str, file_data_list: [FILE_DATA] = None,
                           within_bbox: list = None,
                           config_param_dict: CONFIG_PARAM_DICT = None):
        """Extracts table information from an image and returns as an json output and saves it as an
                excel file, if required.

        Args:
            image_file (str): image file path for which table has to be extracted
            file_data_list ([FILE_DATA], optional): List of all supporting file paths and page numbers, if applicable.
                Image and the file must have the same content.
            within_bbox (list, optional): Bounding box coordinates(x, y, width, height) of the table in the image.
                Defaults to None.
            config_param_dict (CONFIG_PARAM_DICT, optional): Additional info. Defaults to None.
                `custom_cells`: customized cell extraction
                `col_header`: Choose the header to be used `use_first_row`. To customize values for header use `values`.
                `deskew_image_reqd`: If detected skew in image is to be corrected
                `image_cell_cleanup_reqd`: If each cell image is required for cleaning for text extraction
                `output`: `path` to specify where to save the file and `format` for type of file to save the data
                `rgb_line_skew_detection_method`: List of all skew detection methods for detecting skewness
                `line_detection_method`: list of all line detection methods for line detection


        Raises:
            Exception: Valid imagepath is required.

        Returns:
            dict: Dict of saved info.
        """

        fields = []
        full_trace_error = None
        if config_param_dict:
            invalid_keys = TableHelper.get_invalid_keys(
                CONFIG_PARAM_DICT, config_param_dict)
            if len(invalid_keys) > 0:
                raise Exception(f"Invalid keys fcound: {invalid_keys}. ")
            config_param_dict = TableHelper.get_updated_config_dict(
                CONFIG_PARAM_DICT, config_param_dict)
        else:
            config_param_dict = CONFIG_PARAM_DICT

        try:
            if not os.path.exists(image_file):
                self.logger.error("property imagepath not found")
                raise Exception("property imagepath not found")

            # extract bordered table
            response, warning, processing_msg, debug_path = self.image_reader_obj.extract(
                image_file, file_data_list, within_bbox,
                config_param_dict=config_param_dict)
            fields.append(
                {'table_value': response, 'warning': warning, 'table_value_bbox': within_bbox,
                 'processing_msg': processing_msg, 'debug_path': debug_path})
        except Exception:
            full_trace_error = traceback.format_exc()
            self.logger.error(full_trace_error)
            fields.append(
                {'table_value': None, 'error': str(full_trace_error), 'table_value_bbox': within_bbox})
        output = {'fields': fields, 'error': full_trace_error}
        return output

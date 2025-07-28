# ===============================================================================================================#
# Copyright 2021 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import enum
from abc import ABC, abstractmethod
from typing import List


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


CONFIG_PARAM_DICT: dict = {
    'custom_cells': [{'rows': [], 'columns':[]}],
    'col_header': {'use_first_row': True, 'values': []},
    'deskew_image_reqd': False,
    'auto_detect_border': True,
    'image_cell_cleanup_reqd': True,
    'rgb_line_skew_detection_method': [RgbSkewDetectionMethod.CONVOLUTION_CONTRAST_METHOD],
    'line_detection_method': [LineDetectionMethod.RGB_LINE_DETECT],
    "ocr_tool_settings": {
        'tesseract': {
            'psm': ''
        }
    },
    'table_organization_dict': None,
    'is_virtual_table_mode': False
}

FILE_DATA: dict = {
    'path': '',
    'pages': []
}


class ITableExtractor(ABC):
    """Interface class of Table Extractor."""
    @abstractmethod
    def extract_all_fields(self, image_file_path: str, file_data_list: [FILE_DATA] = None,
                           within_bbox: list = None, config_param_dict: CONFIG_PARAM_DICT = None):
        """Extracts table information from an image and returns as an json output and saves it as an
                excel file, if required.

        Args:
            image_file_path (str): image file path for which table has to be extracted
            file_data_list ([FILE_DATA], optional): List of all supporting file paths and page numbers, if applicable.
                Image and the file must have the same content.
            within_bbox (list, optional): Bounding box coordinates(x, y, width, height) of the table in the image.
                Defaults to None.
            config_param_dict (CONFIG_PARAM_DICT, optional): Additional info. Defaults to None.

        Raises:
            Exception: Valid imagepath is required.

        Returns:
            dict: Dict of saved info.
        """

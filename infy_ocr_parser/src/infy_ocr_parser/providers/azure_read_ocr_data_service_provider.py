# ===============================================================================================================#
# Copyright 2021 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import logging
import json
from infy_ocr_parser.internal.response import Response
from infy_ocr_parser.interface.data_service_provider_interface import DataServiceProviderInterface

IN_TO_PX = 96


class AzureReadOcrDataServiceProvider(DataServiceProviderInterface):
    """Implementation of DataServiceProvider for AZURE-Read API"""

    def __init__(self, logger: logging.Logger = None,
                 log_level: int = None):
        """Creates an instance of Provider Interface

        Args:
            logger (logging.Logger, optional): logger object. Defaults to None.
            log_level (int, optional):log level. Defaults to None.
        """
        super(AzureReadOcrDataServiceProvider,
              self).__init__(logger, log_level)
        self._ocr_file_data_list = []

    def init_provider_inputs(self, doc_list: list):
        """Method used to load the list input ocr files to given provider.

        Args:
            doc_list (list):  OCR file list
        """
        if doc_list:
            self._ocr_file_data_list = []
        for ocr_file in doc_list:
            with open(ocr_file, 'r', encoding='utf8') as file_reder:
                self._ocr_file_data_list.append(json.load(file_reder))

    def get_line_dict_from(self, pages: list = None, line_dict_list: list = None, scaling_factors=None) -> list:
        """Returns list of line dictionary containing text and bbox values.

        Args:
            pages (list, optional): Page to filter from given `doc_list`. Defaults to None.
            line_dict_list (list, optional):  Existing line dictonary to filter certain page(s).
                - Defaults to None.
            scaling_factors (list, optional): value to scale up/down the bbox. First element is for
                vertical scaling factor and second is for horizontal scaling factor.
                - Defaults to [1.0, 1.0]

        Raises:
            Exception: Raises an Exception

        Returns:
            list: List of line dictionary containing the text, words and respective bbox values.
        """
        if not scaling_factors:
            scaling_factors = [1.0, 1.0]
        try:
            lines_structure = []
            if line_dict_list:
                if len(pages) == 0:
                    return line_dict_list
                else:
                    _ = [lines_structure.append(
                        ocr_line_obj) for ocr_line_obj in line_dict_list if ocr_line_obj["page"] in pages]
                    return lines_structure

            for ocr_file in self._ocr_file_data_list:
                for page_obj in ocr_file["readResults"]:
                    page_no = page_obj["page"]
                    bbox_unit = page_obj["unit"]
                    if len(pages) > 0 and page_no not in pages:
                        continue
                    for line_obj in page_obj['lines']:
                        word_structure = self.get_word_dict_from(
                            line_obj, [
                                page_no], scaling_factors=scaling_factors,
                            bbox_unit=bbox_unit)
                        line_text = line_obj["text"]
                        # The coordinates of the bounding box
                        (l, t, r, b) = self.__get_formatted_bbox(
                            line_obj["boundingBox"], bbox_unit)
                        lines_structure.append(
                            Response.data_dict(
                                f"line_{page_no}_{l}_{t}_{r}_{b}",
                                page_no,
                                line_text,
                                [l, t, r-l, b-t],
                                f'{scaling_factors[0]}_{scaling_factors[1]}',
                                word_structure=word_structure
                            ))
            return lines_structure
        except Exception as e:
            raise Exception(e)

    def get_word_dict_from(self, line_obj=None, pages: list = None,
                           word_dict_list: list = None, scaling_factors=None,
                           bbox_unit='pixel') -> list:
        """Returns list of word dictionary containing text and bbox values.

        Args:
            line_obj ([any], optional):  Existing line object to get words of it.
                - Defaults to None.
            pages (list, optional): Page to filter from given `doc_list`. Defaults to None.
            word_dict_list (list, optional):  Existing word dictonary to filter certain page(s).
                - Defaults to None.
            scaling_factors (list, optional): value to scale up/down the bbox. First element is for
                vertical scaling factor and second is for horizontal scaling factor.
                - Defaults to [1.0, 1.0]
            bbox_unit (str, optional): Unit of bbox value. Defaults to 'pixel'.

        Returns:
            list: List of word dictionary containing the text, bbox and conf values.
        """
        word_structure = []
        if not scaling_factors:
            scaling_factors = [1.0, 1.0]
        if line_obj:
            return self.__get_word_dict_from_line(line_obj, pages[0], scaling_factors, bbox_unit)

        if word_dict_list:
            if len(pages) == 0:
                return word_dict_list
            else:
                _ = [word_structure.append(
                    ocr_word_obj) for ocr_word_obj in word_dict_list if ocr_word_obj["page"] in pages]
                return word_structure

        for ocr_file in self._ocr_file_data_list:
            for page_obj in ocr_file["readResults"]:
                page_no = page_obj["page"]
                bbox_unit = page_obj["unit"]
                if len(pages) > 0 and page_no not in pages:
                    continue
                for line_obj in page_obj['lines']:
                    word_structure += self.__get_word_dict_from_line(
                        line_obj, page_no, scaling_factors, bbox_unit)
        return word_structure

    def get_page_bbox_dict(self) -> list:
        """Returns pages wise bbox list

        Returns:
            list: List of dictionary containing page num and its bbox values.
        """
        page_bbox_dict_list = []

        def _page_bbox(file_data):
            point = self.__get_unit_point(file_data["unit"])
            w = (file_data["width"])*point
            h = (file_data["height"])*point
            infy_ocr_generator_metadata = file_data.get(
                'infy_ocr_generator_metadata', {})
            page = infy_ocr_generator_metadata.get(
                'doc_page_num', file_data["page"])
            bbox_dict = {"bbox": [0, 0, w, h], "page": page}
            return bbox_dict
        for ocr_file in self._ocr_file_data_list:
            page_bbox_dict_list += [_page_bbox(file_data)
                                    for file_data in ocr_file["readResults"]]
        return page_bbox_dict_list

    def __get_word_dict_from_line(self, line_obj, page, scaling_factors, bbox_unit) -> list:
        word_structure = []
        if not (line_obj or page):
            raise Exception
        for word_obj in line_obj["words"]:
            (l, t, r, b) = self.__get_formatted_bbox(
                word_obj["boundingBox"], bbox_unit)
            word_structure.append(
                Response.data_dict(
                    f"word_{page}_{l}_{t}_{r}_{b}",
                    page,
                    word_obj["text"],
                    [l, t, r-l, b-t],
                    f'{scaling_factors[0]}_{scaling_factors[1]}',
                    conf=word_obj["confidence"]
                ))
        return word_structure

    def __get_formatted_bbox(self, bbox_list, bbox_unit):
        point = self.__get_unit_point(bbox_unit)
        # new_bbox_list = [round(bbox*point) for bbox in bbox_list]
        new_bbox_list = bbox_list
        X1, Y1, X2, Y2, X3, Y3, X4, Y4 = 0, 1, 2, 3, 4, 5, 6, 7
        # l = min(x1, x4)
        # t = min(y1, y2)

        # r = max(x2,x3)
        # b = max(y3,y4)
        l = min(new_bbox_list[X1], new_bbox_list[X4])
        t = min(new_bbox_list[Y1], new_bbox_list[Y2])
        r = max(new_bbox_list[X2], new_bbox_list[X3])
        b = max(new_bbox_list[Y3], new_bbox_list[Y4])
        return [(bbox*point) for bbox in [l, t, r, b]]

    def __get_unit_point(self, bbox_unit):
        # pdf unit is inch and image unit is pixel
        return IN_TO_PX if bbox_unit == 'inch' else 1

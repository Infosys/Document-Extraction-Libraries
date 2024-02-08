# ===============================================================================================================#
# Copyright 2021 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import logging
import json

from infy_ocr_parser.interface.data_service_provider_interface import \
    DataServiceProviderInterface
from infy_ocr_parser.internal.response import Response


class AzureOcrDataServiceProvider(DataServiceProviderInterface):
    """Implementation of DataServiceProvider for AZURE-Read API"""

    def __init__(self, logger: logging.Logger = None,
                 log_level: int = None):
        """Creates an instance of AzureOcrDataServiceProvider class

        Args:
            logger (logging.Logger, optional): logger object. Defaults to None.
            log_level (int, optional): log level. Defaults to None.
        """
        super(AzureOcrDataServiceProvider, self).__init__(logger, log_level)
        self._ocr_file_data_list = []

    def init_provider_inputs(self, doc_list: list):
        """Method used to load the list input ocr files to given provider.

        Args:
            doc_list (list): OCR file list
        """
        if doc_list:
            self._ocr_file_data_list = []
        for ocr_file in doc_list:
            with open(ocr_file, 'r', encoding='utf8') as file_reder:
                self._ocr_file_data_list.append(json.load(file_reder))

    def get_line_dict_from(self, pages: list = None, line_dict_list: list = None, scaling_factors=None) -> list:
        """Returns list of line dictionary containing text and bbox values.

        Args:
            pages (list, optional):Page to filter from given `doc_list`. Defaults to None.
            line_dict_list (list, optional): Existing line dictonary to filter certain page(s).
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

            for i, ocr_file_data in enumerate(self._ocr_file_data_list):
                infy_ocr_generator_metadata = ocr_file_data.get(
                    'infy_ocr_generator_metadata', {})
                page_no = int(infy_ocr_generator_metadata.get(
                    'doc_page_num', i+1))
                if len(pages) > 0 and page_no not in pages:
                    continue
                for region_obj in ocr_file_data["regions"]:
                    for line_obj in region_obj["lines"]:
                        word_structure = self.__get_word_dict_from(
                            line_obj, [page_no], scaling_factors=scaling_factors)
                        line_text = " ".join([word_obj["text"]
                                              for word_obj in line_obj["words"]])
                        # The coordinates of the bounding box
                        (l, t, r, b) = self._get_formatted_bbox(
                            line_obj["boundingBox"])
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

    def get_word_dict_from(self, pages: list = None,
                           word_dict_list: list = None, scaling_factors: list = None) -> list:
        return self.__get_word_dict_from(
            pages=pages, word_dict_list=word_dict_list, scaling_factors=scaling_factors)

    def __get_word_dict_from(self, line_obj=None, pages: list = None,
                             word_dict_list: list = None, scaling_factors=None) -> list:
        """"Returns list of word dictionary containing text and bbox values.

        Args:
            line_obj ([any], optional): Existing line object to get words of it.
                - Defaults to None.
            pages (list, optional): Page to filter from given `doc_list`. Defaults to None.
            word_dict_list (list, optional): Existing word dictonary to filter certain page(s).
                - Defaults to None.
            scaling_factors (list, optional):  value to scale up/down the bbox. First element is for
                vertical scaling factor and second is for horizontal scaling factor.
                - Defaults to [1.0, 1.0]

        Returns:
            list: List of word dictionary containing the text, bbox and conf values.
        """
        word_structure = []
        if not scaling_factors:
            scaling_factors = [1.0, 1.0]
        if line_obj:
            return self.__get_word_dict_from_line(line_obj, pages[0], scaling_factors)

        if word_dict_list:
            if len(pages) == 0:
                return word_dict_list
            else:
                _ = [word_structure.append(
                    ocr_word_obj) for ocr_word_obj in word_dict_list if ocr_word_obj["page"] in pages]
                return word_structure

        for i, ocr_file_data in enumerate(self._ocr_file_data_list):
            infy_ocr_generator_metadata = ocr_file_data.get(
                'infy_ocr_generator_metadata', {})
            page_no = int(infy_ocr_generator_metadata.get(
                'doc_page_num', i+1))
            if len(pages) > 0 and page_no not in pages:
                continue
            for region_obj in ocr_file_data["regions"]:
                for line_obj in region_obj["lines"]:
                    word_structure += self.__get_word_dict_from_line(
                        line_obj, page_no, scaling_factors)
        return word_structure

    def get_page_bbox_dict(self) -> list:
        """Returns pages wise bbox list

        Returns:
            list: List of dictionary containing page num and its bbox values.
        """
        page_bbox_dict_list = []
        for i, ocr_file in enumerate(self._ocr_file_data_list):
            infy_ocr_generator_metadata = ocr_file.get(
                'infy_ocr_generator_metadata', {})
            page_bbox_dict_list.append(
                {"bbox": [0, 0,
                          int(ocr_file.get(
                              "width", infy_ocr_generator_metadata.get('width', 0))),
                          int(ocr_file.get(
                              "height", infy_ocr_generator_metadata.get('height', 0)))
                          ],
                 "page": int(infy_ocr_generator_metadata.get('doc_page_num', i+1))}
            )
        return page_bbox_dict_list

    def __get_word_dict_from_line(self, line_obj, page, scaling_factors) -> list:
        word_structure = []
        if not (line_obj or page):
            raise Exception
        for word_obj in line_obj["words"]:
            (l, t, r, b) = self._get_formatted_bbox(word_obj["boundingBox"])
            word_structure.append(
                Response.data_dict(
                    f"word_{page}_{l}_{t}_{r}_{b}",
                    page,
                    word_obj["text"],
                    [l, t, r-l, b-t],
                    f'{scaling_factors[0]}_{scaling_factors[1]}'
                ))
        return word_structure

    def _get_formatted_bbox(self, bbox):
        (l, t, w, h) = [int(bb) for bb in bbox.split(',')]
        return [l, t, l+w, t+h]

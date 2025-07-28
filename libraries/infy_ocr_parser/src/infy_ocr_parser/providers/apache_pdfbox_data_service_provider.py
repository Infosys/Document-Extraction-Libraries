# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import json
import logging

from infy_ocr_parser.interface.data_service_provider_interface import \
    DataServiceProviderInterface
from infy_ocr_parser._internal.response import Response


class ApachePdfboxDataServiceProvider(DataServiceProviderInterface):
    """Implementation of DataServiceProvider for Apache Pdfbox"""

    def __init__(self, logger: logging.Logger = None,
                 log_level: int = None):
        """Creates an instance of ApachePdfboxDataServiceProvider class

        Args:
            logger (logging.Logger, optional): logger object. Defaults to None.
            log_level (int, optional): log level. Defaults to None.
        """
        super(ApachePdfboxDataServiceProvider,
              self).__init__(logger, log_level)
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

    def get_line_dict_from(self, pages: list = None,
                           line_dict_list: list = None, scaling_factors: list = None) -> list:
        """Returns list of line dictionary containing text and bbox values.

        Args:
            pages (list, optional):  Page to filter from given `doc_list`. Defaults to None.
            line_dict_list (list, optional): Existing line dictonary to filter certain page(s).
                - Defaults to None.
            scaling_factors (list, optional): value to scale up/down the bbox. First element is for
                vertical scaling factor and second is for horizontal scaling factor.
                - Defaults to [1.0, 1.0]

        Raises:
            Exception: Raises an Exception if the method is not implemented.

        Returns:
            list:  List of line dictionary containing the text, words and respective bbox values.
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
                        ocr_line_obj) for ocr_line_obj in line_dict_list
                        if ocr_line_obj["page"] in pages]
                    return lines_structure

            for ocr_file in self._ocr_file_data_list:
                infy_ocr_generator_metadata = ocr_file.get(
                    'infy_ocr_generator_metadata', {})
                page_no = int(infy_ocr_generator_metadata.get(
                    'doc_page_num', ocr_file["page"]))
                if len(pages) > 0 and page_no not in pages:
                    continue
                for line_obj in ocr_file['tokens']:
                    if line_obj['type'] == 'line':
                        word_structure = []
                        line_text = line_obj["text"]
                        # The coordinates of the bounding box
                        (l, t, r, b) = line_obj['bbox']
                        confidence_pct = -1
                        lines_structure.append(
                            Response.data_dict(
                                f"line_{page_no}_{l}_{t}_{r}_{b}",
                                page_no,
                                line_text,
                                [l, t, r-l, b-t],
                                f'{scaling_factors[0]}_{scaling_factors[1]}',
                                word_structure=word_structure,
                                conf=confidence_pct

                            ))
            return lines_structure
        except Exception as e:
            raise Exception(e)

    def get_word_dict_from(self, pages: list = None,
                           word_dict_list: list = None, scaling_factors: list = None) -> list:
        '''getting words from ocr file data'''
        # currently not implemented
        return []

    def get_page_bbox_dict(self) -> list:
        """Returns pages wise bbox list

        Returns:
            list: List of dictionary containing page num and its bbox values.
        """
        page_bbox_dict_list = []

        def _page_bbox(file_data, infy_ocr_generator_metadata):
            w = file_data['width']
            h = file_data["height"]
            page = int(infy_ocr_generator_metadata.get(
                'doc_page_num', file_data["page"]))
            bbox_dict = {"bbox": [0, 0, w, h], "page": page}
            return bbox_dict
        for ocr_file in self._ocr_file_data_list:
            # infy_ocr_generator_metadata is available at same readResults hierarchy level
            infy_ocr_generator_metadata = ocr_file.get(
                'infy_ocr_generator_metadata', {})
            page_bbox_dict_list += [_page_bbox(ocr_file,
                                               infy_ocr_generator_metadata)]
        return page_bbox_dict_list

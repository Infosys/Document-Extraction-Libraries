# ===============================================================================================================#
# Copyright 2021 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import logging
import bs4
from infy_ocr_parser.interface.data_service_provider_interface import \
    DataServiceProviderInterface
from infy_ocr_parser.internal.response import Response


class TesseractOcrDataServiceProvider(DataServiceProviderInterface):
    """Implementation of DataServiceProvider for Tesseract OCR"""

    def __init__(self, logger: logging.Logger = None,
                 log_level: int = None):
        """Creates an instance of TesseractOcrDataServiceProvider class

        Args:
            logger (logging.Logger, optional): logger object. Defaults to None.
            log_level (int, optional): log level. Defaults to None.
        """
        super(TesseractOcrDataServiceProvider,
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
                self._ocr_file_data_list.append(file_reder.read())

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
                        ocr_line_obj) for ocr_line_obj in line_dict_list if ocr_line_obj["page"] in pages]
                    return lines_structure

            for ocr_file in self._ocr_file_data_list:
                soup = bs4.BeautifulSoup(ocr_file, 'lxml')
                page_detail_dict = self.__get_page_detail_from(soup)
                if page_detail_dict:
                    page_no = page_detail_dict.get('page', 0)
                    if len(pages) > 0 and page_no not in pages:
                        continue
                else:
                    continue

                ocr_lines = soup.findAll("span", {"class": "ocr_line"})
                ocr_header = soup.findAll("span", {"class": "ocr_header"})
                ocr_lines += ocr_header
                for line in ocr_lines:
                    word_structure = self.__get_word_dict_from(
                        line, [page_no], scaling_factors=scaling_factors)
                    line_text = line.text.replace("\n", " ").strip()
                    title = line['title']
                    # The coordinates of the bounding box
                    l, t, r, b = map(int, title[5:title.find(";")].split())
                    w, h = r-l, b-t
                    lines_structure.append(
                        Response.data_dict(
                            f"line_{page_no}_{l}_{t}_{r}_{b}",
                            page_no,
                            line_text,
                            [l, t, w, h],
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
                             word_dict_list: list = None, scaling_factors: list = None) -> list:
        """Returns list of word dictionary containing text and bbox values.

        Args:
            line_obj ([any], optional): Existing line object to get words of it.
                - Defaults to None.
            pages (list, optional): Page to filter from given `doc_list`. Defaults to None.
            word_dict_list (list, optional): Existing word dictonary to filter certain page(s).
                - Defaults to None.
            scaling_factors (list, optional): value to scale up/down the bbox. First element is for
                vertical scaling factor and second is for horizontal scaling factor.
                - Defaults to [1.0, 1.0]

        Returns:
            list: List of word dictionary containing the text, bbox and conf values.
        """
        if not scaling_factors:
            scaling_factors = [1.0, 1.0]
        if line_obj:
            return self.__get_word_dict_from_soup(line_obj, pages[0], scaling_factors)

        word_structure = []
        if word_dict_list:
            if len(pages) == 0:
                return word_dict_list
            else:
                _ = [word_structure.append(
                    ocr_word_obj) for ocr_word_obj in word_dict_list if ocr_word_obj["page"] in pages]
                return word_structure

        for ocr_file in self._ocr_file_data_list:
            soup = bs4.BeautifulSoup(ocr_file, 'lxml')
            page_detail_dict = self.__get_page_detail_from(soup)
            if page_detail_dict:
                page_no = page_detail_dict.get('page', 0)
                if len(pages) > 0 and page_no not in pages:
                    continue
            else:
                page_no = 0
            word_structure += self.__get_word_dict_from_soup(
                soup, page_no, scaling_factors)
        return word_structure

    def __get_page_detail_from(self, soup):
        page_detail_dict = {}
        ocr_page = soup.find("div", {"class": "ocr_page"})
        if ocr_page:
            title = ocr_page[
                'title'].split(";")[1]
            title_bbox = title.replace(" bbox ", "").split()
            page_num = int(ocr_page['id'].replace('page_', ''))
            page_detail_dict = {
                "bbox": [int(t_bbox) for t_bbox in title_bbox], "page": page_num}
        return page_detail_dict

    def get_page_bbox_dict(self) -> list:
        """Returns pages wise bbox list

        Returns:
            list:  List of dictionary containing page num and its bbox values.
        """
        page_bbox_dict_list = []
        for ocr_file in self._ocr_file_data_list:
            soup = bs4.BeautifulSoup(ocr_file, 'lxml')
            page_detail_dict = self.__get_page_detail_from(soup)
            if page_detail_dict:
                page_bbox_dict_list.append(page_detail_dict)
        return page_bbox_dict_list

    def __get_word_dict_from_soup(self, soup_obj, page, scaling_factors) -> list:
        word_structure = []
        if not (soup_obj or page):
            raise Exception
        ocr_xword = soup_obj.findAll("span", {"class": "ocrx_word"})
        for line in ocr_xword:
            line_text = line.text.replace("\n", " ").strip()
            title = line['title']
            # The coordinates of the bounding box
            conf = str(title).split(';')[1].replace('x_wconf', '').strip()
            l, t, r, b = map(int, title[5:title.find(";")].split())
            w, h = r-l, b-t
            word_structure.append(
                Response.data_dict(
                    f"word_{page}_{l}_{t}_{r}_{b}",
                    page,
                    line_text,
                    [l, t, w, h],
                    f'{scaling_factors[0]}_{scaling_factors[1]}',
                    conf=conf
                ))
        return word_structure

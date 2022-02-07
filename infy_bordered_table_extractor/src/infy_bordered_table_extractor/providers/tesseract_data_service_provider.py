# ===============================================================================================================#
# Copyright 2021 Infosys Ltd.
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at
# http://www.apache.org/licenses/                                              #
# ===============================================================================================================#

import os
import time
import logging
import numpy as np
import pytesseract
from pytesseract import Output
import bs4
from infy_bordered_table_extractor.interface.data_service_provider_interface import DataServiceProviderInterface,\
    FILE_DATA, IMG_CELL_BBOX, GET_TEXT_OUTPUT, ADDITIONAL_INFO, GET_TOKENS_OUTPUT


class TesseractDataServiceProvider(DataServiceProviderInterface):
    """Tesseract Data Service Provider"""

    def __init__(self, tesseract_path: str, logger: logging.Logger = None, log_level: int = None):
        """Creates an instance of Tesseract Data Service Provider

        Args:
            tesseract_path (str): Path to Tesseract.
            logger (logging.Logger, optional): Logger object. Defaults to None.
            log_level (int, optional): Logging Level. Defaults to None.
        """
        super(TesseractDataServiceProvider, self).__init__(logger, log_level)
        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path

        # This will validate and throw error if tesseract not configured properly
        tesseract_version = pytesseract.get_tesseract_version()
        self.logger.info("Tesseract version = %s", tesseract_version)

    def get_tokens(self, token_type_value: int, img: np.array,
                   file_data_list: [FILE_DATA] = None) -> [GET_TOKENS_OUTPUT]:
        """Method to be implemented to get all tokens (word, phrase or line) and its 
            bounding box as x, y, width and height from an image as a list of dictionary.
            Currently word token is only required.


        Args:
            token_type_value (int): 1(WORD), 2(LINE), 3(PHRASE)
            img (np.array): Read image as np array of the original image.
            file_data_list ([FILE_DATA], optional):  List of all file datas. Each file data has
                the path to supporting document and page numbers, if applicable.
                When multiple files are passed, provider has to pick the right file based 
                on the image dimensions or type of file extension.
                Defaults to None.

        Returns:
            [GET_TOKENS_OUTPUT]: list of dict containing text and its bbox.
        """
        if not file_data_list:
            file_data = pytesseract.image_to_pdf_or_hocr(
                img, extension='hocr')
        else:
            file_data = self._get_hocr_file(file_data_list)
        soup = bs4.BeautifulSoup(file_data, 'lxml')
        word_structure = []
        if token_type_value == 1:
            ocr_xword = soup.findAll("span", {"class": "ocrx_word"})
        for line in ocr_xword:
            line_text = line.text.replace("\n", " ").strip()
            title = line['title']
            # The coordinates of the bounding box
            conf = str(title).split(';')[1].replace('x_wconf', '').strip()
            x, y, w, h = map(int, title[5:title.find(";")].split())
            word_structure.append(
                {'text': line_text, 'bbox': [x, y, w-x, h-y], 'conf': conf})
        return word_structure

    def get_text(self, img: np.array, img_cell_bbox_list: [IMG_CELL_BBOX],
                 file_data_list: [FILE_DATA] = None,
                 additional_info: ADDITIONAL_INFO = None,
                 temp_folderpath: str = None) -> [GET_TEXT_OUTPUT]:
        """Method to be implemented to return the text from the list of
        cell images or bbox of the original image as a list of dictionary.
        (Eg. [{'cell_id': str,'cell_text':'{{extracted_text}}', 'cell_bbox':[x, y, w, h]}]

        Args:
            img (np.array): Read image as np array of the original image.
            img_cell_bbox_list ([IMG_CELL_BBOX]): List of all cell bbox
            file_data_list (FILE_DATA,optional): List of all file datas. Each file data
                has the path to supporting document and page numbers, if applicable.
                Defaults to None.
            additional_info (ADDITIONAL_INFO, optional): Additional info. Defaults to None.
            temp_folderpath (str, optional): Path to temp folder. Defaults to None.

        Returns:
            [GET_TEXT_OUTPUT]: list of dict containing text and its bbox.
        """
        t = str(time.time())
        result = []
        blank_text_index = []
        ocr_file_path = f'{temp_folderpath}/img_list-{t}.txt'
        ocr_file = open(ocr_file_path, "w+")
        for data_dict in additional_info['cell_info']:
            ocr_file.write(data_dict['cell_img_path'] + '\n')
        ocr_file.close()

        # ocr extraction with psm 3
        data = pytesseract.image_to_string(
            ocr_file_path, config='--psm 3',
            output_type=Output.BYTES).decode('utf-8').split('\x0c')[:-1]
        os.remove(ocr_file_path)
        ocr_file = open(ocr_file_path, "w+")
        for i, d in enumerate(data):
            result.append(
                {'cell_text': d, 'cell_bbox': additional_info['cell_info'][i]['cell_bbox']})
            if d == '':
                blank_text_index.append(i)
                ocr_file.write(
                    additional_info['cell_info'][i]['cell_img_path']+'\n')
        ocr_file.close()

        blank_text_index_2 = []
        if len(blank_text_index) > 0:
            # ocr extraction with psm 6
            data = pytesseract.image_to_string(
                ocr_file_path, config='--psm 6',
                output_type=Output.BYTES).decode('utf-8').split('\x0c')[:-1]
            os.remove(ocr_file_path)
            ocr_file = open(ocr_file_path, "w+")
            for i, d in enumerate(data):
                if d != '':
                    result[blank_text_index[i]]['cell_text'] = d
                if d == '':
                    blank_text_index_2.append(blank_text_index[i])
                    ocr_file.write(
                        additional_info['cell_info'][i]['cell_img_path']+'\n')
            ocr_file.close()

        if len(blank_text_index_2) > 0:
            # ocr extraction with psm 7
            data = pytesseract.image_to_string(
                ocr_file_path, config='--psm 7',
                output_type=Output.BYTES).decode('utf-8').split('\x0c')[:-1]
            for i, d in enumerate(data):
                if d != '':
                    result[blank_text_index_2[i]]['cell_text'] = d
        return result

    def _get_hocr_file(self, file_data_list):
        for file_data in file_data_list:
            if file_data['path'].lower().endswith('hocr'):
                return file_data['path']
        raise Exception("hocr file not found")

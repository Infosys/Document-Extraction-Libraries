# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                  #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import os
import json
import glob
import time
import logging
from pathlib import Path
import subprocess
import numpy as np
import bs4
from infy_table_extractor.bordered_table_extractor.interface.data_service_provider_interface import DataServiceProviderInterface, \
    FILE_DATA, IMG_CELL_BBOX, GET_TEXT_OUTPUT, ADDITIONAL_INFO, GET_TOKENS_OUTPUT

JAR_GENERAL_ERROR_MSG = 'Error occurred in main method'


class InfyOcrEngineDataServiceProvider(DataServiceProviderInterface):
    """Tesseract Data Service Provider"""

    def __init__(self, infy_ocr_engine_jar_home: str, model_dir_path: str, logger: logging.Logger = None, log_level: int = None):
        """Creates an instance of Tesseract Data Service Provider

        Args:
            infy_ocr_engine_jar_home (str): Path to InfyOcrEngine jar home.
            logger (logging.Logger, optional): Logger object. Defaults to None.
            log_level (int, optional): Logging Level. Defaults to None.
        """
        super(InfyOcrEngineDataServiceProvider,
              self).__init__(logger, log_level)
        self.infy_ocr_engine_jar_home = infy_ocr_engine_jar_home
        self.model_dir_path = model_dir_path

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
            file, _ = self._call_exe(img, 'hocr')
            output_doc = file.split('\n', maxsplit=1)[0]
            with open(output_doc, 'r', encoding='utf-8') as file:
                file_data = file.read()
        else:
            file_data = self._get_hocr_file(file_data_list)
        soup = bs4.BeautifulSoup(file_data, features='xml')
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
        image_dict_list_json_file_path = f'{temp_folderpath}/img_list-{t}.json'
        image_dict_list = []
        for data_dict in additional_info['cell_info']:
            image_dict = {
                "image_path": data_dict['cell_img_path'],
                "data": ""
            }
            image_dict_list.append(image_dict)
        with open(image_dict_list_json_file_path, 'w', encoding='utf-8') as json_file:
            json.dump(image_dict_list, json_file, indent=4)

        # ocr extraction with psm 3
        output_json_file, _ = self._call_exe(
            image_dict_list_json_file_path, 'txt')
        output_json_file_path = output_json_file.split('\n', maxsplit=1)[0]

        with open(output_json_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        os.remove(image_dict_list_json_file_path)
        image_dict_list = []
        for i, d in enumerate(data):
            result.append(
                {'cell_text': d.get('data').strip(), 'cell_bbox': additional_info['cell_info'][i]['cell_bbox']})
            if d.get('data') == '':
                blank_text_index.append(i)
                image_dict_list.append(d)

        blank_text_index_2 = []
        if len(blank_text_index) > 0:
            with open(image_dict_list_json_file_path, 'w', encoding='utf-8') as json_file:
                json.dump(image_dict_list, json_file, indent=4)

            # ocr extraction with psm 6
            output_json_file, _ = self._call_exe(
                image_dict_list_json_file_path, 'txt', '6')
            output_json_file_path = output_json_file.split('\n', maxsplit=1)[0]

            with open(output_json_file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            os.remove(image_dict_list_json_file_path)
            image_dict_list = []
            for i, d in enumerate(data):
                if d.get('data') != '':
                    result[blank_text_index[i]]['cell_text'] = d.get(
                        'data').strip()
                if d.get('data') == '':
                    blank_text_index_2.append(blank_text_index[i])
                    image_dict_list.append(d)

        if len(blank_text_index_2) > 0:
            with open(image_dict_list_json_file_path, 'w', encoding='utf-8') as json_file:
                json.dump(image_dict_list, json_file, indent=4)

            # ocr extraction with psm 7
            output_json_file, _ = self._call_exe(
                image_dict_list_json_file_path, 'txt', '7')
            output_json_file_path = output_json_file.split('\n', maxsplit=1)[0]

            with open(output_json_file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            os.remove(image_dict_list_json_file_path)
            for i, d in enumerate(data):
                if d.get('data') != '':
                    result[blank_text_index_2[i]]['cell_text'] = d.get(
                        'data').strip()
        # for data_dict in additional_info['cell_info']:
        #     data = _get_data(data_dict['cell_img_path'], 'txt')

        #     if data == '':  # If the text is blank
        #         data = _get_data(data_dict['cell_img_path'], 'txt', '6')
        #         if data == '':
        #             data = _get_data(data_dict['cell_img_path'], 'txt', '7')

        #     result.append(
        #         {'cell_text': data, 'cell_bbox': data_dict['cell_bbox']})

        return result

    def _call_exe(self, input_json_file, ocr_format, psm=None):

        def _get_tool_path():
            JAR_FILE_FORMAT = "infy-ocr-engine-*.jar"
            tool_path = str(
                f"{self.infy_ocr_engine_jar_home}/{JAR_FILE_FORMAT}")
            ocr_engine_jars = glob.glob(tool_path)
            ocr_engine_jars.sort(reverse=True)
            if ocr_engine_jars:
                tool_path = str(Path(ocr_engine_jars[0]).resolve())
            else:
                raise Exception(
                    f"Could not find any jar file of format '{JAR_FILE_FORMAT}' at provided path '{self.infy_ocr_engine_jar_home}'")
            return tool_path

        run_command = ['java', '-jar', _get_tool_path(),
                       '--fromfile', input_json_file, '--modeldir', self.model_dir_path,
                       '--ocrformat', ocr_format, '--lang', 'eng'
                       ]

        if psm:
            run_command.extend(['--psm', psm])

        sub_process = subprocess.Popen(
            run_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        stdout, stderr = sub_process.communicate()
        if (not stdout and stderr) or (JAR_GENERAL_ERROR_MSG in stdout):
            logger = logging.getLogger(os.path.basename(__file__))
            logger.error(stderr)
            return None, stderr

        return stdout, None

    def _get_hocr_file(self, file_data_list):
        for file_data in file_data_list:
            if file_data['path'].lower().endswith('hocr'):
                return file_data['path']
        raise Exception("hocr file not found")

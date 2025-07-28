# ===============================================================================================================#
# Copyright 2020 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import os
from pathlib import PurePath
import pytesseract
import cv2
import bs4
from infy_table_extractor.borderless_table_extractor.interface.data_service_provider_interface import DataServiceProviderInterface


class OcrConstants():
    """Constants"""
    MAX_INT16 = 32767


class TesseractDataServiceProvider(DataServiceProviderInterface):
    """Data Service Provider to extract from Image document."""

    def __init__(self, tesseract_path, logger=None, log_level=None):
        """Creates an instance of TesseractDataServiceProvider

        Args:
            tesseract_path (str): Path to the Tesseract executable.
            logger (logging.Logger, optional): Logger object. Defaults to None.
            log_level (int, optional): Logging Level. Defaults to None.

        Example:
            >>> import logging
            >>> logging.disable(logging.CRITICAL)
            >>> provider = TesseractDataServiceProvider(r'C:\\MyProgramFiles\\Tesseract-OCR\\tesseract.exe')
            >>> isinstance(provider, TesseractDataServiceProvider)
            True
            >>> logging.disable(logging.NOTSET)
        """
        super(TesseractDataServiceProvider, self).__init__(logger, log_level)
        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
        # This will validate and throw error if tesseract not configured properly
        tesseract_version = pytesseract.get_tesseract_version()
        self.logger.info("Tesseract version = %s", tesseract_version)

    def get_rows_cols(self, image_file_path: str,
                      token_type_value: int,
                      within_bbox: list = None,
                      file_data_list: list = None,
                      additional_info: dict = None,
                      config_params_dict: dict = None) -> dict:
        """Method to get rows and columns from an image.

        Args:
            image_file_path (str): Path to the image file.
            token_type_value (int): 1(WORD), 2(LINE), 3(PHRASE)
            within_bbox (list, optional): Bounding box within which to extract tokens. Defaults to None.
            file_data_list (list, optional): List of all file data. Each file data has the path to supporting document and page numbers, if applicable. Defaults to None.
            additional_info (dict, optional): Additional information for row and column extraction. Defaults to None.
            config_params_dict (dict, optional): Configuration parameters. Defaults to None.

        Returns:
            dict: Dictionary containing rows and columns.

        Example:
            >>> import logging
            >>> logging.disable(logging.CRITICAL)
            >>> provider = TesseractDataServiceProvider(r'C:\\MyProgramFiles\\Tesseract-OCR\\tesseract.exe')
            >>> input_pdf = os.path.abspath("./data/samples/infosys_q1-2022.pdf")
            >>> input_img = os.path.abspath("./data/samples/infosys_q1-2022.pdf_files/1.jpg")
            >>> result = provider.get_rows_cols(input_img, 1, file_data_list=[{"path": input_pdf, "pages": [1]}], config_params_dict={"ocr_tool_settings": {'tesseract': {'psm': '12'}}})
            >>> isinstance(result, dict)
            True
            >>> logging.disable(logging.NOTSET)
        """
        token_data = self.__get_tokens_from_ocr(image_file_path, token_type_value, within_bbox,
                                                file_data_list, additional_info, config_params_dict)
        return self.__get_hor_ver_line_position(token_data)

    def get_tokens(self, image_file_path: str,
                   token_type_value: int,
                   within_bbox: list = None,
                   file_data_list: list = None,
                   additional_info: dict = None,
                   config_params_dict: dict = None) -> list:
        """Method to get all tokens (word, phrase or line) and its bounding box as x, y, width and height from an image as a list of dictionary.
        Currently word token is only required.

        Args:
            image_file_path (str): Path to the image file.
            token_type_value (int): 1(WORD), 2(LINE), 3(PHRASE)
            within_bbox (list, optional): Bounding box within which to extract tokens. Defaults to None.
            file_data_list (list, optional): List of all file data. Each file data has the path to supporting document and page numbers, if applicable. Defaults to None.
            additional_info (dict, optional): Additional information for token extraction. Defaults to None.
            config_params_dict (dict, optional): Configuration parameters. Defaults to None.

        Returns:
            list: List of tokens with bounding boxes.

        Example:
            >>> import os
            >>> import logging
            >>> logging.disable(logging.CRITICAL)
            >>> assert 'TESSERACT_PATH' in os.environ
            >>> tesseract_path = os.getenv('TESSERACT_PATH')
            >>> provider = TesseractDataServiceProvider(tesseract_path)
            >>> input_pdf = os.path.abspath("./data/samples/infosys_q1-2022.pdf")
            >>> input_img = os.path.abspath("./data/samples/infosys_q1-2022.pdf_files/1.jpg")
            >>> result = provider.get_tokens(input_img, 1, file_data_list=[{"path": input_pdf, "pages": [1]}], config_params_dict={"ocr_tool_settings": {'tesseract': {'psm': '12'}}})
            >>> isinstance(result, list)
            True
            >>> logging.disable(logging.NOTSET)
        """
        return self.__get_tokens_from_ocr(image_file_path, token_type_value, within_bbox,
                                          file_data_list, additional_info, config_params_dict)

    def get_enhanced_tokens(self, token_data_list: list,
                            image_file_path: str = None,
                            within_bbox: list = None,
                            file_data_list: list = None) -> list:
        """Uses Tesseract to crop image based on token's bbox
        and extracted text to enhance the token_data_list.

        Args:
            token_data_list (list): List of token data with bounding boxes.
            image_file_path (str, optional): Path to the image file. Defaults to None.
            within_bbox (list, optional): Bounding box within which to extract tokens. Defaults to None.
            file_data_list (list, optional): List of file data. Each file data has the path to supporting document and page numbers, if applicable. Defaults to None.

        Returns:
            list: Enhanced token data list.

        Example:
            >>> import os
            >>> import logging
            >>> logging.disable(logging.CRITICAL)
            >>> assert 'TESSERACT_PATH' in os.environ
            >>> tesseract_path = os.getenv('TESSERACT_PATH')
            >>> provider = TesseractDataServiceProvider(tesseract_path)
            >>> token_data_list = [{'bbox': [0, 0, 100, 100], 'text': ''}]
            >>> image_file_path = './data/samples/infosys_q1-2022.pdf_files/1.jpg'
            >>> result = provider.get_enhanced_tokens(token_data_list, image_file_path)
            >>> isinstance(result, list)
            True
            >>> logging.disable(logging.NOTSET)
        """
        def __convert_to_file_safe_text(raw_text):
            # If text is containing only ASCII chars, then return as-is
            if all(ord(c) < 128 for c in raw_text):
                return raw_text
            allowed_additional_characters = (' ', '.', '_')
            return "".join(c for c in raw_text if c.isalnum() or c in allowed_additional_characters).rstrip()
        cordinates_dict = {}
        bounding_box_image = cv2.imread(image_file_path)
        for idx, item in enumerate(token_data_list):
            try:
                startx, starty, endx, endy = item['bbox']
                cordinate_key = str(starty) + str(endx) + str(endy)
                if cordinate_key in cordinates_dict:
                    item['text'] = ""
                else:
                    cordinates_dict[cordinate_key] = startx
                    width = endx - startx
                    height = endy - starty
                    cropped_image = bounding_box_image[
                        starty-0: starty + height + 0,
                        startx - 0: startx + width + 0]
                    outputImage = cv2.copyMakeBorder(
                        cropped_image,
                        10, 10, 10, 10, cv2.BORDER_CONSTANT, value=[255, 255, 255]
                    )
                    cropped_dir = str(PurePath(
                        image_file_path).parent) + "/cropped/"
                    if not os.path.exists(cropped_dir):
                        os.makedirs(cropped_dir)
                    # This method used for filename but not useful when text containing "|" character.
                    # because of that filecreation failing.
                    # file_name_prefix = __convert_to_file_safe_text(
                    #     item['text'])
                    cropped_image_path = f"{cropped_dir}/{idx}_[{startx},{starty},{height},{width}].jpg"
                    cv2.imwrite(cropped_image_path, outputImage)
                    try:
                        newvalue = pytesseract.image_to_string(
                            cropped_image_path)
                        if newvalue != "":
                            item['text'] = newvalue
                    except Exception as e:
                        self.logger.warning(e)
            except Exception as e:
                self.logger.error(e)
        return token_data_list

    def __get_tokens_from_ocr(self, image_file_path: str,
                              token_type_value: int,
                              within_bbox: list = None,
                              file_data_list: list = None,
                              additional_info: dict = None,
                              config_params_dict: dict = None):
        img_ocr_file_list, provided_ocr_file_psm = None, None
        if file_data_list:
            img_ocr_file_list = [file_data for file_data in file_data_list if file_data["path"] and str(
                file_data["path"]).lower().endswith(".hocr")]
        if additional_info:
            provided_ocr_file_psm = additional_info.get(
                'tesseract', {}).get('psm', None)
        expected_ocr_file_psm = config_params_dict.get(
            'tesseract', {}).get('psm', None)
        if img_ocr_file_list and (expected_ocr_file_psm is None or
                                  (provided_ocr_file_psm and
                                   str(provided_ocr_file_psm) == str(expected_ocr_file_psm))):
            img_ocr_file = img_ocr_file_list[0]['path']
        else:
            # set within_bbox default to None, when newly generating ocr as, img cropped from parent.
            within_bbox = None
            img_ocr_file = self.__generate_ocr_file(
                image_file_path, config_params_dict)

        ocr_file_obj = open(img_ocr_file, 'r', encoding="utf8")
        soup = bs4.BeautifulSoup(ocr_file_obj.read(), features='xml')
        token_structure_list = []
        title = soup.find("div", {"class": "ocr_page"})[
            'title'].split(";")[1]
        ori_page_bbox = title.replace(" bbox ", "").split()
        # 1-word, 2-line, 3-phrase
        if token_type_value == 1:
            ocr_class_list = soup.findAll("span", {"class": "ocrx_word"})
        elif token_type_value == 2:
            ocr_lines = soup.findAll("span", {"class": "ocr_line"})
            ocr_header = soup.findAll("span", {"class": "ocr_header"})
            ocr_class_list = ocr_lines+ocr_header

        for line in ocr_class_list:
            line_text = line.text.replace("\n", " ").strip()
            title = line['title']
            l, t, r, b = map(int, title[5:title.find(";")].split())
            should_append = True
            if within_bbox:
                should_append = False
                pl, pt, pw, ph = within_bbox
                if (pl <= l <= pl+pw) and (pt <= t <= pt+ph) \
                        and (pl <= r <= pl+pw) and (pt <= b <= pt+ph):
                    # c_r, c_b = pl+pw, pt+ph
                    scale_to_img = max(
                        pw/int(ori_page_bbox[2]), ph/int(ori_page_bbox[3]))
                    scale_to_img = round(scale_to_img, 2)
                    l, t, r, b = [round(x*scale_to_img) for x in [l, t, r, b]]
                    should_append = True
            if should_append:
                token_structure_list.append(
                    {'text': line_text, 'bbox': [l, t, r, b]})
        return token_structure_list

    def __generate_ocr_file(self, image_file_path: str, additional_info: dict):
        tesseract_obj = additional_info.get('tesseract', {})
        psm = str(tesseract_obj.get('psm', '6'))
        config = '--psm ' + psm
        hocr_data = pytesseract.image_to_pdf_or_hocr(
            image_file_path, extension='hocr',
            config=config)
        hocr_path = f"{str(PurePath(image_file_path).parent)}/{str(PurePath(image_file_path).stem)}_psm={psm}.hocr"
        with open(hocr_path, "w+b") as outfile:
            outfile.write(hocr_data)
        return hocr_path

    def __get_hor_ver_line_position(self, phrase_token_data) -> dict:
        hocr_predicted_row_pos, hocr_predicted_col_pos = [], []
        prev_col = -1
        line_phrase_col = []
        for x in phrase_token_data:
            bbox = x['bbox']
            if bbox[0] < prev_col:
                if len(line_phrase_col) > len(hocr_predicted_col_pos):
                    hocr_predicted_col_pos = line_phrase_col

                l = min([col_data['bbox'][0] for col_data in line_phrase_col])
                t = min([col_data['bbox'][1] for col_data in line_phrase_col])
                r = max([col_data['bbox'][2] for col_data in line_phrase_col])
                b = max([col_data['bbox'][3] for col_data in line_phrase_col])
                hocr_predicted_row_pos.append({'bbox': [l, t, r, b]})
                line_phrase_col = []
                prev_col = -1
            line_phrase_col.append({'bbox': bbox})
            prev_col = bbox[2]

        return {'rows': hocr_predicted_row_pos, 'cols': hocr_predicted_col_pos}

# ===============================================================================================================#
# Copyright 2021 Infosys Ltd.                                                                                   #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

"""
TextExtractor
~~~
This script accepts an image with text and returns the text in an array with each element as each line
of the image

"""
import logging
import sys
import cv2
from os import path
import numpy as np
from infy_field_extractor.internal.extractor_helper import ExtractorHelper
from infy_field_extractor.internal.constants import Constants
from infy_field_extractor.interface.data_service_provider_interface import DataServiceProviderInterface, FILE_DATA_LIST


TEXT_FIELD_DATA_LIST = [
    {
        "field_key": [""],
        "field_key_match": {"method": "normal", "similarityScore": 1},
        "field_value_bbox": [],
        "field_value_pos": "left"
    }
]

CONFIG_PARAMS_DICT = {
    'field_value_pos': "right",
    "page": 1,
    "eliminate_list": [],
    "scaling_factor": {
        'hor': 1,
        'ver': 1
    },
    "within_bbox": [],
    "multiline_sorting_left_to_right": True
}

TEXT_EXTRACT_ALL_FIELD_OUTPUT = {
    'fields': {
        '<field_key>': '<field_value>',
    },
    'error': ''
}

TEXT_EXTRACT_CUSTOM_FIELD_OUTPUT = {
    'fields': [
        {
            'field_key': [],
            'field_value': '',
            'field_value_bbox': []
        }
    ],
    'error': None
}


class TextExtractor():

    def __init__(self, get_text_provider: DataServiceProviderInterface,
                 search_text_provider: DataServiceProviderInterface,
                 temp_folderpath: str, logger: logging.Logger = None,
                 debug_mode_check: bool = False):
        """Creates an instance of Text Extractor.

        Args:
            get_text_provider (DataServiceProviderInterface): Provider to get text either word,
                line or phrases
            search_text_provider (DataServiceProviderInterface): Provider to search the text in the image.
            temp_folderpath (str): Path to temp folder.
            logger (logging.Logger, optional): Logger object. Defaults to None.
            debug_mode_check (bool, optional): To get debug info while using the API. Defaults to False.

        Raises:
            Exception: Valid temp_folderpath is required.
        """
        self.get_text_provider = get_text_provider
        self.search_text_provider = search_text_provider
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

        self.debug_mode_check = debug_mode_check
        self.temp_folderpath = temp_folderpath

        if(path.exists(temp_folderpath) is False):
            self.logger.error("property temp_folderpath not found")
            raise Exception("property temp_folderpath not found")

    def extract_all_fields(self, image_path: str,
                           config_params_dict: CONFIG_PARAMS_DICT = None,
                           file_data_list: FILE_DATA_LIST = None) -> TEXT_EXTRACT_ALL_FIELD_OUTPUT:
        """API to extract text from an image automatically as key-value pair.

        Args:
            image_path (str): Path to the image
            config_params_dict (CONFIG_PARAMS_DICT, optional): Additional info for min and max
                radiobutton radius to text height ratio, position of state w.r.t key,
                within_bbox(x,y,w,h), eliminate_list, scaling_factor and page number.
                Defaults to CONFIG_PARAMS_DICT.
            file_data_list (FILE_DATA_LIST, optional): List of all file datas. Each file data
                has the path to supporting document and page numbers, if applicable. Defaults to None.

        Raises:
            AttributeError: field_value_pos can only be right or bottom

        Returns:
            dict: Dict of extracted info.
        """
        if config_params_dict:
            invalid_keys = ExtractorHelper.get_invalid_keys(
                CONFIG_PARAMS_DICT, config_params_dict)
            if len(invalid_keys) > 0:
                raise Exception(f"Invalid keys fcound: {invalid_keys}. ")
            config_params_dict = ExtractorHelper.get_updated_config_dict(
                CONFIG_PARAMS_DICT, config_params_dict)
        else:
            config_params_dict = CONFIG_PARAMS_DICT
        within_bbox = config_params_dict['within_bbox']
        scaling_factor = config_params_dict['scaling_factor']
        eliminate_list = config_params_dict['eliminate_list']
        within_bbox = ExtractorHelper.get_updated_within_box(
            within_bbox, scaling_factor)
        eliminate_list = ExtractorHelper.get_updated_text_bbox(
            eliminate_list, scaling_factor)

        output, all_error = {}, []
        if(config_params_dict.get('field_value_pos') != "right" and
                config_params_dict.get('field_value_pos') != "bottom"):
            raise AttributeError("field_value_pos can only be right or bottom")

        # read the image from imagepath
        img, _, img_name = ExtractorHelper.read_image(
            image_path, self.logger, self.temp_folderpath, within_bbox)

        # to check the dpi and give appropriate warning, if any
        ExtractorHelper.check_image_dpi(
            image_path, self.logger)

        additional_info = {"scaling_factor": scaling_factor,
                           'pages': [config_params_dict["page"]]
                           }

        # get the ocr_words
        bboxes_text = self.get_text_provider.get_tokens(
            1, img, within_bbox, file_data_list, additional_info, self.temp_folderpath)
        # bboxes_text, all_error = ExtractorHelper.get_ocr_text_bbox(
        #     ocr_parser_object, all_error, within_bbox, config_params_dict["page"], scaling_factor)
        if len(bboxes_text) == 0:
            all_error.append("No words found in the region")
        text_dict = None
        if(config_params_dict['field_value_pos'] == "right"):
            if(all_error == []):
                text_dict = self.__extract_from_inline_text(
                    img, file_data_list,
                    bboxes_text, within_bbox, additional_info
                )
                all_error = None
        elif(config_params_dict['field_value_pos'] == "bottom"):
            if(all_error == []):
                text_dict = self.__extract_from_box_seperated_regions(
                    img, img_name, file_data_list,
                    within_bbox, bboxes_text,
                    additional_info,
                    config_params_dict
                )
            all_error = None

        output['fields'], output['error'] = text_dict, all_error
        return output

    def extract_custom_fields(self, image_path: str,
                              text_field_data_list: TEXT_FIELD_DATA_LIST,
                              config_params_dict: CONFIG_PARAMS_DICT = None,
                              file_data_list: FILE_DATA_LIST = None) -> TEXT_EXTRACT_CUSTOM_FIELD_OUTPUT:
        """API to extract text value for respective given key words or value within given bounding boxes.

        Args:
            image_path (str): Path to the image
            text_field_data_list (list): Info for field_key and its match method,
                and either field_value_pos w.r.t key or field_value_bbox.
                Defaults to [TEXT_FIELD_DATA_DICT].
            config_params_dict (dict, optional): Additional info for position of value w.r.t key and
                within_bbox(x,y,w,h), eliminate_list, within_bbox(x,y,w,h), eliminate_list, scaling_factor and page number.
                Defaults to CONFIG_PARAMS_DICT.
            file_data_list (list, optional): List of all file datas. Each file data has the path to
                supporting document and page numbers, if applicable. Defaults to None.

        Raises:
            AttributeError: Both field_value_pos and field_value_bbox in text_field_data_list              should not be given together.

        Returns:
            dict: Dict of extracted info.
        """
        if config_params_dict:
            invalid_keys = ExtractorHelper.get_invalid_keys(
                CONFIG_PARAMS_DICT, config_params_dict)
            if len(invalid_keys) > 0:
                raise Exception(f"Invalid keys fcound: {invalid_keys}. ")
            config_params_dict = ExtractorHelper.get_updated_config_dict(
                CONFIG_PARAMS_DICT, config_params_dict)
        else:
            config_params_dict = CONFIG_PARAMS_DICT
        within_bbox = config_params_dict['within_bbox']
        scaling_factor = config_params_dict['scaling_factor']
        eliminate_list = config_params_dict['eliminate_list']
        within_bbox = ExtractorHelper.get_updated_within_box(
            within_bbox, scaling_factor)
        eliminate_list = ExtractorHelper.get_updated_text_bbox(
            eliminate_list, scaling_factor)

        # read the image from imagepath if available
        img = None
        if image_path:
            img, _, _ = ExtractorHelper.read_image(
                image_path, self.logger, self.temp_folderpath)

        text_field_data_list = [ExtractorHelper.get_updated_config_dict(
            TEXT_FIELD_DATA_LIST[0], text_field_data) for text_field_data in text_field_data_list]

        field_value_bbox_count, field_key_count = 0, 0
        for field_data in text_field_data_list:
            if len(field_data["field_value_bbox"]) > 0:
                field_value_bbox_count += 1
            if len(field_data["field_key"]) > 0:
                field_key_count += 1

        additional_info = {"scaling_factor": scaling_factor,
                           'pages': [config_params_dict["page"]]}

        if(field_value_bbox_count == len(text_field_data_list) and within_bbox == []):
            return self.__extract_from_field_value_bboxes(
                img, file_data_list, text_field_data_list,
                eliminate_list, additional_info, config_params_dict)
        elif(field_value_bbox_count == 0 and field_key_count == len(text_field_data_list)):
            return self.__extract_from_keys(
                img, file_data_list, text_field_data_list, within_bbox,
                eliminate_list, additional_info)
        else:
            raise AttributeError(
                "Given keys in the attribute 'text_field_data_list' is incorrect")

    def __extract_from_inline_text(self,
                                   img, file_data_list, bboxes_text, region,
                                   additional_info):
        text_dict = {}
        _, width = img.shape
        text_h = bboxes_text[0].get("bbox")[Constants.BB_H]
        text_w = bboxes_text[0].get("bbox")[Constants.BB_W]
        boxes = []
        # filter empty text in bboxes_text
        filter_boxes = []
        for t in bboxes_text:
            if(t.get("text") == ""):
                filter_boxes.append(t)
        bboxes_text = [x for x in bboxes_text if x not in filter_boxes]

        # find contours
        _, threshold = cv2.threshold(img, 170, 255, cv2.THRESH_BINARY_INV)
        contours, _ = cv2.findContours(
            threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        # find boxes
        for i in range(0, len(contours)):
            cnt = contours[i]
            threshold = 0.04
            epsilon = threshold*cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, epsilon, True)
            _, _, w, h = cv2.boundingRect(cnt)
            if (len(approx) == Constants.RECT_EDGES and w > h and h >= text_h):
                xs, ys, ws, hs = cv2.boundingRect(cnt)
                boxes.append([xs, ys, ws, hs])
        if(region != []):
            for b in boxes:
                b[Constants.BB_X] += region[Constants.BB_X]
                b[Constants.BB_Y] += region[Constants.BB_Y]

        if(len(boxes) > 0):
            # extracting text using boxes
            # removing duplicate boxes
            res = []
            [res.append(x) for x in boxes if x not in res]
            boxes = res
            MY_CONS_1 = 9
            # filter extra checkboxes where two checkboxes is obtained for 1 checkbox because two rectangle contours
            # are detected for a single checkbox because of its thickness
            filter_boxes = []
            for i in range(len(boxes)-1):
                c1 = boxes[i]
                c2 = boxes[i+1]
                # filters the outer rectangle by comparing if both x and y coordinate of the outer rectangle
                # is in the range of the x, y coordinate of inner v and x-width/9, y-width/9 of the
                # inner rectangle
                if(c2[Constants.BB_X] >= c1[Constants.BB_X] >= (c2[Constants.BB_X] - c1[Constants.BB_W]//MY_CONS_1) and (c2[Constants.BB_Y] >= c1[Constants.BB_Y] >= (c2[Constants.BB_Y] - c1[Constants.BB_W]//MY_CONS_1))):
                    filter_boxes.append(c1)
            boxes = [x for x in boxes if x not in filter_boxes]
            boxes.sort(key=lambda x: (x[Constants.BB_X]))
            Y_SPACE = 2
            # getting the final result
            for i in range(len(boxes)):
                b = boxes[i]
                key_text = ""
                value_text = ""
                # if more than 1 box for value present in a line then inline_box = True, by default False
                inline_box = False
                if(i > 0):
                    for j in range(len(boxes)):
                        b_j = boxes[j]
                        # if more than 1 box found in the same line by checking the y-coordinate of the boxes
                        # are almost equal and x-coordinate of b_j is always greater than x-coordinate of b,
                        # then inline_box = True
                        if(b_j[Constants.BB_X] <= b[Constants.BB_X] and (b[Constants.BB_Y]-text_h//Y_SPACE) <= b_j[Constants.BB_Y] <= (b[Constants.BB_Y]+text_h//Y_SPACE) and b_j != b):
                            inline_box = True
                            b_prev = b_j
                for t in bboxes_text:
                    t_x = t.get("bbox")[Constants.BB_X]
                    t_y = t.get("bbox")[Constants.BB_Y]
                    # gets all the words as value_text present inside the box
                    if(b[Constants.BB_X] <= t_x <= (b[Constants.BB_X]+b[Constants.BB_W]) and b[Constants.BB_Y] <= t_y <= (b[Constants.BB_Y]+b[Constants.BB_H])):
                        value_text = value_text + t.get("text") + " "
                    # gets all the key_text before the box but after the previous box
                    elif(inline_box is True):
                        if(b[Constants.BB_X] >= t_x >= (b_prev[Constants.BB_X]+b_prev[Constants.BB_W]) and (b[Constants.BB_Y]-text_h//Y_SPACE) <= t_y <= (b[Constants.BB_Y]+b[Constants.BB_H]+text_h//Y_SPACE)):
                            key_text = key_text + t.get("text") + " "
                    # gets all the key_text before the box
                    elif(b[Constants.BB_X] >= t_x and (b[Constants.BB_Y]-text_h//Y_SPACE) <= t_y <= (b[Constants.BB_Y]+b[Constants.BB_H]+text_h//Y_SPACE)):
                        key_text = key_text + t.get("text") + " "

                text_dict[key_text] = value_text

        else:
            # if boxes not found, it searches for line to extract text
            L_STARTX = 0
            L_STARTY = 1
            L_ENDX = 2
            L_ENDY = 3
            HORIZONTAL_BUFFER = 3
            edges = cv2.Canny(img, 50, 120)
            minLineLength = text_w
            maxLineGap = 4*text_h
            lines = cv2.HoughLinesP(
                edges, 1, np.pi/180, 100, minLineLength, maxLineGap)
            if(lines is not None):
                # if lines are found it starts extracting using lines
                lines = lines.tolist()
                lines_list = []
                for i in lines:
                    lines_list.append(i[0])
                if(region != []):
                    for l in lines_list:
                        l[Constants.BB_X] += region[Constants.BB_X]
                        l[Constants.BB_Y] += region[Constants.BB_Y]

                # filter vertical lines , if any
                filter_lines = []
                for i in range(len(lines_list)):
                    c1 = lines_list[i]
                    if(abs(c1[L_STARTY]-c1[L_ENDY]) >= HORIZONTAL_BUFFER):
                        filter_lines.append(c1)
                lines_list = [x for x in lines_list if x not in filter_lines]

                # filter extra lines where two lines is obtained for 1 line because two line contours
                # are detected for a single line because of its thickness
                filter_lines = []
                MAX_THICKNESS = text_h//4
                for i in range(len(lines_list)-1):
                    c1 = lines_list[i]
                    c2 = lines_list[i+1]
                    if(abs(c1[L_STARTX]-c2[L_STARTX]) <= MAX_THICKNESS):
                        filter_lines.append(c2)
                lines_list = [x for x in lines_list if x not in filter_lines]

                # get text from the line
                for i in range(len(lines_list)):
                    # key and value
                    l = lines_list[i]
                    key_text = ""
                    value_text = ""
                    Y_SPACE = 2
                    # if more than 1 line for value present in that particular line then inline_box = True, by default False
                    inline_box = False
                    if(i > 0):
                        for j in range(len(boxes)):
                            l_j = lines_list[j]
                            # if more than 1 line found in the same line by checking the y-coordinate of the boxes
                            # are almost equal and x-coordinate of l_j is always greater than x-coordinate of l,
                            # then inline_box = True
                            if(l_j[L_STARTX] <= l[L_STARTX] and (l[L_STARTY]-text_h//Y_SPACE) <= l_j[L_STARTY] <= (l[L_STARTY]+text_h//Y_SPACE) and l_j != l):
                                inline_box = True
                                l_prev = l_j
                    for b in bboxes_text:
                        t_x = b.get("bbox")[Constants.BB_X]
                        t_y = b.get("bbox")[Constants.BB_Y]
                        # gets all the words as value_text present above the line
                        if(t_x >= l[L_STARTX] and (l[L_STARTY]-Y_SPACE*text_h) <= t_y <= l[L_STARTY]):
                            value_text = value_text + b.get("text") + " "
                        # gets all the key_text before the line but after the previous line as more than one key present
                        elif(inline_box is True):
                            if(l[L_STARTX] >= t_x >= (l_prev[L_STARTX]+l_prev[L_ENDX]) and (l[L_STARTY]-2*text_h) <= t_y <= l[L_STARTY]):
                                key_text = key_text + b.get("text") + " "
                        # gets all the key_text before the line
                        elif(t_x <= l[L_STARTX] and (l[L_STARTY]-Y_SPACE*text_h) <= t_y <= l[L_STARTY]):
                            key_text = key_text + b.get("text") + " "
                    text_dict[key_text] = value_text

        # if no boxes or lines found, extracts text using space between key and value
        if(text_dict == {}):
            self.logger.info(
                "No line or boxes found, extracting text by determing space between key and value")
            # get phrases from words using extractor_helper module
            # phrases_dictList, _ = ExtractorHelper.get_ocr_text_bbox(
            #     ocr_parser_object, ocr_word_list=bboxes_text, scaling_factor=scaling_factor, token="PHRASE", page=config_params_dict["page"])
            additional_info['word_bbox_list'] = bboxes_text
            phrases_dictList = self.get_text_provider.get_tokens(
                3, img, region, file_data_list, additional_info, self.temp_folderpath)
            # dividing each line
            bboxes_line_list = self.__get_each_line_lists(
                phrases_dictList, width)
            bboxes_line_list.sort(key=lambda x: x[Constants.BB_Y])

            # getting key value

            # keyvalue_distance is first assumed to be 4 times the height of the word
            kv_dist = 4 * \
                phrases_dictList[Constants.BB_X].get("bbox")[Constants.BB_H]
            # creates a list of all the key-value distance
            kv_dList = [kv_dist]

            # for each line in the image get all the key and value
            for bbox_line in bboxes_line_list:
                y_l = bbox_line[Constants.BB_Y]
                h_l = bbox_line[Constants.BB_H]
                texts_line = []
                # gets all the phrases present in that line whose y-coordinate is present in the bbox of the line
                for t in phrases_dictList:
                    if(y_l <= int(t.get("bbox")[Constants.BB_Y]) <= (y_l+h_l)):
                        texts_line.append(t)

                texts_line.sort(key=lambda x: (x.get("bbox")[Constants.BB_X]))
                done_list = []
                # if the line contains only 1 phrase then True, by default False
                flag2 = False
                if(len(texts_line) == 1):
                    text_dict[texts_line[Constants.BB_X].get("text")] = ""
                    flag2 = True
                for i in range(len(texts_line)-1):
                    flag3 = False
                    if(texts_line[i] not in done_list):
                        # for tracking key_text
                        flag = True
                        # for tracking last key_text in case of inline key-value pairs
                        flag3 = True
                        key_text = texts_line[i].get("text")
                        value_text = ""
                        t = texts_line[i].get("bbox")
                        # bbox of the next text
                        t_next = texts_line[i+1].get("bbox")
                        # if end pos of the current phrase and start pos of next phrase distance is less
                        # than kv, then next phrase is the value of current phrase
                        if(t[Constants.BB_X]+t[Constants.BB_W] <= t_next[Constants.BB_X] <= t[Constants.BB_X]+t[Constants.BB_W]+kv_dist):
                            value_text = texts_line[i+1].get("text")
                            done_list.append(texts_line[i+1])
                    # adds key_text and value_text to the dictionary
                    if(flag is True):
                        if(value_text != ""):
                            # gets the distance between key and value and stores in the list and also
                            # updates the kv_dist
                            kv_dist = texts_line[i+1].get("bbox")[Constants.BB_X] - texts_line[i].get("bbox")[
                                0]-texts_line[i].get("bbox")[Constants.BB_W]
                            kv_dList.append(kv_dist)
                            kv_dist = sum(kv_dList)//len(kv_dList)
                        text_dict[key_text] = value_text
                        done_list.append(texts_line[i])
                        flag = False
                # in case of inline key value pair, considers for the last key which has no value
                if(flag2 is False and flag3 is True and texts_line[i+1] not in done_list):
                    text_dict[texts_line[i+1].get("text")] = ""

        return text_dict

    def __extract_from_box_seperated_regions(
            self, img, img_name, file_data_list, region,
            bboxes_text, additional_info, config_params_dict):
        """
        extracts key and value by dividing the image into regions using horizonatal and vertical lines
        """
        text_dict = {}
        _, width = img.shape
        # filter empty lines
        filter_list = []
        for b in bboxes_text:
            if(b.get("text") == ''):
                filter_list.append(b)
        bboxes_text = [x for x in bboxes_text if x not in filter_list]
        height_sum = 0
        for b in bboxes_text:
            height_sum += b.get("bbox")[Constants.BB_H]
        word_height = height_sum//len(bboxes_text)
        word_width = bboxes_text[Constants.BB_X].get("bbox")[Constants.BB_W]

        # getting box regions
        bboxes_region = ExtractorHelper.get_box_region(
            img, img_name, self.debug_mode_check, self.temp_folderpath, 3*word_height, word_width)
        if(region != []):
            for b in bboxes_region:
                b[Constants.BB_X] += region[Constants.BB_X]
                b[Constants.BB_Y] += region[Constants.BB_Y]

        # eliminate regions using eliminate list
        eliminate_list = config_params_dict['eliminate_list']
        if(eliminate_list is not []):
            filter_list = []
            if(region != []):
                for b in bboxes_region:
                    for dList in eliminate_list:
                        x_d = dList.get("bbox")[Constants.BB_X]
                        y_d = dList.get("bbox")[Constants.BB_Y]
                        if(b[Constants.BB_X] <= x_d <= (b[Constants.BB_X]+b[Constants.BB_W]) and b[Constants.BB_Y] <= y_d <= (b[Constants.BB_Y]+b[Constants.BB_H])):
                            filter_list.append(b)
                            break
            else:
                for b in bboxes_region:
                    for dList in eliminate_list:
                        x_d = dList.get("bbox")[
                            Constants.BB_X] - region[Constants.BB_X]
                        y_d = dList.get("bbox")[
                            Constants.BB_Y] - region[Constants.BB_Y]
                        if(b[Constants.BB_X] <= x_d <= (b[Constants.BB_X]+b[Constants.BB_W]) and b[Constants.BB_Y] <= y_d <= (b[Constants.BB_Y]+b[Constants.BB_H])):
                            filter_list.append(b)
                            break
            bboxes_region = [x for x in bboxes_region if x not in filter_list]

        # final result
        for b in bboxes_region:
            region_words = []
            # get all the words in the box region
            for words in bboxes_text:
                x_p = words.get("bbox")[Constants.BB_X]
                y_p = words.get("bbox")[Constants.BB_Y]
                if(b[Constants.BB_X] <= x_p <= b[Constants.BB_X]+b[Constants.BB_W] and b[Constants.BB_Y] <= y_p <= b[Constants.BB_Y]+b[Constants.BB_H]):
                    region_words.append(words)
            # get all the phrases from words in the box region
            # region_phrases, _ = ExtractorHelper.get_ocr_text_bbox(
            #     ocr_parser_object, ocr_word_list=region_words, scaling_factor=scaling_factor, token="PHRASE", page=config_params_dict["page"])
            additional_info['word_bbox_list'] = region_words
            region_phrases = self.get_text_provider.get_tokens(
                3, img, [], file_data_list, additional_info, self.temp_folderpath)

            # get each lines bounding boxes for that region
            if(region_phrases == []):
                continue
            bboxes_line_list = self.__get_each_line_lists(
                region_phrases, width)

            bboxes_line_list.sort(key=lambda x: x[Constants.BB_Y])
            # tracks the line number in that box region
            line_count = 0
            key_text = ""
            value_text = ""
            # flag to assure that all the other lines will be value_text
            flag = False
            region_phrases.sort(key=lambda x: x.get("bbox")[Constants.BB_X])
            for line in bboxes_line_list:
                # if first line then always add to key_text
                if(line_count == 0):
                    for phrase in region_phrases:
                        prev_line = line
                        y_p = phrase.get("bbox")[Constants.BB_Y]
                        if(line[Constants.BB_Y] <= y_p <= (line[Constants.BB_Y]+line[Constants.BB_H])):
                            key_text = key_text + " " + phrase.get("text")
                else:
                    # if the space between the current line and prev line is less than half of the word_height
                    # then current line is also key_text
                    if(line[Constants.BB_Y]-prev_line[Constants.BB_Y]-prev_line[Constants.BB_H] <= word_height//2 and flag is False):
                        # get all the phrases present in that line as key_text
                        for phrase in region_phrases:
                            prev_line = line
                            y_p = phrase.get("bbox")[Constants.BB_Y]
                            if(line[Constants.BB_Y] <= y_p <= (line[Constants.BB_Y]+line[Constants.BB_H])):
                                key_text = key_text + " " + phrase.get("text")
                    # else the current line is value text
                    else:
                        flag = True
                        # get all the phrases present in that line as value_text
                        for phrase in region_phrases:
                            y_p = phrase.get("bbox")[Constants.BB_Y]
                            if(line[Constants.BB_Y] <= y_p <= (line[Constants.BB_Y]+line[Constants.BB_H])):
                                value_text = value_text + \
                                    " " + phrase.get("text")
                line_count += 1
            text_dict[key_text] = value_text

        return text_dict

    def __extract_from_field_value_bboxes(
            self, img, file_data_list, text_field_data_list,
            eliminate_list, additional_info, config_params_dict):

        result, output = [], {}

        for field_data in text_field_data_list:
            res = {}
            if "field_key" in field_data.keys():
                res["field_key"] = field_data["field_key"]
            res["field_value_bbox"] = field_data["field_value_bbox"]
            bboxes_text = self.get_text_provider.get_tokens(
                1, img, field_data["field_value_bbox"],
                file_data_list, additional_info, self.temp_folderpath)

            if(bboxes_text == []):
                res["field_value"] = ""
            elif len(bboxes_text) != 1:
                bboxes_text = [
                    x for x in bboxes_text if x not in eliminate_list]
                bboxes_text = ExtractorHelper.order_the_text(
                    config_params_dict["multiline_sorting_left_to_right"], bboxes_text)
                bboxes_line_list = self.__get_each_line_lists(
                    bboxes_text, res['field_value_bbox'][0]+res['field_value_bbox'][2])
                bboxes_line_list.sort(key=lambda x: (x[Constants.BB_Y]))
                text = ""
                words_done = []
                for line in bboxes_line_list:
                    for bbox_text in bboxes_text:
                        if line[Constants.BB_Y] <= bbox_text["bbox"][Constants.BB_Y] <= line[Constants.BB_Y]+line[Constants.BB_H] and \
                                bbox_text not in words_done:
                            words_done.append(bbox_text)
                            text += bbox_text["text"] + " "
                    text = text.strip() + "\n"
                res["field_value"] = text.strip()

                if 'id' in words_done[0]:
                    conf_list = [float(w['conf']) for w in words_done]
                    conf_avg = -1
                    if len(conf_list) > 0:
                        conf_avg = round(sum(conf_list)/len(conf_list), 2)

                    res["field_value_confidence_pct"] = conf_avg
                else:
                    res["field_value_confidence_pct"] = 100
            else:
                res["field_value"] = bboxes_text[0]['text'].strip()
                if 'id' in bboxes_text[0]:
                    res["field_value_confidence_pct"] = float(bboxes_text[0].get(
                        'conf'))

                else:
                    res["field_value_confidence_pct"] = 100

            result.append(res)
        output['fields'], output['error'] = result, None
        return output

    def __extract_from_keys(self, img, file_data_list, text_field_data_list, within_bbox, eliminate_list, additional_info):
        output = {}
        bboxes_text = self.get_text_provider.get_tokens(
            1, img, within_bbox,
            file_data_list, additional_info, self.temp_folderpath)
        bboxes_text = [x for x in bboxes_text if x not in eliminate_list]
        additional_info['word_bbox_list'] = bboxes_text
        phrases_dictList = self.get_text_provider.get_tokens(
            3, img, [], file_data_list, additional_info, self.temp_folderpath)
        if(within_bbox != []):
            region_phrases = []
            for phrase in phrases_dictList:
                c = phrase.get("bbox")
                if (within_bbox[Constants.BB_X] <= c[Constants.BB_X] <= within_bbox[Constants.BB_X]+within_bbox[Constants.BB_W] and
                        within_bbox[Constants.BB_Y] <= c[Constants.BB_Y] <= within_bbox[Constants.BB_Y]+within_bbox[Constants.BB_H]):
                    region_phrases.append(phrase)
            phrases_dictList = [
                x for x in phrases_dictList if x in region_phrases]
        phrase_bbox = []
        for phrase in phrases_dictList:
            phrase_bbox.append(phrase.get("bbox"))
        if(len(phrase_bbox) == 0):
            raise Exception("No phrases found within the given bbox")

        result = []
        for field_data in text_field_data_list:
            res = {}

            response = self.search_text_provider.get_bbox_for(
                img, field_data.get("field_key"),
                field_data.get("field_key_match"),
                file_data_list, additional_info, self.temp_folderpath)
            key_bbox, error = response['regions'], response['error']
            if(key_bbox != [] and len(key_bbox) > 1):
                if(within_bbox != []):
                    remove_key_bbox = []
                    for i in range(len(key_bbox)):
                        bbox = key_bbox[i]['regionBBox'][0]['bbox']
                        if(within_bbox[Constants.BB_X] <= bbox[Constants.BB_X] <= (within_bbox[Constants.BB_X]+within_bbox[Constants.BB_W]) and within_bbox[Constants.BB_Y] <= bbox[Constants.BB_Y] <= (within_bbox[Constants.BB_Y]+within_bbox[Constants.BB_H])):
                            pass
                        else:
                            remove_key_bbox.append(key_bbox[i])
                    key_bbox = [
                        x for x in key_bbox if x not in remove_key_bbox]
                if(key_bbox != [] and len(key_bbox) > 1):
                    error = "More than one key found"
                elif(key_bbox == []):
                    error = "Key: '"+field_data.get("field_key")+"' not found"
            res["field_key"] = field_data.get("field_key")
            if(error is None):
                closest_phrase = ExtractorHelper.get_closest_fieldbox(
                    phrase_bbox, field_data.get("field_value_pos"), key_bbox[0]['regionBBox'][0]['bbox'])
                for phrase in phrases_dictList:
                    if(phrase.get("bbox") == closest_phrase):
                        value = phrase.get("text")

                        if 'words' in phrase:
                            words_list = phrase.get("words")
                            conf_list = [float(w['conf']) for w in words_list]
                            conf_avg = -1
                            if len(conf_list) > 0:
                                conf_avg = round(
                                    sum(conf_list)/len(conf_list), 2)
                        else:
                            conf_avg = 100

                        break
                res["field_value"] = value
                res["field_value_confidence_pct"] = conf_avg
            else:
                res["field_value"] = None
                res["field_value_confidence_pct"] = -1
            res["error"] = error
            result.append(res)
        output['fields'], output['error'] = result, None
        return output

    def __get_each_line_lists(self, ocr_dictList, image_width):
        # dividing each line
        Y_SCALE = 4
        width = image_width
        c = ocr_dictList[Constants.BB_X].get("bbox")
        # appends the first line in bboxes_line_list
        bboxes_line_list = [[0, c[Constants.BB_Y]-c[Constants.BB_H]//Y_SCALE,
                             width, c[Constants.BB_H]+c[Constants.BB_H]//Y_SCALE]]
        # list to add a new line
        temp_list = []
        # to track the count of the number of lines in bboxes_line_list
        count = 0
        # to track if any new word found which is not present in any bboxes_line_list
        flag = False
        for word in ocr_dictList:
            f = word.get("bbox")
            for i in bboxes_line_list:
                count += 1
                # if words already there in the bboxes_list_line then set flag as True and moves to the next line
                if(i[Constants.BB_Y] <= f[Constants.BB_Y] <= (i[Constants.BB_Y]+i[Constants.BB_H])):
                    flag = True
                elif(flag is False and count == len(bboxes_line_list)):
                    temp_list.append(
                        [0, f[Constants.BB_Y]-f[Constants.BB_H]//Y_SCALE, width, f[Constants.BB_H]+f[Constants.BB_H]//Y_SCALE])
            bboxes_line_list = bboxes_line_list + temp_list
            temp_list = []
            flag = False
            count = 0
        return bboxes_line_list

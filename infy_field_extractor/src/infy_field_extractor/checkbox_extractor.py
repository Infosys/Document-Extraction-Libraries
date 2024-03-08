# ===============================================================================================================#
# Copyright 2021 Infosys Ltd.                                                                                   #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

"""
CheckboxExtractor
~~~~~
This script accepts an image with checkboxes and the text and returns True if the button is checked
and False if the button is unchecked
It also returns a list of dictionary whch contains the text used as the key in checkboxes
 and its corresponding bounding box region


"""
import os
from os import path
import logging
import sys
import numpy as np
import cv2
from infy_field_extractor.internal.common_utils import CommonUtils
from infy_field_extractor.internal.extractor_helper import ExtractorHelper
from infy_field_extractor.internal.constants import Constants
from infy_field_extractor.interface.data_service_provider_interface import DataServiceProviderInterface, FILE_DATA_LIST


CHECKBOX_FIELD_DATA_LIST = [
    {
        "field_key": [""],
        "field_key_match": {"method": "normal", "similarityScore": 1},
        "field_state_pos": "left",
        "field_state_bbox": [],
        "field_state_bbox_square_only":True
    }
]

CONFIG_PARAMS_DICT = {
    'min_checkbox_text_scale': None,
    'max_checkbox_text_scale': None,
    'field_state_pos': None,
    'page': 1,
    "eliminate_list": [],
    "scaling_factor": {
        'hor': 1,
        'ver': 1
    },
    "within_bbox": [],
    "image_to_bw": False
}

CHECKBOX_EXTRACT_ALL_FIELD_OUTPUT = {
    'fields': {
        '<field_key>': '<field_state>',
    },
    'error': ''
}

CHECKBOX_EXTRACT_CUSTOM_FIELD_OUTPUT = {
    'fields': [
        {
            'field_key': [],
            'field_state': '',
            'field_state_bbox': []
        }
    ],
    'error': None
}


class CheckboxExtractor():

    def __init__(self, get_text_provider: DataServiceProviderInterface,
                 search_text_provider: DataServiceProviderInterface,
                 temp_folderpath: str, logger=None, debug_mode_check=False):
        """Creates an instance of Checkbox Extractor.

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

        self.debug_mode_check = debug_mode_check
        self.temp_folderpath = temp_folderpath
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

        if(path.exists(temp_folderpath) is False):
            self.logger.error("property temp_folderpath not found")
            raise Exception("property temp_folderpath not found")

    def extract_all_fields(self, image_path: str,
                           config_params_dict: CONFIG_PARAMS_DICT = None,
                           file_data_list: FILE_DATA_LIST = None) -> CHECKBOX_EXTRACT_ALL_FIELD_OUTPUT:
        """API to extract all checkboxes by contour detection automatically

        Args:
            image_path (str): Path to the image
            config_params_dict (CONFIG_PARAMS_DICT, optional): Additional info for min and
                max checkbox height to text height ratio, position of state w.r.t key,
                within_bbox(x,y,w,h), eliminate_list, scaling_factor and page number.
                Defaults to CONFIG_PARAMS_DICT.
            file_data_list (FILE_DATA_LIST, optional): List of all file datas. Each file data
                has the path to supporting document and page numbers, if applicable. Defaults to None.

        Raises:
            AttributeError: field_state_pos in config_params_dict should not be used,
                as feature is not implemented yet

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

        if(config_params_dict.get('field_state_pos') is not None):
            raise AttributeError(
                "Currently field_state_pos is not used")

        # Create request specific temp folder
        img_name = os.path.splitext(os.path.split(image_path)[1])[0]
        self.temp_folderpath = CommonUtils.make_dir_with_timestamp(
            self.temp_folderpath, img_name)

        # read the image from image_path
        crop_image, _, _ = ExtractorHelper.read_image(
            image_path, self.logger, self.temp_folderpath, within_bbox)
        full_image, full_image_path, _ = ExtractorHelper.read_image(
            image_path, self.logger, self.temp_folderpath)
        output = {}

        bboxes_text, checkboxes, all_error = self.__common(
            crop_image, full_image_path, file_data_list, within_bbox, config_params_dict, scaling_factor)
        bboxes_text = [x for x in bboxes_text if x not in eliminate_list]

        if(all_error != []):
            output["error"] = all_error
            output["fields"] = None
            output["fieldsList"] = None
        else:
            # calling extractor helper to extract checkboxes value and its text
            additional_info = {"scaling_factor": scaling_factor,
                               'pages': [config_params_dict["page"]]}
            result, done_fields_dList = ExtractorHelper.extract_with_text_coordinates(
                full_image, bboxes_text, self.get_text_provider, file_data_list, additional_info,
                checkboxes, self.logger, self.temp_folderpath, debug_mode_check=self.debug_mode_check)
            output["fields"] = result
            output["fieldsList"] = done_fields_dList
            output["error"] = None

        if(self.debug_mode_check is False):
            CommonUtils.delete_dir_recursively(self.temp_folderpath)

        return output

    def extract_custom_fields(self, image_path: str,
                              checkbox_field_data_list: CHECKBOX_FIELD_DATA_LIST,
                              config_params_dict: CONFIG_PARAMS_DICT = None,
                              file_data_list: FILE_DATA_LIST = None) -> CHECKBOX_EXTRACT_CUSTOM_FIELD_OUTPUT:
        """API to extract checkboxes using given repective keys for each checkbox or bbox of checkbox

        Args:
            image_path (str): Path to the image
            checkbox_field_data_list (CHECKBOX_FIELD_DATA_LIST): Info for field_key and its match method,
                or either field_state_pos w.r.t key or field_state_bbox.
                Defaults to [CHECKBOX_FIELD_DATA_DICT].
            config_params_dict (CONFIG_PARAMS_DICT, optional): Additional info for min and max
                checkbox height to text height ratio, position of state w.r.t key,
                within_bbox(x,y,w,h), eliminate_list, scaling_factor and page number..
                Defaults to CONFIG_PARAMS_DICT.
            file_data_list (FILE_DATA_LIST, optional): List of all file datas. Each file data
                has the path to supporting document and page numbers, if applicable. Defaults to None.

        Raises:
            AttributeError: Both field_state_pos and field_state_bbox in text_field_data_list
                should not be given together.

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

        checkbox_field_data_list = [ExtractorHelper.get_updated_config_dict(
            CHECKBOX_FIELD_DATA_LIST[0], checkbox_field_data) for checkbox_field_data in checkbox_field_data_list]

        # read image
        image, image_path, _ = ExtractorHelper.read_image(
            image_path, self.logger, self.temp_folderpath,
            image_to_bw=config_params_dict["image_to_bw"])
        crop_image, crop_imagepath, _ = ExtractorHelper.read_image(
            image_path, self.logger, self.temp_folderpath, within_bbox,
            image_to_bw=config_params_dict["image_to_bw"])

        field_state_bbox_count, field_key_count = 0, 0
        for field_data in checkbox_field_data_list:
            if len(field_data["field_state_bbox"]) > 0:
                field_state_bbox_count += 1
            if len(field_data["field_key"]) > 0:
                field_key_count += 1

        additional_info = {"scaling_factor": scaling_factor,
                           'pages': [config_params_dict["page"]]}

        if(field_state_bbox_count == len(checkbox_field_data_list) and within_bbox == []):
            if(image_path != crop_imagepath):
                os.remove(crop_imagepath)
            return self.__extract_from_field_state_bboxes(image, checkbox_field_data_list,
                                                          additional_info)
        elif(field_state_bbox_count == 0 and field_key_count == len(checkbox_field_data_list)):
            return self.__extract_from_keys(
                image, crop_image, image_path, checkbox_field_data_list,
                within_bbox, file_data_list, config_params_dict, additional_info)
        else:
            raise AttributeError(
                "Given keys in the attribute 'checkbox_field_data_list' is incorrect")

    def __extract_from_field_state_bboxes(self, image, checkbox_field_data_list,
                                          additional_info):
        result = []
        output = {}
        for field_data in checkbox_field_data_list:
            bbox = field_data["field_state_bbox"]
            bbox = ExtractorHelper.get_updated_within_box(
                bbox, additional_info["scaling_factor"])
            res = {}
            checkboxes, error = self.__get_checkboxes(
                image, bbox[Constants.BB_H]//2, bbox[Constants.BB_H], field_data["field_state_bbox_square_only"])
            if(error is None):
                checkbox = []
                for c in checkboxes:
                    if(bbox[Constants.BB_X] + bbox[Constants.BB_W] >= c[Constants.BB_X] >= bbox[Constants.BB_X] and
                            bbox[Constants.BB_Y] + bbox[Constants.BB_H] >= c[Constants.BB_Y] >= bbox[Constants.BB_Y]):
                        checkbox.append(c)
                if(checkbox == []):
                    error = "No checkbox found"
            if(field_data.get("field_key") is not None):
                res["field_key"] = field_data.get("field_key")
            res["field_state_bbox"] = bbox
            if(error is None):
                res["field_state"] = ExtractorHelper.check_if_true(
                    image, checkbox[0], "checkbox")
            else:
                res["field_state"] = None
            res['error'] = error
            result.append(res)
        output['fields'] = result
        output['error'] = None

        return output

    def __get_checkboxes(self, image, MIN_CHECKBOX_WIDTH, MAX_CHECKBOX_WIDTH, find_square_only=True):
        checkboxes = []
        error = None
        gray = image.copy()
        SQUARE_SCALE = 4
        kernal = np.ones((2, 2), np.uint8)
        _, threshold = cv2.threshold(gray, 170, 255, cv2.THRESH_BINARY_INV)
        dilation = cv2.dilate(threshold, kernal, iterations=1)
        contours, _ = cv2.findContours(
            dilation, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        for i in range(0, len(contours)):
            cnt = contours[i]
            threshold = 0.04
            epsilon = threshold*cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, epsilon, True)
            _, _, w, h = cv2.boundingRect(cnt)
            if (len(approx) == Constants.RECT_EDGES and MIN_CHECKBOX_WIDTH <= w <= MAX_CHECKBOX_WIDTH) and ((h-(h//SQUARE_SCALE)) <= w <= (h+(h//SQUARE_SCALE))):
                xs, ys, ws, hs = cv2.boundingRect(cnt)
                checkboxes.append([xs, ys, ws, hs])

            if not find_square_only:
                # find rectangle
                threshold = 0.02
                epsilon = threshold*cv2.arcLength(cnt, True)
                approx = cv2.approxPolyDP(cnt, epsilon, True)
                _, _, w, h = cv2.boundingRect(cnt)
                # horizontal(w >= h) and vertical(h >= w) rectangle
                is_rectangle = ((w+(w//2) >= w >= h) or ((h+h//2) > h >= w))
                if (len(approx) == Constants.RECT_EDGES and is_rectangle):
                    xs, ys, ws, hs = cv2.boundingRect(cnt)
                    checkboxes.append([xs, ys, ws, hs])
        if(checkboxes == []):
            self.logger.info("No checkboxes found")
            error = "No checkboxes found"

        return checkboxes, error

    def __filter_extra_checkboxes(self, checkboxes):
        # filter extra checkboxes where two checkboxes is obtained for 1 checkbox
        # because two square contours
        # are detected for a single checkbox because of its thickness
        filter_checkbox = []
        for i in range(len(checkboxes)-1):
            c1 = checkboxes[i]
            c2 = checkboxes[i+1]
            # filters the outer square by comparing if both x and y coordinate of the outer square
            # is in the range of the x, y coordinate of inner square and x-width/9, y-width/9 of the
            # inner square
            if(c2[Constants.BB_X] >= c1[Constants.BB_X] >= (c2[Constants.BB_X] - c1[Constants.BB_W]//9) and
                    (c2[Constants.BB_Y] >= c1[Constants.BB_Y] >= (c2[Constants.BB_Y] - c1[Constants.BB_W]//9))):
                filter_checkbox.append(c1)
        checkboxes = [x for x in checkboxes if x not in filter_checkbox]
        return checkboxes

    def __extract_from_keys(self, image, crop_image, image_path,
                            checkbox_field_data_list, within_bbox,
                            file_data_list, config_params_dict, additional_info):
        output = {}
        bboxes_text, checkboxes, all_error = self.__common(
            crop_image, image_path, file_data_list, within_bbox,
            config_params_dict, scaling_factor=additional_info["scaling_factor"])
        # filter fieldboxes from bboxes_text
        bboxes_text = [
            x for x in bboxes_text if x not in config_params_dict["eliminate_list"]]
        bboxes_text = ExtractorHelper.filter_fieldboxes_from_ocr_words(
            checkboxes, bboxes_text)
        if(checkboxes is not None and (len(checkboxes)) < len(checkbox_field_data_list)):
            all_error.append(
                "No of checkbox identified is less than the number of given keys")
        if(all_error == []):
            result = []
            for field_data in checkbox_field_data_list:
                res = {}
                response = self.search_text_provider.get_bbox_for(
                    image, field_data.get("field_key"),
                    field_data.get("field_key_match"), file_data_list,
                    additional_info, self.temp_folderpath)

                key_bbox, error = response['regions'], response['error']
                if(key_bbox != [] and len(key_bbox) > 1):
                    if(within_bbox != []):
                        remove_key_bbox = []
                        for i in range(len(key_bbox)):
                            bbox = key_bbox[i]['regionBBox'][0]['bbox']
                            if(within_bbox[Constants.BB_X] <= bbox[Constants.BB_X] <= (within_bbox[Constants.BB_X]+within_bbox[Constants.BB_W]) and
                                    within_bbox[Constants.BB_Y] <= bbox[Constants.BB_Y] <= (within_bbox[Constants.BB_Y]+within_bbox[Constants.BB_H])):
                                pass
                            else:
                                remove_key_bbox.append(key_bbox[i])
                        key_bbox = [
                            x for x in key_bbox if x not in remove_key_bbox]
                    if(key_bbox != [] and len(key_bbox) > 1):
                        error = "More than one key found"
                    elif(key_bbox == []):
                        error = "Key: '" + \
                            field_data.get("field_key")+"' not found"
                res["field_key"] = field_data.get("field_key")
                if(error is None):
                    closest_checkbox = ExtractorHelper.get_closest_fieldbox(
                        checkboxes, field_data.get("field_state_pos"), key_bbox[0]['regionBBox'][0]['bbox'])

                    status = ExtractorHelper.check_if_true(
                        image, closest_checkbox, "checkbox")

                    res["field_state"] = status
                else:
                    res["field_state"] = None
                res["error"] = error
                result.append(res)
            output["fields"] = result
            output["error"] = None
        else:
            output["error"] = all_error
            output["fields"] = None
        return output

    def __common(self, crop_image, image_path, file_data_list, within_bbox,
                 config_params_dict, scaling_factor=1):
        all_error = []
        min_checkbox_text_scale = config_params_dict['min_checkbox_text_scale']
        max_checkbox_text_scale = config_params_dict['max_checkbox_text_scale']

        # to check the dpi and give appropriate warning, if any
        ExtractorHelper.check_image_dpi(image_path, self.logger)

        # get the ocr_words
        additional_info = {"scaling_factor": scaling_factor,
                           'pages': [config_params_dict["page"]]}
        bboxes_text = self.get_text_provider.get_tokens(
            1, None, within_bbox, file_data_list, additional_info, self.temp_folderpath)
        if len(bboxes_text) == 0:
            all_error.append("No words found in the region")

        # filter empty lines
        bboxes_text = [x for x in bboxes_text if x.get('text') != '']

        if(self.debug_mode_check):
            img_copy = crop_image.copy()
            bboxes_list = [x['bbox'] for x in bboxes_text]
            img_copy = ExtractorHelper.draw_bboxes_on_image(
                img_copy, bboxes_list, Constants.COLOR_BLUE, thickness=4)
            ExtractorHelper.save_image(
                img_copy, f'{self.temp_folderpath}/text_bboxes.jpg')

        # get checkboxes
        height = sum([bbox.get("bbox")[Constants.BB_H]
                      for bbox in bboxes_text])//len(bboxes_text)
        if(min_checkbox_text_scale is None and max_checkbox_text_scale is None):
            MIN_CHECKBOX_WIDTH, MAX_CHECKBOX_WIDTH = height-height//3, height+height//2
        else:
            MIN_CHECKBOX_WIDTH, MAX_CHECKBOX_WIDTH = height * \
                min_checkbox_text_scale, height*max_checkbox_text_scale
        checkboxes, error = self.__get_checkboxes(
            crop_image, MIN_CHECKBOX_WIDTH, MAX_CHECKBOX_WIDTH)

        if(self.debug_mode_check):
            img_copy = crop_image.copy()
            bboxes_list = checkboxes
            img_copy = ExtractorHelper.draw_bboxes_on_image(
                img_copy, bboxes_list, Constants.COLOR_RED, thickness=4)
            ExtractorHelper.save_image(
                img_copy, f'{self.temp_folderpath}/field_bboxes_pass1.jpg')

        if(error is not None):
            all_error.append(error)
        if(within_bbox != []):
            for c in checkboxes:
                c[Constants.BB_X] += within_bbox[Constants.BB_X]
                c[Constants.BB_Y] += within_bbox[Constants.BB_Y]

        # filter extra checkboxes
        checkboxes = self.__filter_extra_checkboxes(checkboxes)

        if(self.debug_mode_check):
            img_copy = crop_image.copy()
            bboxes_list = checkboxes
            img_copy = ExtractorHelper.draw_bboxes_on_image(
                img_copy, bboxes_list, Constants.COLOR_RED, thickness=4)
            ExtractorHelper.save_image(
                img_copy, f'{self.temp_folderpath}/field_bboxes_pass2.jpg')

        return bboxes_text, checkboxes, all_error

# ===============================================================================================================#
# Copyright 2021 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

"""
RadioButtonExtractor
~~~~~
This script accepts an image with radio buttons and the text and returns True if the button is checked
and False if the button is unchecked
It also returns a list of dictionary whch contains the text used as the key in radiobuttons
 and its corresponding bounding box coordinates


"""
import os
from os import path
import logging
import sys
import glob
import numpy as np
import cv2
from infy_field_extractor.internal.extractor_helper import ExtractorHelper
from infy_field_extractor.internal.constants import Constants
from infy_field_extractor.interface.data_service_provider_interface import DataServiceProviderInterface, FILE_DATA_LIST

RADIOBUTTON_FIELD_DATA_LIST = [
    {
        "field_key": [""],
        "field_key_match": {"method": "normal", "similarityScore": 1},
        "field_state_pos": "left",
        "field_state_bbox": []
    }
]

CONFIG_PARAMS_DICT = {
    'min_radius_text_scale': None,
    'max_radius_text_scale': None,
    'field_state_pos': None,
    'template_checked_folder': None,
    'template_unchecked_folder': None,
    'page': 1,
    "eliminate_list": [],
    "scaling_factor": {
        'hor': 1,
        'ver': 1
    },
    "within_bbox": []
}

RADIO_EXTRACT_ALL_FIELD_OUTPUT = {
    'fields': {
        '<field_key>': '<field_state>',
    },
    'error': ''
}

RADIO_EXTRACT_CUSTOM_FIELD_OUTPUT = {
    'fields': [
        {
            'field_key': [],
            'field_state': '',
            'field_state_bbox': []
        }
    ],
    'error': None
}


class RadioButtonExtractor():
    """Radio Button Extractor"""

    def __init__(self, get_text_provider: DataServiceProviderInterface,
                 search_text_provider: DataServiceProviderInterface,
                 temp_folderpath: str, logger=None, debug_mode_check=False):
        """Creates an instance of Radio button Extractor.

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
                           file_data_list: FILE_DATA_LIST = None) -> RADIO_EXTRACT_ALL_FIELD_OUTPUT:
        """API to extract all radiobuttons by template match automatically

        Args:
            image_path (str): Path to the image
            config_params_dict (CONFIG_PARAMS_DICT, optional): Additional info for min and
                max radiobutton radius to text height ratio, position of state w.r.t key,
                within_bbox(x,y,w,h), eliminate_list, scaling_factor and page number.
                Defaults to CONFIG_PARAMS_DICT.
            file_data_list (FILE_DATA_LIST, optional): List of all file datas. Each file data
                has the path to supporting document and page numbers, if applicable. Defaults to None.

        Raises:
            Exception: Valid template_checked_folder is required.
            Exception: Valid template_unchecked_folder is required.
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

        template_checked_folder, template_unchecked_folder = config_params_dict[
            'template_checked_folder'], config_params_dict['template_unchecked_folder']
        field_state_pos = config_params_dict.get('field_state_pos')

        if(template_checked_folder is not None):
            if(path.exists(template_checked_folder) is False):
                self.logger.error(
                    "property template_checked_folder not found")
                raise Exception("property template_checked_folder not found")
        if(template_unchecked_folder is not None):
            if(path.exists(template_unchecked_folder) is False):
                self.logger.error(
                    "property template_unchecked_folder not found")
                raise Exception("property template_unchecked_folder not found")
        if(field_state_pos is not None):
            raise AttributeError(
                "Currently field_state_pos is not used")

        output, all_error = {}, []

        # read the image
        crop_image, _, _ = ExtractorHelper.read_image(
            image_path, self.logger, self.temp_folderpath, within_bbox)
        _, image_path, _ = ExtractorHelper.read_image(
            image_path, self.logger, self.temp_folderpath)

        # to check the dpi and give appropriate warning, if any
        ExtractorHelper.check_image_dpi(image_path, self.logger)

        additional_info = {"scaling_factor": scaling_factor,
                           'pages': [config_params_dict["page"]]
                           }
        bboxes_text = self.get_text_provider.get_tokens(
            1, crop_image, within_bbox, file_data_list, additional_info, self.temp_folderpath)
        # bboxes_text, all_error = ExtractorHelper.get_ocr_text_bbox(
        #     ocr_parser_object, all_error, within_bbox, config_params_dict["page"], scaling_factor)
        if len(bboxes_text) == 0:
            all_error.append("No words found in the region")
        bboxes_text = [x for x in bboxes_text if x not in eliminate_list]

        # extract radio button status
        result, done_fields_dList, error = self.__extract_radio_by_template_match(
            crop_image, bboxes_text, within_bbox,
            file_data_list, additional_info,
            template_checked_folder, template_unchecked_folder)
        if(error is not None):
            all_error.append(error)
        if(all_error != []):
            output["error"] = all_error
            output["fields"] = result
            output["fieldsList"] = done_fields_dList
        else:
            output["fields"] = result
            output["fieldsList"] = done_fields_dList
            output["error"] = None
        return output

    def extract_custom_fields(
            self, image_path: str,
            radiobutton_field_data_list: RADIOBUTTON_FIELD_DATA_LIST,
            config_params_dict: CONFIG_PARAMS_DICT = None,
            file_data_list: FILE_DATA_LIST = None) -> RADIO_EXTRACT_CUSTOM_FIELD_OUTPUT:
        """API to extract radiobuttons using given respective keys for each radiobutton or
            bbox of radiobuttons

        Args:
            image_path (str): Path to the image
            radiobutton_field_data_list (RADIOBUTTON_FIELD_DATA_LIST): Info for field_key and
                its match method, and either field_state_pos w.r.t key or field_state_bbox.
                Defaults to [RADIOBUTTON_FIELD_DATA_DICT].
            config_params_dict (CONFIG_PARAMS_DICT, optional): Additional info for min and
                max radiobutton radius to text height ratio, position of state w.r.t key,
                within_bbox(x,y,w,h), eliminate_list, scaling_factor and page number
                Defaults to CONFIG_PARAMS_DICT.
            file_data_list (FILE_DATA_LIST, optional): List of all file datas.
                Each file data has the path to supporting document and page numbers, if applicable.
                Defaults to None.
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

        radiobutton_field_data_list = [ExtractorHelper.get_updated_config_dict(
            RADIOBUTTON_FIELD_DATA_LIST[0], radiobutton_field_data)
            for radiobutton_field_data in radiobutton_field_data_list]

        # read image
        image, image_path, img_name = ExtractorHelper.read_image(
            image_path, self.logger, self.temp_folderpath)
        crop_image, crop_imagepath, img_name = ExtractorHelper.read_image(
            image_path, self.logger, self.temp_folderpath, within_bbox)

        field_state_bbox_count, field_key_count = 0, 0
        for field_data in radiobutton_field_data_list:
            if len(field_data["field_state_bbox"]) > 0:
                field_state_bbox_count += 1
            if len(field_data["field_key"]) > 0:
                field_key_count += 1

        additional_info = {"scaling_factor": scaling_factor,
                           'pages': [config_params_dict["page"]]}

        if(field_state_bbox_count == len(radiobutton_field_data_list) and within_bbox == []):
            if(image_path != crop_imagepath):
                os.remove(crop_imagepath)
            return self.__extract_from_field_state_bboxes(
                image, img_name, radiobutton_field_data_list,
                additional_info)
        elif(field_state_bbox_count == 0 and field_key_count == len(radiobutton_field_data_list)):
            return self.__extract_from_keys(
                image, crop_image, crop_imagepath, img_name, radiobutton_field_data_list,
                within_bbox, file_data_list, config_params_dict, additional_info)
        else:
            raise AttributeError(
                "Given keys in the attribute 'radiobutton_field_data_list' is incorrect")

    def __extract_from_field_state_bboxes(
        self, image, img_name, radiobutton_field_data_list,
            additional_info):
        result = []
        output = {}
        for field_data in radiobutton_field_data_list:
            bbox = field_data["field_state_bbox"]
            bbox = ExtractorHelper.get_updated_within_box(
                bbox, additional_info["scaling_factor"])
            img = image[bbox[Constants.BB_Y]:bbox[Constants.BB_Y]+bbox[Constants.BB_H],
                        bbox[Constants.BB_X]:bbox[Constants.BB_X]+bbox[Constants.BB_W]]
            _, circle_values = self.__get_radiobutton_by_hough_circle(
                None, bbox[3]//8, bbox[3]//2, img, img_name, [])
            res = {}
            if(field_data.get("field_key") is not None):
                res["field_key"] = field_data.get("field_key")
            res["field_state_bbox"] = bbox
            if(circle_values is not None):
                circle_value = (max(circle_values, key=lambda x: x['bbox'][2]))
                circle_value["coordinates"][Constants.BB_X] += bbox[Constants.BB_X]
                circle_value['bbox'][Constants.BB_X] += bbox[Constants.BB_X]
                circle_value["coordinates"][Constants.BB_Y] += bbox[Constants.BB_Y]
                circle_value['bbox'][Constants.BB_Y] += bbox[Constants.BB_Y]
                res["field_state"] = ExtractorHelper.check_if_true(
                    image, circle_value['bbox'], "radio", circle_value['coordinates'], True, self.temp_folderpath, img_name)
                res['error'] = None
            else:
                res["field_state"] = None
                res['error'] = "No radiobuttons found"
            result.append(res)
        output['fields'] = result
        output['error'] = None
        return output

    def __extract_radio_by_template_match(
            self, image, bboxes_text, within_bbox, file_data_list,
            additional_info, template_checked_folder, template_unchecked_folder):
        error = None
        # get all the template files
        template_unchecked_files = glob.glob(
            template_unchecked_folder + "/*")
        template_checked_files = glob.glob(template_checked_folder + "/*")

        if(template_checked_files == [] and template_unchecked_files == []):
            self.logger.error("Template folders are empty")
            raise Exception("Template folders are empty")

        # gets all the radiobuttons
        checked_bboxes = self.__template_match(template_checked_files, image)
        unchecked_bboxes = self.__template_match(
            template_unchecked_files, image)
        # filter repeated radiobuttons
        if(checked_bboxes != []):
            checked_bboxes = self.__filter_repeated_fields(checked_bboxes)
        if(unchecked_bboxes != []):
            unchecked_bboxes = self.__filter_repeated_fields(unchecked_bboxes)
        fieldboxes = checked_bboxes + unchecked_bboxes
        if(within_bbox != []):
            for c in fieldboxes:
                c[Constants.BB_X] += within_bbox[Constants.BB_X]
                c[Constants.BB_Y] += within_bbox[Constants.BB_Y]

        if(fieldboxes == []):
            self.logger.error("No radiobuttons found")
            error = "No radiobuttons found"
            return None, None, error

        # calling field extractor to extract radiobuttons value and its text
        # Returns a dict containing text and its corresponding radiobutton's coordinates
        # and a list of dict contaning used texts and its coordinates
        res, done_fields_dList = ExtractorHelper.extract_with_text_coordinates(
            image, bboxes_text, self.get_text_provider,
            file_data_list, additional_info,
            fieldboxes, self.logger, self.temp_folderpath, "radio")

        # matching checked and unchecked radiobuttons with res
        result = {}
        for c in checked_bboxes:
            for key, value in res.items():
                if (c == value):
                    result[key] = True
        for c in unchecked_bboxes:
            for key, value in res.items():
                if (c == value):
                    result[key] = False

        # returning the final result
        return result, done_fields_dList, error

    def __extract_from_keys(
            self, image, crop_image, crop_imagepath, img_name, radiobutton_field_data_list,
            within_bbox, file_data_list, config_params_dict, additional_info):
        output, all_error = {}, []
        min_radius_text_scale = config_params_dict["min_radius_text_scale"]
        max_radius_text_scale = config_params_dict["max_radius_text_scale"]

        # get text bbox from ocr
        bboxes_text = self.get_text_provider.get_tokens(
            1, crop_image, within_bbox, file_data_list, additional_info, self.temp_folderpath)
        if len(bboxes_text) == 0:
            all_error.append("No words found in the region")
        bboxes_text = [
            x for x in bboxes_text if x not in config_params_dict["eliminate_list"]]

        # get radio buttons
        fieldboxes, circle_values = self.__get_radiobutton_by_hough_circle(
            bboxes_text, min_radius_text_scale, max_radius_text_scale, crop_image, img_name, within_bbox)

        if(all_error == []):
            result = []
            for field_data in radiobutton_field_data_list:
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
                            if(within_bbox[Constants.BB_X] <= bbox[Constants.BB_X] <= (within_bbox[Constants.BB_X]+within_bbox[Constants.BB_W]) and within_bbox[Constants.BB_Y] <= bbox[Constants.BB_Y] <= (within_bbox[Constants.BB_Y]+within_bbox[Constants.BB_H])):
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
                    closest_radio = ExtractorHelper.get_closest_fieldbox(
                        fieldboxes, field_data.get("field_state_pos"), key_bbox[0]['regionBBox'][0]['bbox'])
                    for circle in circle_values:
                        if(circle["bbox"] == closest_radio):
                            coordinates = circle["coordinates"]
                            break

                    status = ExtractorHelper.check_if_true(
                        crop_image, closest_radio, "radio", coordinates)

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
        if(self.debug_mode_check is False):
            if(within_bbox != []):
                os.remove(crop_imagepath)
        return output

    def __template_match(self, template_files, image):
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        except Exception:
            gray = image
        matched_bbox = []
        for file in template_files:
            template = cv2.imread(file, cv2.IMREAD_GRAYSCALE)
            w, h = template.shape[:: -1]
            if(h > gray.shape[0] or w > gray.shape[1]):
                continue
            res = cv2.matchTemplate(
                gray, template, cv2.TM_CCOEFF_NORMED)
            threshold = 0.9
            loc = np.where(res >= threshold)
            if(len(loc[0]) > 0):
                img2 = image.copy()
                for pt in zip(*loc[:: -1]):
                    cv2.rectangle(
                        img2, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), 2)
                    matched_bbox.append([pt[0], pt[1], w, h])
                if(self.debug_mode_check is True):
                    cv2.imwrite(self.temp_folderpath+'res.png', img2)
                break
        return matched_bbox

    def __filter_repeated_fields(self, fieldboxes):
        # to eliminate extra fields for the same radiobutton
        DIFF = 2
        # it initiates the variable fields with the first radiobutton
        fields = [fieldboxes[0]]
        flag = 1
        for f1 in fieldboxes:
            for f2 in fieldboxes:
                # for the same radiobutton we get various bounding box with the difference of 2
                # between x-coordinates and y-coordinates of  all the bboxes
                if(f2[Constants.BB_X]-DIFF <= f1[Constants.BB_X] <= f2[Constants.BB_X]+DIFF and f2[Constants.BB_Y]-DIFF <= f1[Constants.BB_Y] <= f2[Constants.BB_Y]+DIFF):
                    continue
                for f in fields:
                    if(f[Constants.BB_X]-DIFF <= f1[Constants.BB_X] <= f[Constants.BB_X]+DIFF and f[Constants.BB_Y]-DIFF <= f1[Constants.BB_Y] <= f[Constants.BB_Y]+DIFF):
                        flag = 0
                        break
                if(flag == 1):
                    fields.append(f1)
                    break
                if(flag == 0):
                    break
            flag = 1
        return fields

    def __get_radiobutton_by_hough_circle(
            self, ocr_word_dict, min_radius_text_scale, max_radius_text_scale,
            image, image_name, within_bbox):
        # get radiobuttons for field_list_data using hough circles

        if(ocr_word_dict is None):
            height = 1
        else:
            height = sum([bbox.get("bbox")[Constants.BB_H]
                          for bbox in ocr_word_dict])//len(ocr_word_dict)
        if(min_radius_text_scale is not None and max_radius_text_scale is not None):
            MIN_RADIUS, MAX_RADIUS = height*min_radius_text_scale, height*max_radius_text_scale
        else:
            MIN_RADIUS, MAX_RADIUS = height//4, 2*height//3
        _, thresh = cv2.threshold(
            src=image, thresh=127, maxval=255, type=0)
        img_blur = cv2.medianBlur(thresh, 5)
        circles = cv2.HoughCircles(img_blur, cv2.HOUGH_GRADIENT, 1, 20, param1=50, param2=16,
                                   minRadius=MIN_RADIUS, maxRadius=MAX_RADIUS)
        if(self.debug_mode_check is True):
            cv2.imwrite(
                f'{self.temp_folderpath}\\{image_name}_crop.png', image)
            cv2.imwrite(
                f'{self.temp_folderpath}\\{image_name}_thresh.png', thresh)
            cv2.imwrite(
                f'{self.temp_folderpath}\\{image_name}_blur.png', img_blur)
        # bounding box around the circles
        fieldboxes = []
        circle_values = []
        if circles is not None:
            circles = np.uint16(np.around(circles))
            for c in circles[0, :]:
                cv2.circle(image, (c[0], c[1]), c[2], (0, 0, 250), 4)
                cv2.imwrite(
                    f'{self.temp_folderpath}\\{image_name}_circle.png', image)
                x = int(c[0]-c[2]-2)
                y = int(c[1] - c[2]-2)
                w = int(2 * (c[2]+2))
                h = int(2*(c[2]+2))
                fieldboxes.append([x, y, w, h])
                circle_values.append(
                    {"bbox": [x, y, w, h], "coordinates": [c[0], c[1], c[2]]})
        if(within_bbox != []):
            for i, c in enumerate(fieldboxes):
                c[Constants.BB_X] += within_bbox[Constants.BB_X]
                c[Constants.BB_Y] += within_bbox[Constants.BB_Y]
                circle_values[i]["bbox"][Constants.BB_X], circle_values[i]["bbox"][Constants.BB_Y] = c[Constants.BB_X], c[Constants.BB_Y]
                circle_values[i]["coordinates"][Constants.BB_X] += within_bbox[Constants.BB_X]
                circle_values[i]["coordinates"][Constants.BB_Y] += within_bbox[Constants.BB_Y]

        return fieldboxes, circle_values

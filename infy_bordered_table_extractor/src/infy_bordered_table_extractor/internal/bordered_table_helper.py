# ===============================================================================================================#
# Copyright 2021 Infosys Ltd.
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at
# http://www.apache.org/licenses/                                                        #
# ===============================================================================================================#

import datetime
import os
import json
import copy
import cv2
import numpy as np
import pandas as pd
from PIL import Image
from infy_bordered_table_extractor.internal.constants import *


class TableHelper:

    @staticmethod
    def rotate_image(img, angle):
        if(angle == 90):
            return cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
        elif(angle == 180):
            return cv2.rotate(img, cv2.ROTATE_180)
        elif(angle == 270):
            return cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
        else:
            return img

    @staticmethod
    def deskew_image(img, angle):
        (h, w) = img.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(img, M, (w, h),
                                 flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        return rotated

    @staticmethod
    def check_image_dpi(img_file):
        im = Image.open(img_file)
        warning = None
        try:
            dpi = im.info['dpi']
            if(dpi[0] < TESSERACT_MIN_DPI and dpi[1] < TESSERACT_MIN_DPI):
                warning = "The result might be not accurate due to dpi less than 300"
        except Exception:
            warning = "Dpi of the image cannot be extracted: The result might be not accurate if the dpi is less than 300"
        return warning

    @staticmethod
    def generate_excel_and_json(img_name, body_arr, header_arr, output_dict, OutputFileFormat, logger):
        save_folder_path = output_dict['path']
        dataframe = pd.DataFrame(np.array(body_arr), columns=header_arr)
        response = json.loads(dataframe.to_json(orient='records'))
        if(len(response) == 0):
            response = header_arr
        output_dataframe = dataframe.style.set_properties(align="left")
        logger.debug("showing data: {}".format(dataframe))
        if save_folder_path is not None and \
                OutputFileFormat.EXCEL in output_dict['format']:
            output_dataframe.to_excel(save_folder_path + f'/{img_name}.xlsx')
        return response

    @staticmethod
    def crop_image(img, within_bbox):
        if within_bbox:
            x = within_bbox[0]
            y = within_bbox[1]
            w = within_bbox[2]
            h = within_bbox[3]
            img = img[y:y+h, x:x+w]
        return img

    @staticmethod
    def make_dir_with_timestamp(folderpath, img_name):
        timestr = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        folderpath = os.path.join(
            folderpath, img_name+'_'+timestr)
        os.mkdir(folderpath)
        return folderpath

    @staticmethod
    def get_cells_bbox(height, width, vertical_lines, horizontal_lines, temp_folderpath, debug_mode_check, logger, method):
        shape = (height, width)
        # adds the vertical and horizontal lines images
        img_vh = cv2.addWeighted(
            vertical_lines, 0.5, horizontal_lines, 0.5, 0.0)
        if(len(img_vh.shape) == 3):
            img_vh = cv2.cvtColor(img_vh, cv2.COLOR_RGB2GRAY)
        _, img_vh = cv2.threshold(
            img_vh, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        if(method == 'pixel_level_line_detect'):
            img_vh = 255-img_vh
        if(debug_mode_check is True):
            cv2.imwrite(temp_folderpath+"/" +
                        'img_vh.png', img_vh)

        contours, _ = cv2.findContours(
            img_vh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        logger.debug(f"Detecting contours for {len(contours)} cells")

        box = []
        img_vh_c = cv2.cvtColor(img_vh, cv2.COLOR_GRAY2BGR)
        for c in contours:
            x, y, w, h = cv2.boundingRect(c)
            if (w <= shape[1]-shape[1]/5 and w > shape[1]/30 and h <= shape[1]-shape[0]/5 and h >= shape[0]/50):
                image = cv2.rectangle(
                    img_vh_c, (x, y), (x+w, y+h), (0, 0, 255), 2)
                box.append([x, y, w, h])

        if(len(box) == 0):
            raise Exception("No cells detected")
        if(debug_mode_check is True):
            cv2.imwrite(temp_folderpath+"/" +
                        'boxes.png', image)
        return box

    @staticmethod
    def validate_rgb_contrast_method(rgb_contrast_method):
        error_1 = "'rgb_line_skew_detection_method' is incorrect"
        methods = ['convolution_contrast_method', 'adaptive_contrast_method']
        if(type(rgb_contrast_method) is list):
            if(len(rgb_contrast_method) == 2):
                if(rgb_contrast_method[0] in methods and rgb_contrast_method[1] in methods):
                    pass
            elif(len(rgb_contrast_method) == 1):
                if(rgb_contrast_method[0] in methods):
                    pass
            else:
                raise AttributeError(error_1)
        else:
            raise AttributeError(error_1)

    @staticmethod
    def get_invalid_keys(truth_dict, test_dict) -> list:
        """Compare two dictionary objects and return invalid keys by using one of them as reference

        Args:
            truth_dict (dict): The object containing all valid keys
            test_dict (dict): The object to evaluate for presence of invalid keys

        Returns:
            list: The list of invalid keys
        """

        def __get_all_keys_recursively(parent_key, dict_obj):
            all_keys = []
            for k, val in dict_obj.items():
                key = k if parent_key is None or len(
                    parent_key) == 0 else f"{parent_key}->{k}"
                if not key in all_keys:
                    all_keys.append(key)
                if isinstance(val, dict):
                    all_keys += __get_all_keys_recursively(key, val)
            return all_keys

        truth_keys = __get_all_keys_recursively(None, truth_dict)
        test_keys = __get_all_keys_recursively(None, test_dict)
        return list(set(test_keys)-set(truth_keys))

    @staticmethod
    def get_updated_config_dict(from_dict, default_dict):
        config_dict_temp = copy.deepcopy(default_dict)
        for key in from_dict:
            if isinstance(from_dict[key], dict):
                if config_dict_temp.get(key) is None:
                    config_dict_temp[key] = from_dict[key]
                else:
                    config_dict_temp[key] = TableHelper.get_updated_config_dict(
                        from_dict[key], config_dict_temp[key])
            else:
                if config_dict_temp.get(key) is None:
                    config_dict_temp[key] = from_dict[key]
        return config_dict_temp

# ===============================================================================================================#
# Copyright 2020 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import re
import copy
from infy_ocr_parser._internal.ocr_const import RegUnitsRe


class CommonUtil:
    @classmethod
    def get_lookup_pages(cls, reg_def_obj, page_dict_list):
        try:
            pages = []
            page_list_from_dict = [page_dict['page']
                                   for page_dict in page_dict_list]
            if not page_list_from_dict:
                return pages
            total_pages = max(page_list_from_dict)
            page_list_from_dict.sort()
            if "pageNum" in reg_def_obj and len(reg_def_obj["pageNum"]) > 0:
                for pnum in reg_def_obj["pageNum"]:
                    pnum = pnum if (isinstance(pnum, str) and (
                        ":" in pnum)) else int(pnum)
                    if isinstance(pnum, str):
                        num_arr = [int(num)
                                   for num in pnum.split(":") if len(num) > 0]
                        if bool(re.match(r'^-?[0-9]+\:{1}-?[0-9]+$', pnum)):
                            page_arr = cls.__get_range_val(total_pages+1)
                            if (num_arr[0] < 0 and num_arr[1] < 0) or (num_arr[0] > 0 and num_arr[1] > 0):
                                num_arr.sort()
                            num_arr[0] = num_arr[0] if num_arr[0] > 0 else num_arr[0]-1
                            num_arr[1] = num_arr[1] + \
                                1 if num_arr[1] > 0 else num_arr[1]

                            pages += page_arr[num_arr[0]: num_arr[1]]
                        elif bool(re.match(r'^-?[0-9]+\:{1}$', pnum)):
                            page_arr = cls.__get_range_val(total_pages)
                            pages += page_arr[num_arr[0]:]
                        elif bool(re.match(r'^\:{1}-?[0-9]+$', pnum)):
                            page_arr = cls.__get_range_val(
                                total_pages+1, position=1)
                            pages += page_arr[:num_arr[0]]
                        else:
                            raise Exception
                    elif pnum < 0:
                        pages += [cls.__get_range_val(
                            total_pages, position=1)[pnum]]
                    elif pnum > 0:
                        pages.append(pnum)
                    else:
                        raise Exception
            else:
                pages = page_list_from_dict
            return pages
        except:
            raise Exception(
                "Please provide valid 'pageNum'. For example, specific page - [1,-1] or range - [1:5,6:-1, -2:-1] or end to/start from [:5,15:].")

    @classmethod
    def __get_range_val(cls, n, position=0):
        return [i for i in range(position, n+1)]

    @classmethod
    def convert_to_decimal(cls, x, p):
        return int(abs(x) * float(re.findall(RegUnitsRe.NUM_RE, p)[0])/100)

    @classmethod
    def get_rect_point_for(cls, x1, y1, x2, y2):
        l, t, r, b = min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2)
        w, h = r-l, b-t
        return [l, t, w, h]

    @classmethod
    def calc_scaling_factor(cls, image_width, image_height,
                            page_bbox_dict_list, scale_to_page=False, page=0):

        warnings = ''
        scale_hor, scale_ver = 1.0, 1.0
        if page > 0:
            page_bbox_dict_list = [
                page_obj for page_obj in page_bbox_dict_list if page_obj['page'] == page]
        if not page_bbox_dict_list:
            pass
        elif scale_to_page:
            if image_width > 0:
                scale_hor = page_bbox_dict_list[0]['bbox'][2]/image_width
            if image_height > 0:
                scale_ver = page_bbox_dict_list[0]['bbox'][3]/image_height
        else:
            if image_width > 0:
                scale_hor = image_width/page_bbox_dict_list[0]['bbox'][2]
            if image_height > 0:
                scale_ver = image_height/page_bbox_dict_list[0]['bbox'][3]
        return float(scale_ver), float(scale_hor), warnings

    @classmethod
    def scaling_bbox_for(cls, token_dict_list, scaling_factor_ver, scaling_factor_hor):
        for token_dict in token_dict_list:
            if isinstance(token_dict, dict):
                bbox = token_dict["bbox"]
                bbox[0], bbox[2] = (
                    bbox[0] * scaling_factor_hor), (bbox[2] * scaling_factor_hor)
                bbox[1], bbox[3] = (
                    bbox[1] * scaling_factor_ver), (bbox[3] * scaling_factor_ver)
                token_dict["bbox"] = bbox
                token_dict["scalingFactor"] = [
                    scaling_factor_ver, scaling_factor_hor]
                words_dict_list = token_dict.get("words", [])
                if len(words_dict_list) > 0:
                    token_dict["words"] = cls.scaling_bbox_for(
                        words_dict_list, scaling_factor_ver, scaling_factor_hor)
        return token_dict_list

    @classmethod
    def scale_reg_def_list(cls, reg_def_list, scaling_factors_key='1.0_1.0'):
        new_reg_def_list = []
        for reg_def in reg_def_list:
            cp_reg_def = copy.deepcopy(reg_def)
            scaling_factor_ver, scaling_factor_hor = [
                float(i) for i in scaling_factors_key.split('_')]
            if "anchorPoint1" in cp_reg_def:
                cp_reg_def["anchorPoint1"] = cls.__scaling_ap_for(
                    cp_reg_def["anchorPoint1"], scaling_factor_ver, scaling_factor_hor)

            if "anchorPoint2" in cp_reg_def:
                cp_reg_def["anchorPoint2"] = cls.__scaling_ap_for(
                    cp_reg_def["anchorPoint2"], scaling_factor_ver, scaling_factor_hor)
        new_reg_def_list.append(cp_reg_def)
        return new_reg_def_list

    @classmethod
    def scaling_region_points_for(cls, reg_def_list, page_bbox_dict_list):
        new_reg_def_list, warnings = [], []
        for reg_def in reg_def_list:
            cp_reg_def = copy.deepcopy(reg_def)
            if "pageDimensions" in cp_reg_def:
                pd_w = cp_reg_def["pageDimensions"].get("width", 0)
                pd_h = cp_reg_def["pageDimensions"].get("height", 0)
                scaling_factor_ver, scaling_factor_hor, warning_msg = cls.calc_scaling_factor(
                    pd_w, pd_h, page_bbox_dict_list, True)
                warnings.append(warning_msg)
                if "anchorPoint1" in cp_reg_def:
                    cp_reg_def["anchorPoint1"] = cls.__scaling_ap_for(
                        cp_reg_def["anchorPoint1"], scaling_factor_ver, scaling_factor_hor)

                if "anchorPoint2" in cp_reg_def:
                    cp_reg_def["anchorPoint2"] = cls.__scaling_ap_for(
                        cp_reg_def["anchorPoint2"], scaling_factor_ver, scaling_factor_hor)
            new_reg_def_list.append(cp_reg_def)
        return new_reg_def_list, warnings, {'ver': scaling_factor_ver, 'hor': scaling_factor_hor}

    @classmethod
    def __scaling_ap_for(cls, anc_point, scaling_factor_ver, scaling_factor_hor):
        if anc_point:
            for k, v in anc_point.items():
                if (v is not None) and bool(re.match(RegUnitsRe.PIXEL_RE, str(v))):
                    a_point = int(str(v).replace("px", ""))
                    #  it as this anchor point used for region find and calculation
                    if k == 'right' or k == 'left':
                        anc_point[k] = (a_point*scaling_factor_hor)
                    else:
                        anc_point[k] = (a_point*scaling_factor_ver)
        return anc_point

    @classmethod
    def get_invalid_keys(cls, truth_dict, test_dict) -> list:
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

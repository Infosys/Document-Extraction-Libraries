# ===============================================================================================================#
# Copyright 2021 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import re
import copy
from infy_ocr_parser.internal.ocr_const import *


class OcrValidator:

    @staticmethod
    def validate_is_anyone_exist(point1, point2, p1_def="anchorPoint1", p2_def="anchorPoint2"):
        if (p1_def != p2_def) and ((point1 and not point2) or (point2 and not point1)):
            raise Exception("Please provide "+p1_def+" and " + p2_def+".")

    @staticmethod
    def validate_point_count(val_dict):
        error = "Provide only two value for anchor1 and anchor2 points. The values provided cannot be for both left and right or top and bottom."
        if val_dict and \
            ((OcrValidator.get_points_count(val_dict) is not 2) or
                (OcrValidator.get_val(BBoxLabel.LEFT, val_dict) is not None and OcrValidator.get_val(BBoxLabel.RIGHT, val_dict) is not None) or
                (OcrValidator.get_val(BBoxLabel.TOP, val_dict) is not None and OcrValidator.get_val(BBoxLabel.BOTTOM, val_dict) is not None)):
            raise Exception(error)

    @staticmethod
    def validate_and_get_anc_txt(label, val_dict):
        a_txt = OcrValidator.get_val(label, val_dict)
        if a_txt is None or len(a_txt) == 0:
            raise Exception(label+" is empty.")
        OcrValidator.validate_anc_txt_arr(a_txt)
        return a_txt

    @staticmethod
    def validate_anc_points(val_dict, is_empty_at=False):
        error_msg_1 = "Left-Top negative points or Right-Bottom positive points of anchorPoint1/anchorPoint2 are not allowed when (-/+)%a or anchorText not provided."
        error_msg_2 = "Please correct the anchor1/anchor2 Points. Valid values are null, (-/+)numbers, strings containing (-/+)numbers or num(px) or (-/+)% or (-/+)%r or (+)%a or (-/+)t."
        if not val_dict:
            return
        for label in val_dict:
            val = copy.copy(val_dict[label])
            if val is None:
                continue
            if is_empty_at or (type(val) == str and bool(re.match(RegUnitsRe.PERCT_ABS_RE, val))):
                if (((type(val) == str and re.search("^[-]", val)) or (type(val) == int and val < 0)) and (label == BBoxLabel.LEFT or label == BBoxLabel.TOP)) or \
                        (((type(val) == str and re.search("^[1-9]", val)) or (type(val) == int and val > 0)) and (label == BBoxLabel.RIGHT or label == BBoxLabel.BOTTOM)):
                    raise Exception(error_msg_1)
            if type(val) == str:
                if not (bool(re.match(RegUnitsRe.PIXEL_RE, val)) or bool(re.match(RegUnitsRe.PERCT_ABS_RE, val)) or bool(re.match(RegUnitsRe.PERCT_REL_RE, val)) or bool(re.match(RegUnitsRe.TEXT_SIZE_RE, val))):
                    raise Exception(error_msg_2)

    @staticmethod
    def check_for_None(val_dict):
        found_none = True
        if val_dict:
            for label in val_dict:
                if val_dict[label] is not None:
                    found_none = False
                    break
        return None if found_none else val_dict

    @staticmethod
    def get_points_count(val_dict):
        point_count = 0
        for label in val_dict:
            if val_dict[label] is not None:
                point_count += 1
        return point_count

    @staticmethod
    def get_val(key, val_dict):
        return val_dict[key] if key in val_dict else None

    @staticmethod
    def is_percentage_val(val):
        return val is not None and type(val) == str and "%" in val

    @staticmethod
    def validate_anc_txt_arr(acn_txt):
        error = "anchorText should either be 1d or 2d array"
        if isinstance(acn_txt, list):
            count1, count2 = 0, 0
            for i in acn_txt:
                if isinstance(i, str):
                    if(i.strip() != ""):
                        count1 += 1
                elif isinstance(i, list):
                    count2 += 1
                    for j in i:
                        if isinstance(j, list):
                            raise Exception(error)
            if (count1 == len(acn_txt) and count2 == 0) or (count2 == len(acn_txt) and count1 == 0):
                return
            else:
                raise Exception(error)
        else:
            raise Exception(error)

    @staticmethod
    def validate_and_get_anc_txt_match(reg_def_dict, match_method, similarity_score):
        if reg_def_dict['anchorTextMatch']["method"] != "":
            match_method = reg_def_dict['anchorTextMatch']['method']
            if(match_method.lower() == 'normal' or match_method.lower() == 'regex'):
                similarity_score = reg_def_dict['anchorTextMatch']['similarityScore'] if reg_def_dict['anchorTextMatch'].get(
                    'similarityScore') != None else similarity_score
                if(similarity_score < 0 or similarity_score > 1):
                    raise Exception(
                        "Similarity score has to be in the range of 0 and 1")
            else:
                raise Exception("Match Method can either be Normal or Regex")
        return match_method, similarity_score

    @staticmethod
    def validate_and_convert_scaling_factor(scaling_factor):
        try:
            if isinstance(scaling_factor, str) and scaling_factor.find('_') != -1:
                return scaling_factor
            scaling_factor_ver = float(scaling_factor.get('ver', 1))
            scaling_factor_hor = float(scaling_factor.get('hor', 1))
            if scaling_factor_ver < 1:
                raise Exception("")
            if scaling_factor_hor < 1:
                raise Exception("")
        except Exception:
            raise Exception("Valid scaling_factor value is required.")
        return f'{scaling_factor_ver}_{scaling_factor_hor}'

    @staticmethod
    def validate_max_word_space(maxWordSpace):
        if bool(re.match(r"^[0-9]+(px)?$", str(maxWordSpace))):
            return int(str(maxWordSpace).replace("px", ""))
        elif bool(re.match(r"^[0-9]+(.)?([0-9])+t$", maxWordSpace)):
            return maxWordSpace
        elif bool(re.match(r"^[0-9]+(.)?([0-9])+%$", maxWordSpace)):
            return maxWordSpace
        else:
            raise Exception("Valid maxWordSpace value is required")

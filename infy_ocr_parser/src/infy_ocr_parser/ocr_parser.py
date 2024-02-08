# ===============================================================================================================#
# Copyright 2021 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import os
import enum
import copy
import logging
import traceback
from imageio import imsave
import cv2
from infy_ocr_parser.internal import ocr_helper
from infy_ocr_parser.internal.response import Response
from infy_ocr_parser.internal.ocr_const import RegLabel, PlotBbox
from infy_ocr_parser.internal.ocr_validator import OcrValidator
from infy_ocr_parser.internal.file_util import FileUtil
from infy_ocr_parser.internal.common_util import CommonUtil
from infy_ocr_parser.interface.data_service_provider_interface import DataServiceProviderInterface


class OcrType(enum.Enum):
    """Ocr type"""
    TESSERACT = 1
    ABBYY = 2


ANCHOR_TXT_DICT = {
    "anchorText": [
        ""
    ],
    "anchorTextMatch": {
        "method": "",
        "similarityScore": 1,
        "maxWordSpace": '1.5t'
    },
    "pageNum": [],
    "distance": {
        "left": None,
        "top": None,
        "right": None,
        "bottom": None
    },
    "pageDimensions": {
        "width": 0,
        "height": 0
    }
}

REG_DEF_DICT = {
    "anchorText": [
        ""
    ],
    "pageNum": [],

    "anchorTextMatch": {
        "method": "",
        "similarityScore": 1,
        "maxWordSpace": '1.5t',
        "occurrenceNums": []
    },
    "anchorPoint1": {
        "left": None,
        "top": None,
        "right": None,
        "bottom": None
    },
    "anchorPoint2": {
        "left": None,
        "top": None,
        "right": None,
        "bottom": None
    },
    "pageDimensions": {
        "width": 1000,
        "height": 1000
    }
}

CONFIG_PARAMS_DICT = {
    "match_method": 'normal',
    "similarity_score": 1,
    "max_word_space": '1.5t'
}

REG_BBOX_DICT = {"bbox": [], "page": 1}

SCALING_FACTOR = {
    'hor': 1,
    'ver': 1
}

PLOT_DATA = {
    'token_type_value': 1,
    'images': [{
        'image_page_num': 1,
        'image_file_path': ''
    }]
}


class OcrParser:
    """Class providing APIs to parse OCR XML files"""

    def __init__(self, ocr_file_list: list, data_service_provider: DataServiceProviderInterface,
                 config_params_dict=CONFIG_PARAMS_DICT, logger: logging.Logger = None,
                 log_level: int = None):
        """Creates an instance of OCR Parser.

        Args:
            ocr_file_list (list): List of OCR documents with full path. E.g. `[C:\\1.hocr]`.
            data_service_provider (DataServiceProviderInterface): Provider to parse OCR file of
                a specified OCR tool.
            config_params_dict (CONFIG_PARAMS_DICT, optional): Configuration dictionary for achor
                text match method. Defaults to CONFIG_PARAMS_DICT.
            logger (logging.Logger, optional): Logger object. Defaults to None.
            log_level (int, optional): log level. Defaults to None.

        Raises:
            Exception: Valid ocr_file_list is required.
            Exception: Invalid keys found in config_params_dict.
            Exception: Valid DataServiceProvider is required.
        """

        if not ocr_file_list:
            raise Exception(
                "Valid ocr_file_list is required")

        # Validate incoming config dictionary
        invalid_keys = CommonUtil.get_invalid_keys(
            CONFIG_PARAMS_DICT, config_params_dict)
        if len(invalid_keys) > 0:
            raise Exception(
                f"Invalid keys found in config_params_dict: {invalid_keys}")
        config_params_dict = FileUtil.get_updated_config_dict(
            config_params_dict, CONFIG_PARAMS_DICT)
        self._logger = logger
        log_level = log_level if log_level else logging.INFO
        if logger is None:
            logging.basicConfig(
                level=log_level,
                format='%(asctime)s.%(msecs)03d %(levelname)s ocr-parser - %(module)s - %(funcName)s: %(message)s'
            )
            logger = logging.getLogger()
            self._logger = logger
            logger.info('log initialized')
        ocr_file_data_list = []
        for ocr_file in ocr_file_list:
            ocr_file_obj = open(ocr_file, 'r', encoding="utf8")
            ocr_file_data_list.append(ocr_file_obj.read())

        self._match_method = config_params_dict['match_method']
        self._similarity_score = config_params_dict['similarity_score']
        self._max_word_space = OcrValidator.validate_max_word_space(
            config_params_dict['max_word_space'])

        if data_service_provider:
            data_service_provider.init_provider_inputs(ocr_file_list)
            ocr_handler_obj = data_service_provider
        else:
            raise Exception("Valid DataServiceProvider is required.")
        self._ocr_helper_obj = ocr_helper.OcrHelper(
            self._logger, ocr_handler_obj, self._max_word_space)

    def get_tokens_from_ocr(self, token_type_value: int, within_bbox=[],
                            ocr_word_list=[], pages=[], scaling_factor=SCALING_FACTOR,
                            max_word_space='1.5t') -> list:
        """Get Json data of token_type_value by parsing the OCR file(s).

        Args:
            token_type_value (int):  1(WORD), 2(LINE), 3(PHRASE)
            within_bbox(x,y,w,h) (list, optional): Return Json data within this region.
                Default is empty list.
            ocr_word_list (list, optional): When token_type_value is 3(PHRASE)
                then ocr_word_list formed as pharse and returns Json data of it.
                Default is empty list.
            pages (list, optional): To get token_type_value Json data for specific page(s) from list of pages.
                Default is empty list.
            scaling_factor (SCALING_FACTOR, optional): Scale to given number and then returns token.
                Defaults to SCALING_FACTOR.
            max_word_space (str, optional): max space between words to consider them as one phrase.
                Defaults to '1.5t'.

        Returns:
            list: List of token dict
        """
        def _sort_token_page(tokens):
            for i in range(len(tokens)):
                for j in range(len(tokens)):
                    if tokens[i]['page'] < tokens[j]['page']:
                        tokens[i], tokens[j] = tokens[j], tokens[i]
            return tokens
        scaling_factor = OcrValidator.validate_and_convert_scaling_factor(
            scaling_factor)
        tokens = copy.deepcopy(self._ocr_helper_obj.get_tokens_from_ocr(
            token_type_value=token_type_value,
            within_bbox=within_bbox, ocr_word_list=ocr_word_list, pages=pages,
            scaling_factors_key=scaling_factor, max_word_space=max_word_space))
        # Sorting based on page no.
        tokens = _sort_token_page(tokens)
        return Response.update_get_tokens_bbox_response(tokens)

    def save_tokens_as_json(self, out_file, token_type_value: int, pages=[], scaling_factor=SCALING_FACTOR) -> dict:
        """Save token_type_value Json data to out_file location by parsing the OCR file(s).

        Args:
            out_file (str): Json file full path. E.g. 'C:/word_token.json'.
            token_type_value (int): 1(WORD), 2(LINE), 3(PHRASE).
            pages (list, optional):To get token_type_value Json data for specific page(s) from list
                of pages. Default is empty list.
            scaling_factor (SCALING_FACTOR, optional): Token data saved to json file after Scaling to
                given number. Defaults to SCALING_FACTOR.

        Returns:
            dict: Dict of saved info.
        """
        res_data = self.get_tokens_from_ocr(
            token_type_value=token_type_value, pages=pages, scaling_factor=scaling_factor)
        is_saved, error = FileUtil.save_to_json(out_file, res_data)
        return Response.save_res(is_saved, error)

    def get_bbox_for(self, region_definition=[REG_DEF_DICT],
                     subtract_region_definition=[[REG_DEF_DICT]],
                     scaling_factor=SCALING_FACTOR) -> list:
        """Get the relative region of given region definition by parsing the OCR file(s).
        Returns [X1,Y1,W,H] bbox of 'anchor-text', If 'anchorPoint1' and 'anchorPoint2' provided
        then 'anchorText' bbox calculated based on that.

        Args:
            region_definition ([REG_DEF_DICT], optional): List of `REG_DEF_DICT` to find relative region.
                `REG_DEF_DICT`:
                - `anchorText` - Text to search for in ocr.
                - `pageNums` - page numbers to look for the `anchorText` in the doc.
                - `anchorPoint1` & `anchorPoint2` - A point placed inside/on/outside the
                bounding box of the anchor-text using location properties.
                It accepts unit as **pixels** (Eg. 30, '30', '30px')
                or **percent** (Eg. '30%a'- 30% of page dimension or '30%r' - 30% from `anchorText`
                to the end of page) or **text width/height** (Eg. '30t' based on direction).
                - `anchorTextMatch` - Accepts pattern `matchMethod` and its `similarityScore`.
                Also accepts `maxWordSpace` with unit as **pixels** (Eg. 30, '30', '30px')
                or **percent** (Eg. '30%')
                or **text height** (Eg. '30t').
                - `pageDimensions` - `width` and `height` of the page.
                 Defaults to [REG_DEF_DICT].
            subtract_region_definition ([[REG_DEF_DICT]], optional): 2d List of `REG_DEF_DICT` to subtract
                region from interested regions. E.g Subtract Header/ Footer region.
                Defaults to [[REG_DEF_DICT]].
            scaling_factor (SCALING_FACTOR, optional): Token data saved to json file after Scaling to given
                number. Defaults to SCALING_FACTOR.

        Raises:
            Exception: Raises an Exception

        Returns:
            list: List of regions dict that contains anchorText bbox and interested area bbox.
        """
        try:
            # Private function for field validation
            def __validate_region_definition(reg_def_dict, parameter_name):
                invalid_keys = CommonUtil.get_invalid_keys(
                    REG_DEF_DICT, reg_def_dict)
                if len(invalid_keys) > 0:
                    error_text = f"Invalid keys found in {parameter_name}: {invalid_keys}. "
                    return error_text
                return ''
            validation_error = ''
            # Validate incoming region_definition dictionary
            if isinstance(region_definition, list):
                reg_def_temp = []
                for reg_def_entry in region_definition:
                    validation_error += __validate_region_definition(
                        reg_def_entry, 'region_definition')
                    reg_def_temp.append(FileUtil.get_updated_config_dict(
                        reg_def_entry, REG_DEF_DICT))
                region_definition = reg_def_temp

            # Validate incoming subtract_region_definition dictionary
            if isinstance(subtract_region_definition, list):
                subtract_region_temp = []
                for region_entry in subtract_region_definition:
                    reg_def_temp = []
                    if isinstance(region_entry, list):
                        for reg_def_entry in region_entry:
                            validation_error += __validate_region_definition(
                                reg_def_entry, 'subtract_region_definition')
                            reg_def_temp.append(FileUtil.get_updated_config_dict(
                                reg_def_entry, REG_DEF_DICT))
                        subtract_region_temp.append(reg_def_temp)
                subtract_region_definition = subtract_region_temp

            if len(validation_error) > 0:
                return Response.response(error=validation_error.strip())

            response_regions = None
            scaling_factors_key = '1.0_1.0'
            region_definition, warnings, rd_scaling_factor = CommonUtil.scaling_region_points_for(
                region_definition, self._ocr_helper_obj.get_page_bbox_dict())
            if len(region_definition) == 1:
                reg_def = region_definition[0]
                a_txt = OcrValidator.get_val(RegLabel.A_TXT, reg_def)
                is_empty_txt = True if len(
                    a_txt) == 0 else False
                # validate anchor_text
                if is_empty_txt is False:
                    OcrValidator.validate_anc_txt_arr(a_txt)
                a_point_1 = OcrValidator.check_for_None(OcrValidator.get_val(
                    RegLabel.A_POINT_1, reg_def))
                a_point_2 = OcrValidator.check_for_None(OcrValidator.get_val(
                    RegLabel.A_POINT_2, reg_def))
                # Validation 1. Needed max two point and providing both
                # left and right or top and bottom points not allowed
                OcrValidator.validate_point_count(a_point_1)
                OcrValidator.validate_point_count(a_point_2)
                # Validation 2. Non % str not allowed
                OcrValidator.validate_anc_points(a_point_1, is_empty_txt)
                OcrValidator.validate_anc_points(a_point_2, is_empty_txt)
                # Validation 3. Is anyone exist
                OcrValidator.validate_is_anyone_exist(
                    a_point_1, a_point_2)
                # anchorTextMatch in reg def
                anchorTextMatch = OcrValidator.validate_and_get_anc_txt_match(
                    reg_def, self._match_method, self._similarity_score)
                lookup_pages = CommonUtil.get_lookup_pages(
                    reg_def, self._ocr_helper_obj.get_page_bbox_dict())
                # maxWordSpace validation
                max_word_space = OcrValidator.validate_max_word_space(
                    reg_def['anchorTextMatch']['maxWordSpace'])
                # Get bbox
                response_regions = self._ocr_helper_obj.derive_1_anc_bbox_from(
                    a_txt, a_point_1, a_point_2, anchorTextMatch,
                    lookup_pages, scaling_factors_key, warnings, max_word_space)
            elif len(region_definition) == 2:
                reg_def_1 = region_definition[0]
                reg_def_2 = region_definition[1]
                try:
                    a_txt_1 = OcrValidator.validate_and_get_anc_txt(
                        RegLabel.A_TXT, reg_def_1)
                    a_txt_2 = OcrValidator.validate_and_get_anc_txt(
                        RegLabel.A_TXT, reg_def_2)
                except Exception as e:
                    raise Exception("Two "+RegLabel.A_TXT+" are required.")
                a_point_1 = OcrValidator.check_for_None(OcrValidator.get_val(
                    RegLabel.A_POINT_1, reg_def_1))
                a_point_2 = OcrValidator.check_for_None(OcrValidator.get_val(
                    RegLabel.A_POINT_1, reg_def_2))

                # Validation 1. Needed max two point and Providing both left and right points not allowed
                OcrValidator.validate_point_count(a_point_1)
                OcrValidator.validate_point_count(a_point_2)
                # Validation 2. Non % str not allowed
                OcrValidator.validate_anc_points(a_point_1)
                OcrValidator.validate_anc_points(a_point_2)
                # Validation 3. Is anyone exist
                OcrValidator.validate_is_anyone_exist(
                    a_point_1, a_point_2, p2_def="anchorPoint1")
                # anchorTextMatch in reg def_1
                anchorTextMatch_1 = OcrValidator.validate_and_get_anc_txt_match(
                    reg_def_1, self._match_method, self._similarity_score)
                # anchorTextMatch in reg def_2
                anchorTextMatch_2 = OcrValidator.validate_and_get_anc_txt_match(
                    reg_def_2, self._match_method, self._similarity_score)
                lookup_pages = [
                    CommonUtil.get_lookup_pages(
                        reg_def_1, self._ocr_helper_obj.get_page_bbox_dict()),
                    CommonUtil.get_lookup_pages(reg_def_2, self._ocr_helper_obj.get_page_bbox_dict())]
                # max_word_space in reg_defs
                max_word_space_1 = OcrValidator.validate_max_word_space(
                    reg_def_1['anchorTextMatch']['maxWordSpace'])
                max_word_space_2 = OcrValidator.validate_max_word_space(
                    reg_def_2['anchorTextMatch']['maxWordSpace'])
                # get bbox
                response_regions = self._ocr_helper_obj.derive_2_anc_bbox_from(
                    a_txt_1, a_txt_2, a_point_1, a_point_2, anchorTextMatch_1,
                    anchorTextMatch_2, lookup_pages, scaling_factors_key, warnings,
                    max_word_space_1, max_word_space_2)
            if not response_regions["error"] and len(subtract_region_definition) > 0 and \
                    subtract_region_definition != [[REG_DEF_DICT]]:
                subract_bbox_list = []
                for sub_reg_def in subtract_region_definition:
                    # recursive call
                    subract_bbox_list.append(self.get_bbox_for(
                        sub_reg_def, []))
                response_regions = self._ocr_helper_obj.subtract_region_from_attribute_region(
                    subract_bbox_list, response_regions, scaling_factors_key)

            scaling_factors_key = OcrValidator.validate_and_convert_scaling_factor(
                scaling_factor)
            occurance_response_regions = {}
            if len(region_definition[0]['anchorTextMatch']['occurrenceNums']) == 0:
                occurance_response_regions = response_regions
            else:
                reg_len = len(response_regions['regions'])
                new_region = []
                for i in region_definition[0]['anchorTextMatch']['occurrenceNums']:
                    if i > reg_len or i <= 0:
                        raise Exception(
                            f"Occurance number should be between 1 and {reg_len}")
                    new_region.append(response_regions['regions'][i-1])
                occurance_response_regions = dict(
                    {"regions": new_region, 'error': response_regions['error'], 'warnings': response_regions['warnings']})

            return Response.update_get_bbox_for_response(occurance_response_regions, 'scalingFactor', rd_scaling_factor, scaling_factors_key)
        except Exception as e:
            return Response.response(error=e.args[0])

    def calculate_scaling_factor(self, image_width: int = 0, image_height: int = 0, page: int = 0) -> dict:
        """Calculate and Return the Scaling Factor of given image

        Args:
            image_width (int, optional): Value of image width. Default is 0.
            image_height (int, optional): Value of image height. Default is 0.
            page (int, optional): Page of Pages. Defaul is 0.

        Returns:
            dict: Dict of calculated scaling factor and warnings(if any).
        """
        sf_ver, sf_hor, warn_msg = CommonUtil.calc_scaling_factor(
            image_width, image_height, self._ocr_helper_obj.get_page_bbox_dict(), page=int(page))
        # return {"scalingFactor": scaling_factor, "warnings": [warn_msg]}
        return {'scalingFactor': {'ver': sf_ver, 'hor': sf_hor}, 'warnings': [warn_msg]}

    def get_nearby_tokens(self,
                          anchor_txt_dict: ANCHOR_TXT_DICT,
                          token_type_value: int = 3,
                          token_count: int = 1,
                          token_min_alignment_threshold: float = 0.5,
                          scaling_factor=SCALING_FACTOR):
        """It returns a ordered list of tokens in all four directions (top, left, bottom, right) from a given
            anchor text. The numbeer of tokens returned in each direction can be set using `token_count`

        Args:
            anchor_txt_dict (ANCHOR_TXT_DICT): Anchor text info around which nearby tokens are to be searched.
            token_type_value (int, optional): 1(WORD), 2(LINE), 3(PHRASE). Defaults to 3.
            token_count (int, optional): Count of nearby tokens to be returned. Defaults to 1.
            token_min_alignment_threshold (float, optional): Percent of anchor text aligned with nearby tokens.
                The value ranges from 0 to 1. If the threshold is set to 0, it means the nearby token
                should completely be within the width/height of the anchor text (Eg. anchor_text_bbox =[10,10,100,20],
                then nearby top token should be above the anchor text and between the lines, x=10 and x=110). For
                threshold between 0 to 1, nearby token should align atleast the given threshold of anchor text (Eg.
                anchor_text_bbox=[10,10,100,20] and threshold=0.5, then nearby top should atleast align with 50px
                of anchor text(either side), which is 0.5(threshold) of anchor text width). For threshold 1, the token
                should start from anchortext's start position or before and end at anchortext's end poition or after.
                Defaults to 0.5.
            scaling_factor (SCALING_FACTOR, optional): Token data saved to json file after Scaling to given number.
             Defaults to SCALING_FACTOR.

        Raises:
            Exception: Raises an Exception if the method is not implemented

        Returns:
            list: info of nearby tokens
        """
        try:
            # Private function for field validation
            def __validate_region_definition(anchor_txt_dict, parameter_name):
                invalid_keys = CommonUtil.get_invalid_keys(
                    ANCHOR_TXT_DICT, anchor_txt_dict)
                if len(invalid_keys) > 0:
                    error_text = f"Invalid keys found in {parameter_name}: {invalid_keys}. "
                    return error_text
                return ''

            validation_error = ''
            # Validate incoming anchor_txt_dict dictionary
            if isinstance(anchor_txt_dict, dict):
                validation_error += __validate_region_definition(
                    anchor_txt_dict, 'anchor_txt_dict')
                anchor_txt_dict = FileUtil.get_updated_config_dict(
                    anchor_txt_dict, ANCHOR_TXT_DICT)

            if len(validation_error) > 0:
                return Response.response(error=validation_error.strip())
            scaling_factor = OcrValidator.validate_and_convert_scaling_factor(
                scaling_factor)
            distance = anchor_txt_dict['distance']
            del anchor_txt_dict['distance']
            response = self.get_bbox_for(
                [anchor_txt_dict])
            key, error = response['regions'], response['error']
            if key == []:
                raise Exception(error)
            output = self._ocr_helper_obj.get_nearby_tokens(
                key, anchor_txt_dict, token_type_value,
                token_count, token_min_alignment_threshold, scaling_factor, distance)
            return Response.token_response(output)
        except Exception as e:
            error = traceback.format_exc()
            return Response.token_response(error=e.args[0])

    def plot(self, plot_data: PLOT_DATA) -> list:
        '''plotting the bbox and saving the image'''
        response_list = []
        token_type_value = plot_data['token_type_value']
        images_data_list = plot_data['images']
        page_list = [x['image_page_num'] for x in images_data_list]
        tokens_list = self.get_tokens_from_ocr(
            token_type_value=token_type_value, pages=page_list)
        for image_data in images_data_list:
            image_file_path = image_data['image_file_path']
            if not os.path.exists(image_file_path):
                raise FileNotFoundError(f'{image_file_path} does not exist')
            page_level_tokens_list = [x for x in tokens_list if
                                      x['page'] == image_data['image_page_num']
                                      and x['text'].strip() != '']
            # draw and save image bbox
            bbox_img_path = self.__draw_bbox(
                image_file_path, page_level_tokens_list)
            response_list.append({
                "image_page_num": image_data['image_page_num'],
                "image_file_path": image_file_path,
                "output_image_file_path": bbox_img_path
            })
        return response_list

    def __draw_bbox(self, image_file_path: str, tokens: list):
        img_path = image_file_path
        alpha = 0.4  # Transparency factor.
        file_extension = os.path.splitext(img_path)[-1]
        bbox_img_file_path = f'{os.path.dirname(img_path)}/{os.path.basename(img_path)}_bbox{file_extension}'
        font = cv2.FONT_HERSHEY_SIMPLEX
        # token bbox image drawn
        image_bbox = cv2.imread(img_path)
        transparent = image_bbox.copy()
        token_bbox_list = [x['bbox'] for x in tokens]

        if token_bbox_list:
            for idx, bbox in enumerate(token_bbox_list):
                # text,bbox=bbox_text
                _color_dict = copy.deepcopy(PlotBbox.COLOR_DICT)
                _idx = idx % len(PlotBbox.COLOR_NAMES)
                color_name = PlotBbox.COLOR_NAMES[_idx]
                _color_code = _color_dict[color_name]
                _org_color_code = copy.deepcopy(_color_code)
                _color_code.append(50)
                start, end = (bbox[0], bbox[1]), (bbox[2] +
                                                  bbox[0], bbox[3]+bbox[1])
                cv2.rectangle(img=transparent, pt1=start, pt2=end,
                              color=tuple(_org_color_code), thickness=-1)
                cv2.putText(img=image_bbox, text=f"{start},{end}", org=(int(
                    (start[0]+end[0])/2), start[1]-5), fontFace=font, fontScale=0.5, color=(255, 0, 0))
                image_new = cv2.addWeighted(
                    transparent, alpha, image_bbox, 1 - alpha, 0)
        imsave(bbox_img_file_path, image_new)
        return bbox_img_file_path

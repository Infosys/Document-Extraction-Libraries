# ===============================================================================================================#
# Copyright 2021 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import copy
import re
import logging
import itertools
from infy_ocr_parser.internal.response import Response
from infy_ocr_parser.internal.ocr_const import *
from infy_ocr_parser.internal.common_util import CommonUtil
from collections import Counter
from math import sqrt


class OcrHelper:
    """Helper class for OcrParser"""
    __logging = logging

    def __init__(self, logger, ocr_handler_obj, max_word_space):
        self.__logger = logger
        self._ocr_handler_obj = ocr_handler_obj
        self._max_word_space = max_word_space
        self.init_ocr_tokens()
        self._page_bbox_dict_list = self._ocr_handler_obj.get_page_bbox_dict()

    def init_ocr_tokens(self):
        self._word_token_dict = {}
        self._line_token_dict = {}
        self._phrase_token_dict = {}
        scaling_factors_key = f'{float(1)}_{float(1)}'
        sf_max_word_space = f'{scaling_factors_key}_{(self._max_word_space)}'
        self._word_token_dict[scaling_factors_key] = self.get_tokens_from_ocr(
            token_type_value=TokenType.WORD.value, scaling_factors_key=scaling_factors_key)
        self._phrase_token_dict[sf_max_word_space] = self.get_tokens_from_ocr(
            token_type_value=TokenType.PHRASE.value, scaling_factors_key=scaling_factors_key, max_word_space=self._max_word_space)
        self._line_token_dict[scaling_factors_key] = self.get_tokens_from_ocr(
            token_type_value=TokenType.LINE.value, scaling_factors_key=scaling_factors_key)

    def subtract_region_from_attribute_region(self, sub_region_bbox_list, attr_reg_bbox, scaling_factors_key):
        for sub_region_bbox_obj in sub_region_bbox_list:
            if sub_region_bbox_obj[ResProp.ERROR]:
                return sub_region_bbox_obj
            sub_reg_list = self._get_region_bbox_list_from(sub_region_bbox_obj)
            for attr_regions_obj in attr_reg_bbox[ResProp.REGIONS]:
                for attr_reg_obj in attr_regions_obj[ResProp.REG_BBOX]:
                    p_bbox = [p_bbox_obj[ResProp.BBOX]
                              for p_bbox_obj in self._page_bbox_dict_list if int(p_bbox_obj[ResProp.PAGE]) == attr_reg_obj[ResProp.PAGE]]
                    sub_bbox_page_wise_list = [sub_region_obj[ResProp.BBOX]
                                               for sub_region_obj in sub_reg_list if sub_region_obj[ResProp.PAGE] == attr_reg_obj[ResProp.PAGE]]
                    for sub_bbox_page_wise in sub_bbox_page_wise_list:
                        al, at, aw, ah = attr_reg_obj[ResProp.BBOX]
                        _, st, _, sh = sub_bbox_page_wise
                        _, pt, _, ph = p_bbox[0]
                        a_bottom, s_bottom = at+ah, st+sh
                        p_bottom = pt+ph
                        a_bottom = p_bottom if a_bottom > p_bottom else a_bottom
                        s_bottom = p_bottom if s_bottom > p_bottom else s_bottom

                        is_at_overlapping_sub_reg = (
                            at < s_bottom and at >= st)
                        is_ab_overlapping_sub_reg = (
                            a_bottom <= s_bottom and a_bottom > st)
                        is_sub_reg_inside_interest_reg = (
                            at < st and a_bottom > s_bottom)
                        is_interest_reg_inside_sub_reg = (
                            is_at_overlapping_sub_reg and is_ab_overlapping_sub_reg)
                        is_both_overlapping = (
                            at == st and a_bottom == s_bottom)

                        if is_at_overlapping_sub_reg:
                            # Subtract region of interest area when its intersecting to subtract region.
                            at = abs(at-sh)
                            attr_reg_obj[ResProp.BBOX] = [al, at, aw, ah]

                        if is_ab_overlapping_sub_reg:
                            # Subtract region of interest area when its intersecting to subtract region.
                            ah = abs(at-st)
                            attr_reg_obj[ResProp.BBOX] = [al, at, aw, ah]

                        if is_sub_reg_inside_interest_reg:
                            # Divide interest region by subracting region.
                            within_text = [t['text'] for t in self.get_tokens_from_ocr(
                                3, within_bbox=[al, at, aw, abs(st-at)])]
                            new_attr_reg_obj_1 = Response.res_reg_bbox(within_text,
                                                                       [al, at, aw, abs(st-at)], attr_reg_obj[ResProp.PAGE], scaling_factors_key)
                            within_text = [t['text'] for t in self.get_tokens_from_ocr(
                                3, within_bbox=[al, s_bottom, aw, abs(a_bottom-s_bottom)])]
                            new_attr_reg_obj_2 = Response.res_reg_bbox(within_text, [al, s_bottom, aw, abs(
                                a_bottom-s_bottom)], attr_reg_obj[ResProp.PAGE], scaling_factors_key)
                            attr_regions_obj[ResProp.REG_BBOX].append(
                                new_attr_reg_obj_1)
                            attr_regions_obj[ResProp.REG_BBOX].append(
                                new_attr_reg_obj_2)

                        if is_sub_reg_inside_interest_reg or is_both_overlapping or is_interest_reg_inside_sub_reg:
                            # Remove region of interest area when its fully inside subtract region.
                            attr_regions_obj[ResProp.REG_BBOX].remove(
                                attr_reg_obj)

        return attr_reg_bbox

    def get_phrases_from_words(self, ocr_word_dict=[], within_bbox=[], pages=[], scaling_factors_key='1.0_1.0', phrase_dict_list=[], max_word_space=None):
        '''
        Desc:
        ---------
        It groups words as a phrase by assuming the distance between two words
        to not be greater than than the word's fontsize(height)
        Returns a dictionary of phrases as key and its bbox as value
        -----------------------------------
        '''
        if(ocr_word_dict != [] and within_bbox != []):
            raise Exception(
                "Either provide ocr_word_dict or within_bbox, not both")
        if len(ocr_word_dict) == 0:
            # If the caller not given ocr_word_list to filter then use existing document phrase_dict_list if any
            if len(phrase_dict_list) > 0 and len(within_bbox) == 0:
                if len(pages) == 0:
                    return phrase_dict_list
                else:
                    return [ocr_phrase_obj for ocr_phrase_obj in phrase_dict_list if ocr_phrase_obj["page"] in pages]
            ocr_word_dict = self.get_tokens_from_ocr(
                token_type_value=TokenType.WORD.value, scaling_factors_key=scaling_factors_key, max_word_space=max_word_space)
        if len(within_bbox) > 0:
            ocr_word_dict = self._filter_words_from_region(
                within_bbox, word_dict_list=ocr_word_dict)
        ocr_word_dict.sort(key=lambda x: (x.get("bbox")[OcrConstants.BB_X]))
        phrases_dict_list = []
        words_done = []
        flag = False
        for t in ocr_word_dict:
            if len(pages) > 0 and t["page"] not in pages:
                continue
            word_dict = []
            text = t.get("text")
            if text == '':
                words_done.append(t)
                continue
            t_x = t.get("bbox")[OcrConstants.BB_X]
            t_y = t.get("bbox")[OcrConstants.BB_Y]
            t_w = t.get("bbox")[OcrConstants.BB_W]
            t_h = t.get("bbox")[OcrConstants.BB_H]
            word_space = self._get_max_word_space(
                max_word_space, t["page"], t_h)
            if(t not in words_done):
                words_done.append(t)
                word_dict.append(t)
                # declaring x, y and height of the entire phrase
                x = t_x
                y = t_y
                h = t_h
                for b in ocr_word_dict:
                    if(b['page'] == t['page']):
                        b_x = b.get("bbox")[OcrConstants.BB_X]
                        b_y = b.get("bbox")[OcrConstants.BB_Y]
                        b_w = b.get("bbox")[OcrConstants.BB_W]
                        b_h = b.get("bbox")[OcrConstants.BB_H]
                        if b.get("text") == '':
                            words_done.append(t)
                            continue
                        # matches t with the current word(b) and adds to phrase if space between the two words
                        # is less than the height of the word and if the y-coordinate of current word is in the range
                        # of t's (y-coordinate-t's height) and t's (y-coordinate+t's height)
                        # and also that word is not present in the words_done list
                        if((t_x+t_w) < b_x <= (t_x+t_w+word_space) and (t_y) <= b_y+b_h/2 <= (t_y+t_h) and
                           (b not in words_done)):
                            text = text+" "+b.get("text")
                            word_dict.append(b)
                            # if the condition is true then t's bbox is updated to the current word's bbox(b)
                            t_x, t_y, t_w, t_h = b_x, b_y, b_w, b_h
                            # updating y-coordinate and height of the phrase
                            # if(t_y < y):
                            #     y = t_y
                            # if(h < t_h):
                            y, h = self._update_text_bbox((y, h), (b_y, b_h))
                            # h = t_h
                            words_done.append(b)
                            flag = True
                # once all the words gets added to the that phrase if updates the final width and height of the phrase
                if(flag == True):
                    w = (t_x+t_w-x)
                else:
                    w, h = (t_x+t_w-x), t_h
                flag = False
                phrases_dict_list.append(
                    Response.data_dict(
                        f"phrase_{t.get('page')}_{x}_{y}_{w+x}_{h+y}",
                        t.get("page"),
                        text,
                        [x, y, w, h],
                        scaling_factors_key,
                        word_structure=word_dict
                    )
                )
        return phrases_dict_list

    def get_tokens_from_ocr(self, token_type_value, within_bbox=[], ocr_word_list=[], pages=[], scaling_factors_key='1.0_1.0', max_word_space=None):
        scaling_factor_ver, scaling_factor_hor = [
            float(i) for i in scaling_factors_key.split('_')]
        if (token_type_value == TokenType.LINE.value):
            line_dict_list = self._line_token_dict.get(scaling_factors_key, [])
            if scaling_factor_ver != 1.0 and scaling_factor_hor != 1.0 and len(line_dict_list) == 0:
                # scale the already existing default scaling factor 1 dict, this was created while init load
                line_dict_list = CommonUtil.scaling_bbox_for(
                    copy.deepcopy(self._line_token_dict.get('1.0_1.0')), scaling_factor_ver, scaling_factor_hor)
                self._line_token_dict[scaling_factors_key] = line_dict_list
            return self._ocr_handler_obj.get_line_dict_from(pages=pages, line_dict_list=line_dict_list, scaling_factors=[scaling_factor_ver, scaling_factor_hor])
        elif (token_type_value == TokenType.WORD.value):
            word_dict_list = self._word_token_dict.get(scaling_factors_key, [])
            if scaling_factor_ver != 1.0 and scaling_factor_hor != 1.0 and len(word_dict_list) == 0:
                # scale the already existing default scaling factor 1 dict, this was created while init load
                word_dict_list = CommonUtil.scaling_bbox_for(
                    copy.deepcopy(self._word_token_dict.get('1.0_1.0')), scaling_factor_ver, scaling_factor_hor)
                self._word_token_dict[scaling_factors_key] = word_dict_list
            if within_bbox and len(within_bbox) > 0:
                return self._filter_words_from_region(to_bbox=within_bbox, pages=pages, word_dict_list=word_dict_list)
            else:
                return self._ocr_handler_obj.get_word_dict_from(pages=pages, word_dict_list=word_dict_list, scaling_factors=[scaling_factor_ver, scaling_factor_hor])
        elif (token_type_value == TokenType.PHRASE.value):
            sf_max_word_space = f'{scaling_factors_key}_{(max_word_space)}'
            phrase_dict_list = self._phrase_token_dict.get(
                sf_max_word_space, [])
            if len(ocr_word_list) == 0 and scaling_factor_ver != 1.0 and scaling_factor_hor != 1.0 and len(phrase_dict_list) == 0:
                # scale the already existing default scaling factor 1 dict, this was created while init load
                phrase_dict_list = CommonUtil.scaling_bbox_for(
                    copy.deepcopy(self._phrase_token_dict.get(f'1.0_1.0_1.5t')), scaling_factor_ver, scaling_factor_hor)
                self._phrase_token_dict[sf_max_word_space] = phrase_dict_list
            return self.get_phrases_from_words(ocr_word_list, within_bbox, pages=pages,
                                               scaling_factors_key=scaling_factors_key, phrase_dict_list=phrase_dict_list, max_word_space=max_word_space)

    def derive_1_anc_bbox_from(self, anchor_txt, a_point_1, a_point_2, anchorTextMatch, lookup_pages, scaling_factors_key, warnings, max_word_space):
        res_regions, error = [], None
        try:
            anchor_txt_bbox_lst, is_a_text_empty = [], False
            is_empty_txt = True if len(
                anchor_txt) == 0 else False
            if not is_empty_txt:
                # Get anchor text bbox
                anchor_txt_bbox_lst, error = self._get_anchor_text_regions(
                    anchor_txt, anchorTextMatch, lookup_pages, scaling_factors_key, max_word_space)
                if error:
                    raise Exception(error)
            else:
                # Get Page bbox
                anchor_txt_bbox_lst = [
                    p_bbox_obj for p_bbox_obj in self._page_bbox_dict_list if p_bbox_obj[OcrConstants.PAGE] in lookup_pages]
                is_a_text_empty = True
            anc_txt_bbox = []
            # return res for with/without anchor1 and anchor2 points.
            for anchor_txt_bbox_obj in anchor_txt_bbox_lst:
                anchor_txt_bbox = copy.copy(anchor_txt_bbox_obj[ResProp.BBOX])
                res_bbox = anchor_txt_bbox
                token_type = anchor_txt_bbox_obj.get('token_type', 'phrase')
                page_num = anchor_txt_bbox_obj[ResProp.PAGE]
                if a_point_1 and a_point_2:
                    labeled_anc_bbox = self._get_labeled_bbox(anchor_txt_bbox)
                    x1, y1 = self._get_point_for(anchor_txt, a_point_1, copy.copy(
                        labeled_anc_bbox), page_num, is_empty_a_txt=is_a_text_empty)
                    x2, y2 = self._get_point_for(anchor_txt, a_point_2, copy.copy(
                        labeled_anc_bbox), page_num, is_empty_a_txt=is_a_text_empty)
                    res_bbox = CommonUtil.get_rect_point_for(x1, y1, x2, y2)
                within_text = [t['text'] for t in self.get_tokens_from_ocr(
                    3, within_bbox=res_bbox, scaling_factors_key=scaling_factors_key, max_word_space=max_word_space)]
                res_reg_bbox = [Response.res_reg_bbox(
                    within_text, res_bbox, page_num, scaling_factors_key)]
                actual_text = [t['text'] for t in self.get_tokens_from_ocr(
                    3, within_bbox=anchor_txt_bbox, scaling_factors_key=scaling_factors_key, max_word_space=max_word_space)]
                res_regions.append(Response.response_regions(
                    [Response.res_at_bbox(anchor_txt, actual_text, token_type, anchor_txt_bbox, scaling_factors_key)], res_reg_bbox))
        except Exception as e:
            res_regions, error = [], e.args[0]
        return Response.response(res_regions, error, warnings)

    def derive_2_anc_bbox_from(self, anchor_txt_1, anchor_txt_2, anchor_point_1, anchor_point_2,
                               anchorTextMatch_1, anchorTextMatch_2, lookup_pages, scaling_factors_key, warnings, max_word_space_1, max_word_space_2):
        res_regions, error = [], None
        try:
            # Get anchor text bbox
            anchor_txt_bbox_1_lst, error1 = self._get_anchor_text_regions(
                anchor_txt_1, anchorTextMatch_1, lookup_pages[0], scaling_factors_key, max_word_space_1)
            if error1:
                raise Exception(error1)
            anchor_txt_bbox_2_lst, error2 = self._get_anchor_text_regions(
                anchor_txt_2, anchorTextMatch_2, lookup_pages[1], scaling_factors_key, max_word_space_2)
            if error2:
                raise Exception(error2)
            # anchor1 top lesser than anchor2
            anchor_txt_bbox_1_lst.sort(
                key=lambda x: (x[ResProp.BBOX][1]), reverse=True)
            anchor_txt_bbox_2_lst.sort(key=lambda x: (x[ResProp.BBOX][1]))
            res_regions_1 = self._get_bbox_from_2anc_point(
                copy.copy(anchor_txt_bbox_1_lst), copy.copy(
                    anchor_txt_bbox_2_lst),
                anchor_point_1, anchor_point_2, anchor_txt_1, anchor_txt_2, scaling_factors_key, max_word_space_1)
            # anchor2 top lesser than anchor1
            anchor_txt_bbox_1_lst.sort(key=lambda x: (x[ResProp.BBOX][1]))
            anchor_txt_bbox_2_lst.sort(
                key=lambda x: (x[ResProp.BBOX][1]), reverse=True)
            res_regions_2 = self._get_bbox_from_2anc_point(
                copy.copy(anchor_txt_bbox_2_lst), copy.copy(
                    anchor_txt_bbox_1_lst),
                anchor_point_2, anchor_point_1, anchor_txt_2, anchor_txt_1, scaling_factors_key, max_word_space_2)
            res_regions = res_regions_1 + res_regions_2
            temp_reg_bbox = []
            unique_res_regions = []
            for res_reg in res_regions:
                bb = res_reg[ResProp.REG_BBOX]
                bb.sort(key=lambda x: (x[ResProp.BBOX][1]))
                if bb not in temp_reg_bbox:
                    temp_reg_bbox.append(bb)
                    unique_res_regions.append(res_reg)
            res_regions = unique_res_regions
        except Exception as e:
            res_regions, error = [], e.args[0]
        return Response.response(res_regions, error, warnings)

    def get_nearby_tokens(
            self, key, anchor_txt_dict, token_type_value,
            token_count, token_alignment_threshold,
            scaling_factors_key, distance_dict):
        output = []
        tokens = self.get_tokens_from_ocr(
            token_type_value, scaling_factors_key=scaling_factors_key)
        for token in tokens:
            if token.get('words') is not None:
                del token['words']
            else:
                break
        tokens_bbox = [t.get('bbox') for t in tokens]
        for i in range(len(key)):
            page_bbox = self._get_page_bbox_for(
                key[i]['regionBBox'][0]['page'])
            key_bbox = key[i]['regionBBox'][0]['bbox']
            key_text = [t['text'] for t in self.get_tokens_from_ocr(
                3, within_bbox=key_bbox, scaling_factors_key=scaling_factors_key)]
            result = {'top': {'tokens': []}, 'left': {'tokens': []},
                      'right': {'tokens': []}, 'bottom': {'tokens': []}}
            for num in range(token_count):
                if num == 0:
                    closest_phrase_r = closest_phrase_l = closest_phrase_t = closest_phrase_b = key[
                        i]['regionBBox'][0]['bbox']
                    key_box = key_bbox
                closest_phrase_r = self._get_closest_fieldbox(
                    tokens_bbox, 'right', closest_phrase_r, key_box, token_alignment_threshold)
                closest_phrase_l = self._get_closest_fieldbox(
                    tokens_bbox, 'left', closest_phrase_l, key_box, token_alignment_threshold)
                closest_phrase_t = self._get_closest_fieldbox(
                    tokens_bbox, 'top', closest_phrase_t, key_box, token_alignment_threshold)
                closest_phrase_b = self._get_closest_fieldbox(
                    tokens_bbox, 'bottom', closest_phrase_b, key_box, token_alignment_threshold)

                for token in tokens:
                    if key_bbox == token.get('bbox'):
                        continue
                    if(token.get("bbox") == closest_phrase_r):
                        r_dist = page_bbox[2] if distance_dict['right'] is None else self._get_point_calc_from_measurement_unit(
                            distance_dict['right'], False, self._get_labeled_bbox(
                                key_bbox),
                            'right', key[i]['regionBBox'][0]['page']) - key_bbox[0] - key_bbox[2]
                        if num == 0 and r_dist >= (closest_phrase_r[0]-key_bbox[0]-key_bbox[2]):
                            result['right']['regionBbox'] = closest_phrase_r
                            result['right']['tokens'].append(token)
                        elif len(result['right'].get('tokens', [])) > 0 and \
                                r_dist >= (closest_phrase_r[0]-result['right']['regionBbox'][0]-result['right']['regionBbox'][2]):
                            if token == result['right']['tokens'][-1]:
                                continue
                            y, h = self._update_text_bbox(
                                (result['right']['regionBbox'][1],
                                    result['right']['regionBbox'][3]),
                                (closest_phrase_r[1], closest_phrase_r[3]))
                            x = result['right']['regionBbox'][0]
                            w = closest_phrase_r[0]+closest_phrase_r[2] - \
                                result['right']['regionBbox'][0]
                            result['right']['regionBbox'] = [x, y, w, h]
                            result['right']['tokens'].append(token)
                    elif(token.get("bbox") == closest_phrase_b):
                        r_dist = page_bbox[3] if distance_dict['bottom'] is None else self._get_point_calc_from_measurement_unit(
                            distance_dict['bottom'], False, self._get_labeled_bbox(
                                key_bbox),
                            'bottom', key[i]['regionBBox'][0]['page']) - key_bbox[1] - key_bbox[3]
                        if num == 0 and r_dist >= (closest_phrase_b[1]-key_bbox[1]-key_bbox[3]):
                            result['bottom']['regionBbox'] = closest_phrase_b
                            result['bottom']['tokens'].append(token)
                        elif len(result['bottom'].get('tokens', [])) > 0 and \
                                r_dist >= (closest_phrase_b[1]-result['bottom']['regionBbox'][1]-result['bottom']['regionBbox'][3]):
                            if token == result['bottom']['tokens'][-1]:
                                continue
                            h = closest_phrase_b[1]+closest_phrase_b[3] - \
                                result['bottom']['regionBbox'][1]
                            y = result['bottom']['regionBbox'][1]
                            x, w = self._update_text_bbox(
                                (result['bottom']['regionBbox'][0],
                                    result['bottom']['regionBbox'][2]),
                                (closest_phrase_b[0], closest_phrase_b[2]))
                            result['bottom']['regionBbox'] = [x, y, w, h]
                            result['bottom']['tokens'].append(token)
                    elif(token.get("bbox") == closest_phrase_l):
                        r_dist = page_bbox[2] if distance_dict['left'] is None else self._get_point_calc_from_measurement_unit(
                            distance_dict['left'], False, self._get_labeled_bbox(
                                key_bbox),
                            'left', key[i]['regionBBox'][0]['page']) - key_bbox[0]
                        if num == 0 and r_dist >= (key_bbox[0]-closest_phrase_l[0]-closest_phrase_l[2]):
                            result['left']['regionBbox'] = closest_phrase_l
                            result['left']['tokens'].append(token)
                        elif len(result['left'].get('tokens', [])) > 0 and \
                                r_dist >= (result['left']['regionBbox'][0]-closest_phrase_l[0]-closest_phrase_l[2]):
                            if token == result['left']['tokens'][-1]:
                                continue
                            x = closest_phrase_l[0]
                            y, h = self._update_text_bbox(
                                (result['left']['regionBbox'][1],
                                    result['left']['regionBbox'][3]),
                                (closest_phrase_l[1], closest_phrase_l[3]))
                            w = result['left']['regionBbox'][0] + \
                                result['left']['regionBbox'][2] - \
                                closest_phrase_l[0]
                            result['left']['regionBbox'] = [x, y, w, h]
                            result['left']['tokens'].append(token)
                    elif(token.get("bbox") == closest_phrase_t):
                        r_dist = page_bbox[3] if distance_dict['top'] is None else self._get_point_calc_from_measurement_unit(
                            distance_dict['top'], False, self._get_labeled_bbox(
                                key_bbox),
                            'top', key[i]['regionBBox'][0]['page']) - key_bbox[1]
                        if num == 0 and r_dist >= (key_bbox[1]-closest_phrase_t[1] - closest_phrase_t[3]):
                            result['top']['regionBbox'] = closest_phrase_t
                            result['top']['tokens'].append(token)
                        elif len(result['top'].get('tokens', [])) > 0 and \
                                r_dist >= (result['top']['regionBbox'][1]-closest_phrase_t[1]-closest_phrase_t[3]):
                            if token == result['top']['tokens'][-1]:
                                continue
                            h = result['top']['regionBbox'][1] + \
                                result['top']['regionBbox'][3] - \
                                closest_phrase_t[1]
                            y = closest_phrase_t[1]
                            x, w = self._update_text_bbox(
                                (result['top']['regionBbox'][0],
                                    result['top']['regionBbox'][2]),
                                (closest_phrase_t[0], closest_phrase_t[2]))
                            result['top']['regionBbox'] = [x, y, w, h]
                            result['top']['tokens'].append(token)
            output.append(
                Response.res_nearby_tokens(
                    anchor_txt_dict['anchorText'], key_text, key_bbox, result)
            )
        return output

    def get_page_bbox_dict(self) -> list:
        return self._page_bbox_dict_list

    def _filter_words_from_region(self, to_bbox=[], pages=[], word_dict_list=[]):
        word_structure = []
        for i, word_obj in enumerate(word_dict_list):
            if len(pages) > 0 and word_obj["page"] not in pages:
                continue
            l, t, w, h = word_obj[OcrConstants.BBOX]
            pl, pt, pw, ph = to_bbox
            if l >= pl and l <= pl+pw and t >= pt and t <= pt+ph and \
                    l+w >= pl and l+w <= pl+pw and t+h >= pt and t+h <= pt+ph:
                word_structure.append(word_obj)
        return word_structure

    def _get_region_bbox_list_from(self, regions_obj_list):
        reg_list = []
        for reg_bb_list in regions_obj_list[ResProp.REGIONS]:
            reg_list += reg_bb_list[ResProp.REG_BBOX]
        return reg_list

    def _get_region(self, text, text_match_var='phrase', anchorTextMatch='normal', lookup_pages=[], scaling_factors_key=0, max_word_space=None):
        if text_match_var == 'phrase':
            max_word_space = '1.5t' if max_word_space is None else max_word_space
            phrase_dict_list = self.get_tokens_from_ocr(
                token_type_value=TokenType.PHRASE.value, scaling_factors_key=scaling_factors_key, max_word_space=max_word_space)
            if(anchorTextMatch[0] == 'regex'):
                return [
                    copy.deepcopy(item) for i, item in enumerate(phrase_dict_list) if item[OcrConstants.PAGE] in lookup_pages and re.search(text.lower(), item[OcrConstants.TXT].lower())]
            return [
                copy.deepcopy(item) for i, item in enumerate(phrase_dict_list) if item[OcrConstants.PAGE] in lookup_pages and len(self._cos_sim(text.lower(), item[OcrConstants.TXT].lower(), anchorTextMatch[1])) > 0]
        elif text_match_var == 'word':
            word_dict_list = self.get_tokens_from_ocr(
                token_type_value=TokenType.WORD.value, scaling_factors_key=scaling_factors_key, max_word_space=max_word_space)
            return [
                copy.deepcopy(item[OcrConstants.BBOX]) for i, item in enumerate(word_dict_list) if item[OcrConstants.PAGE] in lookup_pages and item[OcrConstants.TXT].lower() == text.lower()]
        else:
            line_dict_list = self.get_tokens_from_ocr(
                token_type_value=TokenType.LINE.value, scaling_factors_key=scaling_factors_key, max_word_space=max_word_space)
            return [
                copy.deepcopy(item) for i, item in enumerate(line_dict_list) if item[OcrConstants.PAGE] in lookup_pages and re.search(text.lower(), item[OcrConstants.TXT].lower())]

    def _cos_sim(self, text_1, text_2, similarity_score):
        start_word_pos_arr = []
        if(str(text_2).strip() == ''):
            return start_word_pos_arr
        txt_1_list, txt_2_list = text_1.split(' '), text_2.split(' ')
        start_word_pos_arr = []
        for i in range(len(txt_2_list)-len(txt_1_list)+1):
            match_text = ' '.join(txt_2_list[i:len(txt_1_list)+i])
            if(match_text == ''):
                continue

            v1, v2 = self._word_to_vec(text_1), self._word_to_vec(match_text)
            common = v1[1].intersection(v2[1])
            cos_dist = round(sum(v1[0][ch]*v2[0][ch]
                                 for ch in common)/v1[2]/v2[2], 3)
            if(cos_dist >= similarity_score):
                start_word_pos_arr.append(i)
        return start_word_pos_arr

    def _word_to_vec(self, word):
        # count the characters in word
        cw = Counter(word)
        # precomputes a set of the different characters
        sw = set(cw)
        # precomputes the "length" of the word vector
        lw = sqrt(sum(c*c for c in cw.values()))
        return cw, sw, lw

    def _get_match_text_region(self, match_txt, anchorTextMatch, lookup_pages, scaling_factors_key, max_word_space):
        res_regions = []
        match_txt = match_txt.lower()
        token_type = 'phrase'
        phrase_matched_bbox_list = self._get_region(
            match_txt, text_match_var='phrase', anchorTextMatch=anchorTextMatch,
            lookup_pages=lookup_pages, scaling_factors_key=scaling_factors_key,
            max_word_space=max_word_space)
        if len(phrase_matched_bbox_list) == 0:
            token_type = 'line'
            phrase_matched_bbox_list = self._get_region(
                match_txt, text_match_var='line', anchorTextMatch=anchorTextMatch,
                lookup_pages=lookup_pages, scaling_factors_key=scaling_factors_key,
                max_word_space=max_word_space)
            if len(phrase_matched_bbox_list) == 0:
                return phrase_matched_bbox_list
        for phrase_match_bbox in phrase_matched_bbox_list:
            if(anchorTextMatch[0] == 'regex'):
                start_char_pos_arr, end_char_pos_arr = [], []
                for m in re.finditer(match_txt, phrase_match_bbox[OcrConstants.TXT].lower()):
                    start_char_pos_arr.append(m.start(0))
                    end_char_pos_arr.append(m.end(0))
                space_pos_arr = [m.start(0) for m in re.finditer(
                    ' ', phrase_match_bbox[OcrConstants.TXT])]
                no_of_matches = start_char_pos_arr
            else:
                no_of_matches = start_word_pos_arr = self._cos_sim(
                    match_txt, phrase_match_bbox[OcrConstants.TXT].lower(), anchorTextMatch[1])
            for j in range(len(no_of_matches)):
                if(anchorTextMatch[0] == 'regex'):
                    diff_start_arr = [
                        start_char_pos_arr[j]-space_pos for space_pos in space_pos_arr if start_char_pos_arr[j]-space_pos > 0]
                    start_word_pos = 0 if diff_start_arr == [
                    ] else diff_start_arr.index(min(diff_start_arr))+1
                    diff_end_arr = [
                        end_char_pos_arr[j]-space_pos for space_pos in space_pos_arr if end_char_pos_arr[j]-space_pos > 0]
                    end_word_pos = 0 if diff_end_arr == [
                    ] else diff_end_arr.index(min(diff_end_arr))+1
                else:
                    start_word_pos, end_word_pos = start_word_pos_arr[j], start_word_pos_arr[j]+len(
                        match_txt.split(' '))-1
                l, t, h = phrase_match_bbox[OcrConstants.WORDS][start_word_pos][OcrConstants.BBOX][
                    0], phrase_match_bbox[OcrConstants.WORDS][start_word_pos][OcrConstants.BBOX][1], phrase_match_bbox[OcrConstants.WORDS][start_word_pos][OcrConstants.BBOX][3]
                for i in range(start_word_pos, end_word_pos+1):
                    # incase of more than one word anchor text then consider the lesser top for remaining all.
                    t, h = self._update_text_bbox(
                        (t, h),
                        (phrase_match_bbox[OcrConstants.WORDS][i][OcrConstants.BBOX][1],
                         phrase_match_bbox[OcrConstants.WORDS][i][OcrConstants.BBOX][3]))
                w_end = phrase_match_bbox[OcrConstants.WORDS][end_word_pos][OcrConstants.BBOX][2]
                w = phrase_match_bbox[OcrConstants.WORDS][end_word_pos][OcrConstants.BBOX][0] - \
                    phrase_match_bbox[OcrConstants.WORDS][start_word_pos][OcrConstants.BBOX][0] + w_end
                res_regions.append(
                    {"bbox": [l, t, w, h], "page": phrase_match_bbox["page"], 'token_type': token_type})
        return res_regions

    def _get_bbox_from_2anc_point(self, anchor_txt_bbox_1_lst,
                                  anchor_txt_bbox_2_lst, anchor_point_1, anchor_point_2,
                                  anchor_txt_1, anchor_txt_2, scaling_factors_key, max_word_space):
        res_regions = []
        for anchor_txt_bbox_1_obj in anchor_txt_bbox_1_lst:
            token_type_1 = anchor_txt_bbox_1_obj.get('token_type', 'phrase')
            anchor_txt_bbox_1 = anchor_txt_bbox_1_obj[ResProp.BBOX]
            for anchor_txt_bbox_2_obj in anchor_txt_bbox_2_lst:
                token_type_2 = anchor_txt_bbox_2_obj.get(
                    'token_type', 'phrase')
                anchor_txt_bbox_2 = anchor_txt_bbox_2_obj[ResProp.BBOX]
                actual_text_1 = [t['text'] for t in self.get_tokens_from_ocr(
                    3, within_bbox=anchor_txt_bbox_1, scaling_factors_key=scaling_factors_key, max_word_space=max_word_space)]
                actual_text_2 = [t['text'] for t in self.get_tokens_from_ocr(
                    3, within_bbox=anchor_txt_bbox_2, scaling_factors_key=scaling_factors_key, max_word_space=max_word_space)]
                anc_txt_bbox = [Response.res_at_bbox(anchor_txt_1, actual_text_1, token_type_1, anchor_txt_bbox_1, scaling_factors_key),
                                Response.res_at_bbox(anchor_txt_2, actual_text_2, token_type_2, anchor_txt_bbox_2, scaling_factors_key)]
                if anchor_txt_bbox_1_obj[ResProp.PAGE] == anchor_txt_bbox_2_obj[ResProp.PAGE] and anchor_txt_bbox_1[1] < anchor_txt_bbox_2[1]:
                    page_num = anchor_txt_bbox_1_obj[ResProp.PAGE]
                    labeled_anc_1_bbox = self._get_labeled_bbox(
                        anchor_txt_bbox_1, anchor_txt_1)
                    labeled_ach_2_bbox = self._get_labeled_bbox(
                        anchor_txt_bbox_2, anchor_txt_2)
                    x1, y1 = self._get_point_for(
                        anchor_txt_1, anchor_point_1, labeled_anc_1_bbox, page_num)
                    x2, y2 = self._get_point_for(
                        anchor_txt_2, anchor_point_2, labeled_ach_2_bbox, page_num)
                    anchor_txt_bbox_2_lst.remove(anchor_txt_bbox_2_obj)
                    within_text = [t['text'] for t in self.get_tokens_from_ocr(
                        3, within_bbox=CommonUtil.get_rect_point_for(x1, y1, x2, y2),
                        scaling_factors_key=scaling_factors_key, max_word_space=max_word_space)]
                    res_reg_bbox = [Response.res_reg_bbox(within_text, CommonUtil.get_rect_point_for(
                        x1, y1, x2, y2), page_num, scaling_factors_key)]
                    res_regions.append(Response.response_regions(
                        anc_txt_bbox, res_reg_bbox))
                    break
                elif anchor_txt_bbox_1_obj[ResProp.PAGE] != anchor_txt_bbox_2_obj[ResProp.PAGE]:
                    res_reg_bbox = self._adjust_bbox_to_combine_mul_page(
                        anchor_txt_bbox_1_obj, anchor_txt_bbox_2_obj, scaling_factors_key, max_word_space)
                    res_regions.append(
                        Response.response_regions(anc_txt_bbox, res_reg_bbox))
                    anchor_txt_bbox_2_lst.remove(anchor_txt_bbox_2_obj)
                    break
        return res_regions

    def _adjust_bbox_to_combine_mul_page(self, anchor_txt_bbox_1_obj, anchor_txt_bbox_2_obj, scaling_factors_key, max_word_space):
        within_text_1 = [t['text'] for t in self.get_tokens_from_ocr(
            3, within_bbox=anchor_txt_bbox_1_obj[ResProp.BBOX], scaling_factors_key=scaling_factors_key, max_word_space=max_word_space)]
        within_text_2 = [t['text'] for t in self.get_tokens_from_ocr(
            3, within_bbox=anchor_txt_bbox_2_obj[ResProp.BBOX],
            scaling_factors_key=scaling_factors_key, max_word_space=max_word_space)]
        res_reg_bbox = [Response.res_reg_bbox(within_text_1, anchor_txt_bbox_1_obj[ResProp.BBOX], anchor_txt_bbox_1_obj[ResProp.PAGE], scaling_factors_key),
                        Response.res_reg_bbox(within_text_2, anchor_txt_bbox_2_obj[ResProp.BBOX], anchor_txt_bbox_2_obj[ResProp.PAGE], scaling_factors_key)]
        res_reg_bbox.sort(key=lambda x: (x[ResProp.PAGE]))
        start_page = res_reg_bbox[0][ResProp.PAGE]
        l1, t1, w1, h1 = res_reg_bbox[0][ResProp.BBOX]
        pl1, pt1, pw1, ph1 = self._get_page_bbox_for(start_page)
        res_reg_bbox[0][ResProp.BBOX] = [pl1, t1, pw1, ph1-t1]

        end_page = res_reg_bbox[1][ResProp.PAGE]
        l2, t2, w2, h2 = res_reg_bbox[1][ResProp.BBOX]
        pl2, pt2, pw2, ph2 = self._get_page_bbox_for(end_page)
        res_reg_bbox[1][ResProp.BBOX] = [pl2, pt2, pw2,
                                         ph2 if l2 == w2 and t2 == h2 else t2+h2]
        for page in range(start_page+1, end_page):
            reg_bbox = self._get_page_bbox_for(page)
            within_text = [t['text'] for t in self.get_tokens_from_ocr(
                3, within_bbox=reg_bbox, scaling_factors_key=scaling_factors_key, max_word_space=max_word_space)]
            res_reg_bbox.append(Response.res_reg_bbox(
                within_text, reg_bbox, page, scaling_factors_key))

        return res_reg_bbox

    def _get_labeled_bbox(self, bbox_arr, anchor_txt=None):
        right_bbox = bbox_arr[2] + bbox_arr[0]
        bottom_bbox = bbox_arr[3] + bbox_arr[1]
        if anchor_txt and anchor_txt[0] == OcrConstants.DOC_ANC_TXT_EOD:
            right_bbox, bottom_bbox = bbox_arr[2], bbox_arr[3]
        return {BBoxLabel.LEFT: bbox_arr[0],
                BBoxLabel.TOP: bbox_arr[1],
                BBoxLabel.RIGHT: right_bbox,
                BBoxLabel.BOTTOM: bottom_bbox
                }

    def _get_point_for(self, a_txt, a_point_dict, labeled_anc_txt_bbox, page_num, is_empty_a_txt=False):
        x, y, = 0, 0
        if not a_point_dict:
            if a_txt == [OcrConstants.DOC_ANC_TXT_EOD]:
                return labeled_anc_txt_bbox[BBoxLabel.RIGHT], labeled_anc_txt_bbox[BBoxLabel.BOTTOM]
            return labeled_anc_txt_bbox[BBoxLabel.LEFT], labeled_anc_txt_bbox[BBoxLabel.TOP]
        for label in a_point_dict:
            a_point = a_point_dict[label]
            if a_point is not None:
                calc_point = self._get_point_calc_from_measurement_unit(
                    a_point, is_empty_a_txt, labeled_anc_txt_bbox, label, page_num)
                is_x = (label == BBoxLabel.LEFT or label == BBoxLabel.RIGHT)
                x, y = (calc_point, y) if is_x else (x, calc_point)
        return x, y

    def _get_point_calc_from_measurement_unit(self, a_point, is_empty_a_txt, labeled_anc_txt_bbox, label, page_num):
        start_point = copy.copy(labeled_anc_txt_bbox[label])
        if bool(re.match(RegUnitsRe.PIXEL_RE, str(a_point))):
            a_point = float(str(a_point).replace("px", ""))
            return start_point + a_point
        if type(a_point) == str and (bool(re.match(RegUnitsRe.PERCT_REL_RE, a_point)) or bool(re.match(RegUnitsRe.PERCT_ABS_RE, a_point))):
            skip_start_point_add = False
            point_to_derive_perct = start_point
            if not is_empty_a_txt or start_point == 0:
                look_for = 2 if (
                    label == BBoxLabel.LEFT or label == BBoxLabel.RIGHT) else 3
                is_positive_num = bool(
                    re.match(RegUnitsRe.STARTS_WITH_NUM_RE, a_point))
                if bool(re.match(RegUnitsRe.PERCT_REL_RE, a_point)) and is_positive_num:
                    point_to_derive_perct = self._get_page_bbox_for(page_num)[
                        look_for]
                    point_to_derive_perct -= start_point
                if bool(re.match(RegUnitsRe.PERCT_ABS_RE, a_point)):
                    point_to_derive_perct = self._get_page_bbox_for(page_num)[
                        look_for]
                    skip_start_point_add = True

            a_point = CommonUtil.convert_to_decimal(
                point_to_derive_perct, a_point)
            return abs(a_point) if skip_start_point_add else abs(start_point + a_point)
        if type(a_point) == str and bool(re.match(RegUnitsRe.TEXT_SIZE_RE, a_point)):
            a_point = float(str(a_point).replace("t", ""))
            page_bbox = self._get_page_bbox_for(page_num)
            calc_point = copy.copy(labeled_anc_txt_bbox[label])
            if label == BBoxLabel.LEFT or label == BBoxLabel.RIGHT:
                w_point = copy.copy(
                    labeled_anc_txt_bbox[BBoxLabel.RIGHT]) - copy.copy(labeled_anc_txt_bbox[BBoxLabel.LEFT])
                calc_point = calc_point + (w_point * a_point)
                calc_point = page_bbox[0] if calc_point < page_bbox[0] else calc_point
                calc_point = page_bbox[2] if calc_point > page_bbox[2] else calc_point
            elif label == BBoxLabel.TOP or label == BBoxLabel.BOTTOM:
                h_point = copy.copy(
                    labeled_anc_txt_bbox[BBoxLabel.BOTTOM]) - copy.copy(labeled_anc_txt_bbox[BBoxLabel.TOP])
                calc_point = calc_point+(h_point * a_point)
                calc_point = page_bbox[1] if calc_point < page_bbox[1] else calc_point
                calc_point = page_bbox[3] if calc_point > page_bbox[3] else calc_point
            return calc_point

    def _get_region_containing_text(self, match_text_arr, anchorTextMatch, lookup_pages, scaling_factors_key, max_word_space):
        '''
        Desc:
        ---------
        Returns the region list of 'match_text_arr' (Even if it is multiline)
        -----------------------------------
        '''
        mat_txt_reg_list, error = [], None
        try:
            if(len(match_text_arr) > 1):
                key_found_count = 0
                column_bboxes_list = []
                for line_txt in match_text_arr:
                    if(line_txt.strip() == ""):
                        raise Exception("key is empty")
                    match_txt_bbox = self._get_match_text_region(
                        line_txt, anchorTextMatch, lookup_pages, scaling_factors_key, max_word_space)
                    sorted(match_txt_bbox, key=lambda i: (
                        i['page'], i['bbox'][1]))
                    if(match_txt_bbox == []):
                        raise Exception("Key: " + line_txt + " not found")
                    column_bboxes_list.append(match_txt_bbox)
                for i, bbox_obj_1 in enumerate(column_bboxes_list[0]):
                    token_type = bbox_obj_1['token_type']
                    first_key = bbox_obj_1[ResProp.BBOX]
                    this_page_num = bbox_obj_1[ResProp.PAGE]
                    matched_count = 1
                    l, t, h, r = first_key[0], first_key[1], first_key[3], first_key[0]+first_key[2]
                    for c_count in range(1, len(column_bboxes_list)):
                        for r_count, bbox_obj_next in enumerate(column_bboxes_list[c_count]):
                            curr_key = bbox_obj_next[ResProp.BBOX]
                            if_next_line = False
                            # Current design proposes the multi-line anchor text should be present at the same page.
                            if this_page_num != bbox_obj_next[ResProp.PAGE]:
                                continue
                            prev_bbox = first_key if(
                                c_count == 1) else match_bbox
                            # next line text's 'left' should be either start in between the prev line width or end in between the prev line width
                            if((first_key[1] < curr_key[1]) and ((first_key[0] <= curr_key[0] <= first_key[0]+first_key[2] or first_key[0] <= curr_key[0]+curr_key[2] <= first_key[0]+first_key[2] or curr_key[0] <= first_key[0] <= curr_key[0]+curr_key[2]) or (prev_bbox[0] <= curr_key[0] <= prev_bbox[0]+prev_bbox[2] or prev_bbox[0] <= curr_key[0]+curr_key[2] <= prev_bbox[0]+prev_bbox[2] or curr_key[0] <= prev_bbox[0] <= curr_key[0]+curr_key[2]))):
                                if(c_count == 1):
                                    l_1 = first_key[0] if first_key[0] < curr_key[0] else curr_key[0]
                                    r_1 = first_key[0]+first_key[2] if first_key[0] + \
                                        first_key[2] > curr_key[0]+curr_key[2] else curr_key[0]+curr_key[2]
                                    t_1, w_1, h_1 = first_key[1] + \
                                        first_key[3], r_1-l_1, curr_key[1] - \
                                        first_key[1]-first_key[3]-2
                                else:
                                    if(matched_count == c_count):
                                        l_1 = match_bbox[0] if match_bbox[0] < curr_key[0] else curr_key[0]
                                        r_1 = match_bbox[0]+match_bbox[2] if match_bbox[0] + \
                                            match_bbox[2] > curr_key[0]+curr_key[2] else curr_key[0]+curr_key[2]
                                        t_1, w_1, h_1 = match_bbox[1] + \
                                            match_bbox[3], r_1-l_1, curr_key[1] - \
                                            match_bbox[1]-match_bbox[3]-2
                                    else:
                                        raise Exception(
                                            "All the key-list elements are not aligned in the same column")
                                # get all words between the two texts, if any
                                words_within_obj_list = []
                                for word in self.get_tokens_from_ocr(token_type_value=TokenType.WORD.value, scaling_factors_key=scaling_factors_key, max_word_space=max_word_space):
                                    if(word['text'].strip() != ''):
                                        if((word['bbox'][0] <= l_1 <= word['bbox'][0]+word['bbox'][2] or word['bbox'][0] <= l_1+w_1 <= word['bbox'][0]+word['bbox'][2] or l_1 <= word['bbox'][0] <= l_1+w_1) and t_1 <= word['bbox'][1] <= t_1+h_1):
                                            words_within_obj_list.append(word)
                                # if words found, searches if the word is in the same page and also if the the entire word is contained within the two texts region
                                if len(words_within_obj_list) > 0:
                                    for words_within_obj in words_within_obj_list:
                                        word_bbox = words_within_obj['bbox']
                                        if(t_1 <= word_bbox[1]+word_bbox[3] <= t_1+h_1):

                                            if(words_within_obj['page'] == this_page_num):
                                                if_next_line = True
                                                break
                                    if(if_next_line == True):
                                        continue
                                r = curr_key[0]+curr_key[2] if r < curr_key[0] + \
                                    curr_key[2] else r
                                l = curr_key[0] if l > curr_key[0] else l
                                if(c_count == 1):
                                    h = h + curr_key[3]+(curr_key[1] -
                                                         (first_key[1]+first_key[3]))
                                else:
                                    h = h + curr_key[3]+(curr_key[1] -
                                                         (match_bbox[1]+match_bbox[3]))
                                match_bbox = curr_key
                                matched_count += 1
                                break
                    if(matched_count == len(column_bboxes_list)):
                        key_found_count += 1
                        w = r-l
                        mat_txt_reg_list.append(
                            {"bbox": [l, t, w, h], "page": this_page_num, 'token_type': token_type})
                if(key_found_count == 0):
                    raise Exception(
                        "All the key-list elements are not aligned in the same column")
            else:
                mat_txt_reg_list = self._get_match_text_region(
                    match_text_arr[0], anchorTextMatch, lookup_pages, scaling_factors_key, max_word_space)
                if(mat_txt_reg_list == []):
                    raise Exception("Key: " + match_text_arr[0] + " not found")
        except Exception as e:
            mat_txt_reg_list, error = [], e.args[0]
        return mat_txt_reg_list, error

    def _check_and_get_anc_keyword_reg(self, anchor_text, lookup_pages):
        mat_txt_reg_list = []
        if len(anchor_text) != 1:
            return mat_txt_reg_list
        # Either {{BOD}} or {{EOD}} expected as string here
        a_txt = anchor_text[0]
        lookup_pages.sort()
        if a_txt == OcrConstants.DOC_ANC_TXT_BOD:
            [mat_txt_reg_list.append(
                page_obj) for page_obj in self._page_bbox_dict_list if page_obj["page"] == lookup_pages[0]]
        if a_txt == OcrConstants.DOC_ANC_TXT_EOD:
            for page_obj in self._page_bbox_dict_list:
                if page_obj["page"] == lookup_pages[-1]:
                    page_obj_temp = copy.deepcopy(page_obj)
                    _, _, x2, y2 = page_obj_temp["bbox"]
                    page_obj_temp["bbox"] = [x2, y2, x2, y2]
                    [mat_txt_reg_list.append(page_obj_temp)]
        return mat_txt_reg_list

    def _get_anchor_text_regions(self, anc_text, anchorTextMatch, lookup_pages, scaling_factors_key, max_word_space):
        mat_txt_reg_list, error = [], None
        try:
            # For Example, anc_text- ["foo", "poo"]
            if isinstance(anc_text[0], str):
                mat_txt_reg_list = self._check_and_get_anc_keyword_reg(
                    anc_text, lookup_pages)
                if len(mat_txt_reg_list) > 0:
                    return mat_txt_reg_list, error
                return self._get_region_containing_text(anc_text, anchorTextMatch, lookup_pages, scaling_factors_key, max_word_space)

            # For Example, anc_text- [["foo", "poo"]]
            elif(len(anc_text) == 1):
                for i in anc_text[0]:
                    reg_list, error = self._get_region_containing_text(
                        [i], anchorTextMatch, lookup_pages, scaling_factors_key, max_word_space)
                    if(reg_list != []):
                        mat_txt_reg_list += reg_list
                if mat_txt_reg_list == []:
                    raise Exception("No region found with the given keys")

            # For Example, anc_text- [["foo1", "poo1"],["foo2", "poo2"]]
            else:
                for i in list(itertools.product(*anc_text)):
                    reg_list, error = self._get_region_containing_text(
                        i, anchorTextMatch, lookup_pages, scaling_factors_key, max_word_space)
                    if(reg_list != []):
                        mat_txt_reg_list += reg_list
                if mat_txt_reg_list == []:
                    raise Exception("No region found with the given keys")
        except Exception as e:
            mat_txt_reg_list, error = [], e.args[0]
        if(len(mat_txt_reg_list) != 0):
            error = None
        return mat_txt_reg_list, error

    def _get_page_bbox_for(self, page):
        bbox = [page_obj[ResProp.BBOX]
                for page_obj in self._page_bbox_dict_list if page_obj[ResProp.PAGE] == page]
        return bbox[0]

    def _get_max_word_space(self, max_word_space, page, word_height):
        max_word_space = self._max_word_space if max_word_space is None else max_word_space
        if isinstance(max_word_space, int) or isinstance(max_word_space, float):
            return max_word_space
        else:
            if max_word_space.endswith('t'):
                return float(str(max_word_space.replace("t", ""))) * word_height
            elif max_word_space.endswith('px'):
                return float(max_word_space.replace("px", ""))
            elif max_word_space.endswith('%'):
                return float(str(max_word_space.replace("%", ""))) * self._get_page_bbox_for(page)[2] / 100
            else:
                return float(max_word_space)

    def _get_closest_fieldbox(self, fieldboxes, field_pos, block_bbox, key_bbox, token_alignment_threshold):
        closest = fieldboxes[0]
        if(field_pos == "right"):
            fieldboxes = [f for f in fieldboxes if f[0] >= block_bbox[0]]
            fieldboxes.sort(key=lambda x: (x[OcrConstants.BB_X]))
            for c in fieldboxes:
                c_dist = c[OcrConstants.BB_X] - \
                    (block_bbox[OcrConstants.BB_X] +
                     block_bbox[OcrConstants.BB_W])
                close_dist = closest[OcrConstants.BB_X] - \
                    (block_bbox[OcrConstants.BB_X] +
                     block_bbox[OcrConstants.BB_W])
                closest = self._closest_fieldbox_if_left_right(
                    key_bbox, c, close_dist, c_dist, closest, token_alignment_threshold)
                if closest == None:
                    closest = key_bbox
                    break
        elif(field_pos == "left"):
            fieldboxes = [f for f in fieldboxes if f[0] <= block_bbox[0]]
            fieldboxes.sort(key=lambda x: (x[OcrConstants.BB_X]), reverse=True)
            for c in fieldboxes:
                c_dist = block_bbox[OcrConstants.BB_X] - \
                    (c[OcrConstants.BB_X] + c[OcrConstants.BB_W])
                close_dist = block_bbox[OcrConstants.BB_X] - \
                    (closest[OcrConstants.BB_X]+closest[OcrConstants.BB_W])
                closest = self._closest_fieldbox_if_left_right(
                    key_bbox, c, close_dist, c_dist, closest, token_alignment_threshold)
                if closest == None:
                    closest = key_bbox
                    break
        elif(field_pos == "bottom"):
            fieldboxes = [f for f in fieldboxes if f[1] >= block_bbox[1]]
            fieldboxes.sort(key=lambda x: (x[OcrConstants.BB_Y]))
            for c in fieldboxes:
                c_dist = c[OcrConstants.BB_Y] - \
                    (block_bbox[OcrConstants.BB_Y] +
                     block_bbox[OcrConstants.BB_H])
                close_dist = closest[OcrConstants.BB_Y] - \
                    (block_bbox[OcrConstants.BB_Y] +
                     block_bbox[OcrConstants.BB_H])
                closest = self._closest_fieldbox_if_top_bottom(
                    key_bbox, c, close_dist, c_dist, closest, token_alignment_threshold)
                if closest == None:
                    closest = key_bbox
                    break
        elif(field_pos == "top"):
            fieldboxes = [f for f in fieldboxes if f[1] <= block_bbox[1]]
            fieldboxes.sort(key=lambda x: (x[OcrConstants.BB_Y]), reverse=True)
            for c in fieldboxes:
                c_dist = block_bbox[OcrConstants.BB_Y] - \
                    (c[OcrConstants.BB_Y] + c[OcrConstants.BB_H])
                close_dist = block_bbox[OcrConstants.BB_Y] - \
                    (closest[OcrConstants.BB_Y]+closest[OcrConstants.BB_H])
                closest = self._closest_fieldbox_if_top_bottom(
                    key_bbox, c, close_dist, c_dist, closest, token_alignment_threshold)
                if closest == None:
                    closest = key_bbox
                    break
        return closest

    def _closest_fieldbox_if_top_bottom(
            self, key_bbox, fieldbox, closest_fieldbox_dist,
            fieldbox_dist, closest_fieldbox, token_alignment_threshold):
        close_dist = closest_fieldbox_dist
        c = fieldbox
        c_dist = fieldbox_dist
        closest = closest_fieldbox
        if(close_dist < 0):
            if token_alignment_threshold > 0:
                if(key_bbox[OcrConstants.BB_X] >= c[OcrConstants.BB_X] and
                        key_bbox[OcrConstants.BB_X]+key_bbox[OcrConstants.BB_W] <= c[OcrConstants.BB_X]+c[OcrConstants.BB_W]):
                    closest = c
                elif c[OcrConstants.BB_X] + c[OcrConstants.BB_W] <= key_bbox[OcrConstants.BB_X]+key_bbox[OcrConstants.BB_W] and \
                        key_bbox[OcrConstants.BB_X] <= c[OcrConstants.BB_X]:
                    if c[OcrConstants.BB_W] < token_alignment_threshold*key_bbox[OcrConstants.BB_W]:
                        closest = None
                    else:
                        closest = c
                elif(key_bbox[OcrConstants.BB_X] <= c[OcrConstants.BB_X] <= key_bbox[OcrConstants.BB_X]+key_bbox[OcrConstants.BB_W]):
                    if(key_bbox[OcrConstants.BB_X] <= c[OcrConstants.BB_X] <= key_bbox[OcrConstants.BB_X]+(key_bbox[OcrConstants.BB_W]*(1-token_alignment_threshold))):
                        closest = c
                    else:
                        closest = None
                elif(key_bbox[OcrConstants.BB_X] <= c[OcrConstants.BB_X]+c[OcrConstants.BB_W] <= key_bbox[OcrConstants.BB_X]+key_bbox[OcrConstants.BB_W]):
                    if(key_bbox[OcrConstants.BB_X]+(key_bbox[OcrConstants.BB_W]*token_alignment_threshold) <= c[OcrConstants.BB_X]+c[OcrConstants.BB_W] <= key_bbox[OcrConstants.BB_X]+key_bbox[OcrConstants.BB_W]):
                        closest = c
                    else:
                        closest = None
            else:
                if(key_bbox[OcrConstants.BB_X] <= c[OcrConstants.BB_X] and
                        key_bbox[OcrConstants.BB_X]+key_bbox[OcrConstants.BB_W] >= c[OcrConstants.BB_X]+c[OcrConstants.BB_W]):
                    closest = c
        elif(close_dist > 0 and c_dist > 0 and c_dist <= close_dist):
            if token_alignment_threshold > 0:
                if(key_bbox[OcrConstants.BB_X] >= c[OcrConstants.BB_X] and
                        key_bbox[OcrConstants.BB_X]+key_bbox[OcrConstants.BB_W] <= c[OcrConstants.BB_X]+c[OcrConstants.BB_W]):
                    closest = c
                elif c[OcrConstants.BB_X] + c[OcrConstants.BB_W] <= key_bbox[OcrConstants.BB_X]+key_bbox[OcrConstants.BB_W] and \
                        key_bbox[OcrConstants.BB_X] <= c[OcrConstants.BB_X]:
                    if c[OcrConstants.BB_W] < token_alignment_threshold*key_bbox[OcrConstants.BB_W]:
                        closest = None
                    else:
                        closest = c
                elif(key_bbox[OcrConstants.BB_X] <= c[OcrConstants.BB_X] <= key_bbox[OcrConstants.BB_X]+key_bbox[OcrConstants.BB_W]):
                    if(key_bbox[OcrConstants.BB_X] <= c[OcrConstants.BB_X] <= key_bbox[OcrConstants.BB_X]+(key_bbox[OcrConstants.BB_W]*(1-token_alignment_threshold))):
                        closest = c
                    else:
                        closest = None
                elif(key_bbox[OcrConstants.BB_X] <= c[OcrConstants.BB_X]+c[OcrConstants.BB_W] <= key_bbox[OcrConstants.BB_X]+key_bbox[OcrConstants.BB_W]):
                    if(key_bbox[OcrConstants.BB_X]+(key_bbox[OcrConstants.BB_W]*token_alignment_threshold) <= c[OcrConstants.BB_X]+c[OcrConstants.BB_W] <= key_bbox[OcrConstants.BB_X]+key_bbox[OcrConstants.BB_W]):
                        closest = c
                    else:
                        closest = None
            else:
                if(key_bbox[OcrConstants.BB_X] <= c[OcrConstants.BB_X] and
                        key_bbox[OcrConstants.BB_X]+key_bbox[OcrConstants.BB_W] >= c[OcrConstants.BB_X]+c[OcrConstants.BB_W]):
                    closest = c
        return closest

    def _closest_fieldbox_if_left_right(
            self, key_bbox, fieldbox, closest_fieldbox_dist,
            fieldbox_dist, closest_fieldbox, token_alignment_threshold):
        close_dist = closest_fieldbox_dist
        c = fieldbox
        c_dist = fieldbox_dist
        closest = closest_fieldbox
        if(close_dist < 0):
            if token_alignment_threshold > 0:
                if(key_bbox[OcrConstants.BB_Y] >= c[OcrConstants.BB_Y] and
                        key_bbox[OcrConstants.BB_Y]+key_bbox[OcrConstants.BB_H] <= c[OcrConstants.BB_Y]+c[OcrConstants.BB_H]):
                    closest = c
                elif key_bbox[OcrConstants.BB_Y] <= c[OcrConstants.BB_Y] and \
                        key_bbox[OcrConstants.BB_Y]+key_bbox[OcrConstants.BB_H] >= c[OcrConstants.BB_Y]+c[OcrConstants.BB_H]:
                    if c[OcrConstants.BB_H] < token_alignment_threshold*key_bbox[OcrConstants.BB_H]:
                        closest = None
                    else:
                        closest = c
                elif(key_bbox[OcrConstants.BB_Y] <= c[OcrConstants.BB_Y]
                     <= key_bbox[OcrConstants.BB_Y]+key_bbox[OcrConstants.BB_H]):
                    if(key_bbox[OcrConstants.BB_Y] <= c[OcrConstants.BB_Y]
                            <= key_bbox[OcrConstants.BB_Y]+key_bbox[OcrConstants.BB_H]*(1-token_alignment_threshold)):
                        closest = c
                    else:
                        closest = None
                elif (key_bbox[OcrConstants.BB_Y] <= c[OcrConstants.BB_Y]+c[OcrConstants.BB_H]
                        <= (key_bbox[OcrConstants.BB_Y]+key_bbox[OcrConstants.BB_H])):
                    if (key_bbox[OcrConstants.BB_Y]+(key_bbox[OcrConstants.BB_H]*token_alignment_threshold)
                        <= c[OcrConstants.BB_Y]+c[OcrConstants.BB_H]
                            <= (key_bbox[OcrConstants.BB_Y]+key_bbox[OcrConstants.BB_H])):
                        closest = c
                    else:
                        closest = None
            else:
                if(key_bbox[OcrConstants.BB_Y] <= c[OcrConstants.BB_Y] and
                        key_bbox[OcrConstants.BB_Y]+key_bbox[OcrConstants.BB_H] >= c[OcrConstants.BB_Y]+c[OcrConstants.BB_H]):
                    closest = c
        elif(close_dist > 0 and c_dist > 0 and c_dist <= close_dist):
            if token_alignment_threshold > 0:
                if(key_bbox[OcrConstants.BB_Y] >= c[OcrConstants.BB_Y] and
                        key_bbox[OcrConstants.BB_Y]+key_bbox[OcrConstants.BB_H] <= c[OcrConstants.BB_Y]+c[OcrConstants.BB_H]):
                    closest = c
                elif key_bbox[OcrConstants.BB_Y] <= c[OcrConstants.BB_Y] and \
                        key_bbox[OcrConstants.BB_Y]+key_bbox[OcrConstants.BB_H] >= c[OcrConstants.BB_Y]+c[OcrConstants.BB_H]:
                    if c[OcrConstants.BB_H] < token_alignment_threshold*key_bbox[OcrConstants.BB_H]:
                        closest = None
                    else:
                        closest = c
                elif(key_bbox[OcrConstants.BB_Y] <= c[OcrConstants.BB_Y]
                     <= key_bbox[OcrConstants.BB_Y]+key_bbox[OcrConstants.BB_H]):
                    if(key_bbox[OcrConstants.BB_Y] <= c[OcrConstants.BB_Y]
                            <= key_bbox[OcrConstants.BB_Y]+key_bbox[OcrConstants.BB_H]*(1-token_alignment_threshold)):
                        closest = c
                    else:
                        closest = None
                elif (key_bbox[OcrConstants.BB_Y] <= c[OcrConstants.BB_Y]+c[OcrConstants.BB_H]
                        <= (key_bbox[OcrConstants.BB_Y]+key_bbox[OcrConstants.BB_H])):
                    if (key_bbox[OcrConstants.BB_Y]+(key_bbox[OcrConstants.BB_H]*token_alignment_threshold)
                        <= c[OcrConstants.BB_Y]+c[OcrConstants.BB_H]
                            <= (key_bbox[OcrConstants.BB_Y]+key_bbox[OcrConstants.BB_H])):
                        closest = c
                    else:
                        closest = None
            else:
                if(key_bbox[OcrConstants.BB_Y] <= c[OcrConstants.BB_Y] and
                        key_bbox[OcrConstants.BB_Y]+key_bbox[OcrConstants.BB_H] >= c[OcrConstants.BB_Y]+c[OcrConstants.BB_H]):
                    closest = c
        return closest

    def _update_text_bbox(self, block_bbox, word_bbox):
        b_pt, b_len = block_bbox
        w_pt, w_len = word_bbox
        if b_pt >= w_pt and b_pt+b_len >= w_pt+w_len:
            b_len = b_pt+b_len-w_pt
            b_pt = w_pt
        elif b_pt <= w_pt and b_pt+b_len <= w_pt+w_len:
            b_len = w_pt+w_len-b_pt
        elif b_pt > w_pt and b_pt+b_len < w_pt+w_len:
            b_pt = w_pt
            b_len = w_len
        elif b_pt == w_pt:
            b_len = b_len if b_len > w_len else w_len
        return b_pt, b_len

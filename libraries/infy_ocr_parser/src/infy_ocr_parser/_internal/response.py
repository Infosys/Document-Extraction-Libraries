# ===============================================================================================================#
# Copyright 2020 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

class Response:
    @staticmethod
    def response(regions=[], error=None, warnings=[]):
        res = {
            "regions": regions,
            "error": error
        }
        if len(warnings) > 0:
            res["warnings"] = warnings
        return res

    @staticmethod
    def update_get_tokens_bbox_response(token_dict_list):
        for token_dict in token_dict_list:
            if isinstance(token_dict, dict):
                token_dict["bbox"] = [round(i) for i in token_dict["bbox"]]
                if isinstance(token_dict['scalingFactor'], list):
                    token_dict["scalingFactor"] = {'ver': token_dict["scalingFactor"][0],
                                                   'hor': token_dict["scalingFactor"][1]}
                words_dict_list = token_dict.get("words", [])
                if len(words_dict_list) > 0:
                    token_dict["words"] = Response.update_get_tokens_bbox_response(
                        words_dict_list)
        return token_dict_list

    @staticmethod
    def update_get_bbox_for_response(res, key, val, ex_scaling_factors_key):
        scaling_factor_ver, scaling_factor_hor = [
            float(i) for i in ex_scaling_factors_key.split('_')]
        for response in res['regions']:
            for region in response['regionBBox']:
                region[key] = {'external': {'ver': scaling_factor_ver, 'hor': scaling_factor_hor},
                               'internal': val}
                region['bbox'][0], region['bbox'][2] = round(
                    region['bbox'][0] * scaling_factor_hor), round(region['bbox'][2] * scaling_factor_hor)
                region['bbox'][1], region['bbox'][3] = round(
                    region['bbox'][1] * scaling_factor_ver), round(region['bbox'][3] * scaling_factor_ver)
            for region in response['anchorTextBBox']:
                region['bbox'][0], region['bbox'][2] = round(
                    region['bbox'][0] * scaling_factor_hor), round(region['bbox'][2] * scaling_factor_hor)
                region['bbox'][1], region['bbox'][3] = round(
                    region['bbox'][1] * scaling_factor_ver), round(region['bbox'][3] * scaling_factor_ver)
        return res

    @staticmethod
    def response_regions(txt_bbox=[], bbox=[]):
        return {
            "anchorTextBBox": txt_bbox,
            "regionBBox": bbox
        }

    @staticmethod
    def res_at_bbox(anchor_text=[], text=[], token_type='phrase', bbox=[], scaling_factor=0):
        return {
            "anchorText": anchor_text,
            "text": text,
            "tokenType": token_type,
            "bbox": bbox,
            "scalingFactor": [float(i) for i in scaling_factor.split('_')]
        }

    @staticmethod
    def res_reg_bbox(text, bbox, text_conf,  page, scaling_factor):
        return{
            "text": text,
            "bbox": bbox,
            "page": page,
            "confidencePct": text_conf,
            "scalingFactor": [float(i) for i in scaling_factor.split('_')]
        }

    @staticmethod
    def token_response(output=[], error=None):
        return {
            "tokenData": Response.update_nearby_token_dict(output),
            "error": error
        }

    @staticmethod
    def update_nearby_token_dict(res):
        for response in res:
            response['anchorTextData']['bbox'] = [
                round(i) for i in response['anchorTextData']['bbox']]
            region = response['regions']
            for direction in ('top', 'right', 'left', 'bottom'):
                if region[direction].get('regionBbox'):
                    region[direction]['regionBbox'] = [
                        round(i) for i in region[direction]['regionBbox']]
                    Response.update_get_tokens_bbox_response(
                        region[direction]['tokens'])
        return res

    @staticmethod
    def res_nearby_tokens(anchor_text, actual_text, key_bbox, result):
        return{
            'anchorTextData': {
                'anchorText': anchor_text,
                'text': actual_text,
                'bbox': key_bbox
            },
            'regions': result
        }

    @staticmethod
    def data_dict(id_str, page, text, bbox, scaling_factor=None, conf=None, word_structure=None):
        data_dict = {"id": id_str, "page": page, "text": text, "bbox": bbox}
        if scaling_factor is not None:
            data_dict["scalingFactor"] = [float(i)
                                          for i in scaling_factor.split('_')]
        if conf is not None:
            data_dict["conf"] = str(conf)
        if word_structure is not None:
            data_dict["words"] = word_structure
        return data_dict

    @staticmethod
    def save_res(is_saved=False, error=None):
        return {"isFileSaved": is_saved, "error": error}

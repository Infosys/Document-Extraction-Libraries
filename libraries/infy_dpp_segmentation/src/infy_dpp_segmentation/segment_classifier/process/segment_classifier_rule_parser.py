# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import copy
from infy_dpp_segmentation.segment_classifier.common.common_util import CommonUtil
from infy_dpp_segmentation.segment_classifier.rules.rule_segment_base_class import RuleSegmentBaseClass


class SegmentClassifierRuleParser:
    def __init__(self, file_sys_handler, logger, app_config) -> None:
        self.__logger = logger
        self.__app_config = app_config
        self.__file_sys_handler = file_sys_handler

    def classify_segments(self, segment_data_list, header, footer, ocr_file_path_list):
        is_content_bbox_empty = False
        for segment_data in segment_data_list:
            if not segment_data.get("content_bbox"):
                is_content_bbox_empty = True

        header_name = header.get('name') if header else None
        footer_name = footer.get('name') if footer else None

        if header_name == "manually_detect" and footer_name == "manually_detect":
            rule_name = 'rule_segment_manually_detect'
        elif header_name == "auto_detect" and footer_name == "auto_detect":
            rule_name = 'rule_segment_auto_detect'
        elif header_name != footer_name:
            raise Exception(
                'Header and Footer technique should be same for the document.')

        rule_class = CommonUtil.get_rule_class_instance(
            rule_name, rc_entity_name='')
        rule_instance: RuleSegmentBaseClass = rule_class(
            self.__file_sys_handler, self.__logger, self.__app_config)

        if header and footer and not is_content_bbox_empty:
            rule_result = rule_instance.template_method(
                copy.deepcopy(segment_data_list), header, footer, ocr_file_path_list)
        elif header is None and footer and not is_content_bbox_empty:
            rule_result = rule_instance.template_method(
                copy.deepcopy(segment_data_list), header, footer, ocr_file_path_list)
        elif header and footer is None and not is_content_bbox_empty:
            rule_result = rule_instance.template_method(
                copy.deepcopy(segment_data_list), header, footer, ocr_file_path_list)
        elif header is None and footer is None and not is_content_bbox_empty:
            rule_result = rule_instance.template_method(
                copy.deepcopy(segment_data_list), header, footer, ocr_file_path_list)
        else:
            raise Exception('content bbox is empty.')
        return rule_result

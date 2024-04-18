# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                   #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import copy
from infy_dpp_segmentation.segment_classifier.common.common_util import CommonUtil
from infy_dpp_segmentation.segment_classifier.rules.rule_segment_base_class import RuleSegmentBaseClass

class SegmentClassifierRuleParser:
    def __init__(self) -> None:
        pass
    
    def classify_segments(self, segment_data_list, header, footer):
        is_content_bbox_empty = False
        for segment_data in segment_data_list:
            if not segment_data.get("content_bbox"):
                is_content_bbox_empty = True
                
        rule_name = 'rule_segment_header_footer'
        rule_class = CommonUtil.get_rule_class_instance(
                rule_name, rc_entity_name='') 
        rule_instance: RuleSegmentBaseClass = rule_class()
        
        if header and footer and not is_content_bbox_empty:
            rule_result = rule_instance.template_method(
                copy.deepcopy(segment_data_list),header,footer)
        elif header is None and footer and not is_content_bbox_empty:
            rule_result = rule_instance.template_method(
                copy.deepcopy(segment_data_list),header,footer)
        elif header and footer is None and not is_content_bbox_empty:
            rule_result = rule_instance.template_method(
                copy.deepcopy(segment_data_list),header,footer)
        elif header is None and footer is None and not is_content_bbox_empty:
            rule_result = rule_instance.template_method(
                copy.deepcopy(segment_data_list),header,footer)
        else:
            raise Exception('content bbox is empty.')
        return rule_result
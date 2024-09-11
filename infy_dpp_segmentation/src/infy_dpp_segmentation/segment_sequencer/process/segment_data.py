# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                   #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import copy
from infy_dpp_segmentation.segment_sequencer.common.common_util import CommonUtil
from infy_dpp_segmentation.segment_sequencer.rules.rule_segment_base_class import RuleSegmentBaseClass


class SegementData:
    def __init__(self) -> None:
        pass

    def update_sequence(self, segment_data_list, layout, pattern, pages, page):
        is_content_bbox_empty = False
        for segment_data in segment_data_list:
            if not segment_data.get("content_bbox"):
                is_content_bbox_empty = True
        if (layout == 'single-column' and pattern == 'sequence-order') or is_content_bbox_empty:
            rule_name = 'rule_segment_default'
            rule_class = CommonUtil.get_rule_class_instance(
                rule_name, rc_entity_name='')
            rule_instance: RuleSegmentBaseClass = rule_class()
            rule_result = rule_instance.template_method(
                copy.deepcopy(segment_data_list), pages, page)
        # if  layout =='single' and pattern == 'default'
        elif layout == 'multi-column' and pattern == 'left-right':
            rule_name = 'rule_segment_left_to_right'
            rule_class = CommonUtil.get_rule_class_instance(
                rule_name, rc_entity_name='')
            rule_instance: RuleSegmentBaseClass = rule_class()
            rule_result = rule_instance.template_method(
                copy.deepcopy(segment_data_list), pages, page)
        elif layout == 'multi-column' and pattern == 'zig-zag':
            rule_name = 'rule_segment_zig_zag'
            rule_class = CommonUtil.get_rule_class_instance(
                rule_name, rc_entity_name='')
            rule_instance: RuleSegmentBaseClass = rule_class()
            rule_result = rule_instance.template_method(
                copy.deepcopy(segment_data_list), pages, page)
        else:
            raise Exception('Invalid layout and pattern.')
        return rule_result

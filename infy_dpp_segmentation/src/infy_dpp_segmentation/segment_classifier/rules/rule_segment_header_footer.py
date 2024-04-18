# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                   #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

from infy_dpp_segmentation.segment_classifier.rules.rule_segment_base_class import RuleSegmentBaseClass

class RuleSegmentHeaderFooter(RuleSegmentBaseClass):
    def classify_segment(self, segment_data_list:list, header:object, footer:object) -> list:
        if header is None and footer is None:
            return segment_data_list
        
        new_segment_data_list = []
        for segment_data in segment_data_list:
            bbox = segment_data.get('content_bbox')
            if bbox:
                if header is not None and header['min_height'] <= bbox[3] <= header['max_height']:
                    segment_data['content_type'] = "header"
                if footer is not None and footer['min_height'] <= bbox[1] <= footer['max_height']:
                    segment_data['content_type'] = "footer"
                new_segment_data_list.append(segment_data)
        return new_segment_data_list


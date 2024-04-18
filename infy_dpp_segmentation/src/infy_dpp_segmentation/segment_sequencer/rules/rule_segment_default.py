# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                   #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

from infy_dpp_segmentation.segment_sequencer.rules.rule_segment_base_class import RuleSegmentBaseClass


class RuleSegmentDefault(RuleSegmentBaseClass):
    def __init__(self) -> None:
        super().__init__()

    def generate_sequence_no(self, segment_data_list: list) -> list:
        updated_segment_data_list = []
        counter = 1
        for segment_data in segment_data_list:
            # TODO: segment logic should be added.
            # if len(segment_data.get('content_bbox')) > 0:
            #     pass
            # else:
            single_segment_data_dict = segment_data
            single_segment_data_dict.update({"sequence": counter})
            updated_segment_data_list.append(single_segment_data_dict)
            counter = counter+1
        return updated_segment_data_list

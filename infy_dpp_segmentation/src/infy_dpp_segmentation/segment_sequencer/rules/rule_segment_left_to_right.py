# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                   #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

from infy_dpp_segmentation.segment_sequencer.rules.rule_segment_base_class import RuleSegmentBaseClass
import scipy.spatial.distance as distance
import copy


class RuleSegmentLeftToRight(RuleSegmentBaseClass):
    def __init__(self) -> None:
        super().__init__()

    def generate_sequence_no(self, segment_data_list: list) -> list:
        """_summary_

        Args:
            content_bbox : here it takes x1,y1,x2,y2 format

        Returns:
            list: populate sequence no and update the segment_data_list
        """
        updated_segment_data_list = []
        points = list(map(lambda x: [x['content'], [x['content_bbox'][0], x['content_bbox'][1]],
                                     [x['content_bbox'][2], x['content_bbox'][3]], x['page']], segment_data_list))
        # sum of x1 and y1 to get nearest point
        points_sum = list(
            map(lambda x: [x[0], x[1], sum(x[1]), x[2][1]], points))
        # x_y_cordinate = list(map(lambda x: x[1],points_sum))
        sorted_list = [i for i in sorted(
            enumerate(points), key=lambda x: (x[1][3], x[1][1][1], x[1][1][0]))]
        sequence_counter = 1
        for idx, data in enumerate(sorted_list):
            # print(idx)
            # if new page no comes , sequence no resets.
            if idx != 0 and data[1][3] != sorted_list[idx-1][1][3]:
                sequence_counter = 1
            for i in segment_data_list:
                if data[1][3] == i['page'] and \
                        data[1][0] == i['content'] and \
                        data[1][1] == [i['content_bbox'][0], i['content_bbox'][1]]:
                    # print(data)
                    segment_data_dict = copy.deepcopy(i)
                    segment_data_dict['sequence'] = sequence_counter
                    updated_segment_data_list.append(segment_data_dict)
            sequence_counter += 1
        updated_segment_data_list.sort(key=lambda x: (
            x['page'], x['sequence']), reverse=False)
        return updated_segment_data_list

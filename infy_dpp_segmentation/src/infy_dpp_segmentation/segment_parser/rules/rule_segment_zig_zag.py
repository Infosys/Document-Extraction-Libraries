# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

from infy_dpp_segmentation.segment_parser.rules.rule_segment_base_class import RuleSegmentBaseClass
import scipy.spatial.distance as distance
import copy


class RuleSegmentZigZag(RuleSegmentBaseClass):
    def __init__(self) -> None:
        super().__init__()

    def generate_sequence_no(self, segment_data_list: list) -> list:
        updated_segment_data_list = []
        points = list(map(lambda x: [x['content'], [x['content_bbox'][0], x['content_bbox'][1]],
                                     [x['content_bbox'][2], x['content_bbox'][3]], x['page']], segment_data_list))
        # sum of x1 and y1 to get nearest point
        points_sum = list(map(lambda x: [x[0], x[1], sum(x[1]), x[3]], points))
        # x_y_cordinate = list(map(lambda x: x[1],points_sum))
        # reading with sum , left , top
        _ = [i for i in sorted(enumerate(points_sum), key=lambda x: (
            x[1][3], x[1][1][0], x[1][2], x[1][1][1]))]
        sorted_list = [i for i in sorted(
            enumerate(points), key=lambda x: (x[1][3], x[1][1][0], x[1][1][1]))]

        new_column = []
        group = 1
        for idx, data in enumerate(sorted_list):
            if idx != 0:
                if data[1][3] != sorted_list[idx-1][1][3]:
                    group = group+1
                    new_column.append((group, data))
                elif data[1][3] == sorted_list[idx-1][1][3] and data[1][1][0] >= sorted_list[idx-1][1][1][0]*1.05:
                    group = group+1
                    new_column.append((group, data))
                elif data[1][3] == sorted_list[idx-1][1][3] and data[1][1][0] <= sorted_list[idx-1][1][1][0]*1.05:
                    new_column.append((group, data))
            else:
                new_column.append((group, data))

        col_group_sorted_list = [i for i in sorted(
            new_column, key=lambda x: (x[0], x[1][1][1][1]))]
        sequence_counter = 1
        for idx, data in enumerate(col_group_sorted_list):
            # print(idx)
            if idx != 0 and data[1][1][3] != col_group_sorted_list[idx-1][1][1][3]:
                sequence_counter = 1
            for i in segment_data_list:
                if data[1][1][3] == i['page'] and \
                        data[1][1][0] == i['content'] and \
                        data[1][1][1] == [i['content_bbox'][0], i['content_bbox'][1]]:
                    # print(data)
                    segment_data_dict = copy.deepcopy(i)
                    segment_data_dict['sequence'] = sequence_counter
                    updated_segment_data_list.append(segment_data_dict)
            sequence_counter += 1
        updated_segment_data_list.sort(key=lambda x: (
            x['page'], x['sequence']), reverse=False)
        return updated_segment_data_list

# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                   #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import copy
import scipy.spatial.distance as distance
from collections import defaultdict
from infy_dpp_segmentation.segment_sequencer.rules.rule_segment_base_class import RuleSegmentBaseClass
from infy_dpp_segmentation.common.file_util import FileUtil


class RuleSegmentZigZag(RuleSegmentBaseClass):
    def __init__(self) -> None:
        super().__init__()

    def generate_sequence_no_dynamically(self, segment_data_list: list, pages, page) -> list:
        """This method generated sequence not relying on page_column_detectors 
        column data and has logic to dynamically group segments into columns based on threshold(unused)"""

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

    def generate_sequence_no(self, segment_data_list: list, pages, page) -> list:
        """This method generates sequence based on the column boundaries 
        detected by the page_column_detector(current)"""

        # Filter segments to include only those from the target page
        segment_data_list = [
            segment for segment in segment_data_list if segment['page'] == page]

        # Assign columns to segments
        for segment in segment_data_list:
            x1, y1, _, _ = segment['content_bbox']
            column_boundaries = [
                (col['content_bbox'][0], col['content_bbox'][2]) for col in pages[page]]
            column_index = next((index for index, (start_x, end_x) in enumerate(
                column_boundaries) if start_x <= x1 < end_x), None)
            segment['column'] = (
                column_index + 1) if column_index is not None else -1

        # Group and sort segments by page, column, and position
        segments_by_page_and_column = {}
        for segment in segment_data_list:
            key = (segment['page'], segment['column'])
            if key not in segments_by_page_and_column:
                segments_by_page_and_column[key] = []
            segments_by_page_and_column[key].append(segment)

        # Adjusted sorting: First by page, then by column, within each column by x, and then by y
        x_threshold = 50
        for key, segments in segments_by_page_and_column.items():
            # First, sort by x to group by sub-columns
            segments.sort(key=lambda x: x['content_bbox'][0])
            # Then, within each sub-column, sort by y
            sub_columns = []
            current_sub_column = []
            last_x = None
            for segment in segments:
                if last_x is not None and abs(segment['content_bbox'][0] - last_x) > x_threshold:
                    sub_columns.append(current_sub_column)
                    current_sub_column = []
                current_sub_column.append(segment)
                last_x = segment['content_bbox'][0]
            if current_sub_column:  # Add the last sub-column if it exists
                sub_columns.append(current_sub_column)
            # Flatten the sub-columns after sorting each by y
            sorted_segments = [seg for sub_col in sub_columns for seg in sorted(
                sub_col, key=lambda x: x['content_bbox'][1])]
            segments_by_page_and_column[key] = sorted_segments

        # Flatten the sorted segments and assign sequence numbers
        updated_segment_data_list = []
        sequence_counter = 1
        current_page = None
        for key in sorted(segments_by_page_and_column.keys(), key=lambda x: (x[0], x[1])):
            for segment in segments_by_page_and_column[key]:
                if segment['page'] != current_page:
                    sequence_counter = 1
                    current_page = segment['page']
                else:
                    sequence_counter += 1
                segment['sequence'] = sequence_counter
                segment["segment_id"] = f'S-{FileUtil.get_uuid()[:5]}'
                # Optional: comment out the next line if column key is needed
                del segment['column']
                updated_segment_data_list.append(segment)

        return updated_segment_data_list

# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                   #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

class SegmentDataMerger:
    def __init__(self, segment_data_list_of_list: list):
        self.segment_data_list_of_list = segment_data_list_of_list
        self.segment_data_result_list = []

    def overlaps(self, bbox1: list, bbox2: list):
        return not (bbox1[2] <= bbox2[0] or bbox1[0] >= bbox2[2] or bbox1[3] <= bbox2[1] or bbox1[1] >= bbox2[3])

    def segment_data_insert(self, data):
        for existing_data in self.segment_data_result_list:
            if ((existing_data['page'] == data['page']) and (self.overlaps(data['content_bbox'], existing_data['content_bbox']))):
                return
        # self.segment_data_result_list.append(data)
        # self.max_data_update(data)
        if (data['content_bbox'][3] - data['content_bbox'][1] < 1500):
            self.segment_data_result_list.append(data)

    def segment_data_merge(self) -> list:
        if len(self.segment_data_list_of_list) == 1:
            return self.segment_data_list_of_list[0]

        list_one = self.segment_data_list_of_list[0]
        list_two = self.segment_data_list_of_list[1]

        if not list_one and not list_two:
            return []
        elif not list_one:
            return list_two
        elif not list_two:
            return list_one

        # Merge the two lists and sort by 'page' and 'content_bbox' y1 coordinate
            # vertical positioning (top to bottom)
        # merged_list = sorted(list_one + list_two, key=lambda data: (data['page'], data['content_bbox'][1]))
        # Merge the two lists and sort by 'page' and 'content_bbox' x1 coordinate
            # horizontal positioning (left to right)
        merged_list = sorted(
            list_one + list_two, key=lambda data: (data['page'], data['content_bbox'][0]))

        # Filter out duplicate data and data with empty 'content'
        for data in merged_list:
            if data['content'] != "" and (not self.segment_data_result_list or data != self.segment_data_result_list[-1]):
                self.segment_data_insert(data)

        return self.segment_data_result_list

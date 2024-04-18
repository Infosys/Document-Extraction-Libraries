# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                   #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

class SegmentDataConsolidator:
    def __init__(self, segment_data_list_of_list: list):
        self.segment_data_list_of_list = segment_data_list_of_list
        self.segment_data_result_list = []

    def overlaps(self, bbox1: list, bbox2: list):
        return not (bbox1[2] <= bbox2[0] or bbox1[0] >= bbox2[2] or bbox1[3] <= bbox2[1] or bbox1[1] >= bbox2[3])

    def segment_data_insert(self, data):
        for existing_data in self.segment_data_result_list:
            if ((existing_data['page'] == data['page']) and (self.overlaps(data['content_bbox'], existing_data['content_bbox']))):
                return

        if (data['content_type'] == 'image_text'):
            self.segment_data_result_list.append(data)
        elif (data['content_bbox'][3] - data['content_bbox'][1] < 1500):
            self.segment_data_result_list.append(data)

    def segment_data_merge(self) -> list:
        if not self.segment_data_list_of_list:
            return []
        if len(self.segment_data_list_of_list) == 1:
            return self.segment_data_list_of_list[0]

        merged_list = sorted(
            [item for sublist in self.segment_data_list_of_list for item in sublist],
            key=lambda data: (data['page'], 0 if data['content_type'] ==
                              'image_text' else 1 if data['content_type'] == 'table' else 2,
                              data['content_bbox'][0])
        )

        # Filter out duplicate data and data with empty 'content'
        for data in merged_list:
            # if data['content'] != "" and (not self.segment_data_result_list or data != self.segment_data_result_list[-1]):
            if data['content'] != "" and any(char.isalnum() for char in data['content']) and (not self.segment_data_result_list or data != self.segment_data_result_list[-1]):
                self.segment_data_insert(data)

        return self.segment_data_result_list

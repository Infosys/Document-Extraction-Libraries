# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                   #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

class SegmentDataMerger:
    def __init__(self, segment_data_list_of_list: list, prefer_larger_segments=False):
        self.segment_data_list_of_list = segment_data_list_of_list
        self.segment_data_result_list = []
        self.prefer_larger_segments = prefer_larger_segments

    def segment_data_merge(self, merge_requirements) -> list:
        if len(self.segment_data_list_of_list) == 1:
            if merge_requirements.get('enabled'):
                vertical_max_gap = merge_requirements.get(
                    'vertical_adjacent_segments_max_gap_in_pixel')
                horizontal_max_gap = merge_requirements.get(
                    'horizontal_adjacent_segments_max_gap_in_pixel')
                group_adjacent_boxes = self.__group_adjacent_boxes(
                    self.segment_data_list_of_list[0], vertical_max_gap, horizontal_max_gap)
                return group_adjacent_boxes

            return self.segment_data_list_of_list[0]

    # def __group_adjacent_boxes(self, merged_list, vertical_max_gap, horizontal_max_gap):
    #     # Sort the list by 'page', 'y1', and 'x1'
    #     sorted_list = sorted(merged_list, key=lambda data: (
    #         data['page'], data['content_bbox'][1], data['content_bbox'][0]))

    #     grouped_boxes = []
    #     for data in sorted_list:
    #         # If the content type is 'table' or 'image_text', start a new group with this data and
    #         # continue to the next iteration
    #         if data['content_type'] in ['table', 'image_text']:
    #             grouped_boxes.append([data])
    #             continue

    #         found_group = False
    #         for group in grouped_boxes:
    #             # Check if the current box is adjacent to any box in the group and on the same page
    #             if any(box['page'] == data['page'] and box['content_type'] == data['content_type']
    #                    and self.__is_adjacent(box['content_bbox'], data['content_bbox'],
    #                                           vertical_max_gap, horizontal_max_gap) for box in group):
    #                 # If such a group is found, add the box to that group
    #                 group.append(data)
    #                 found_group = True
    #                 break
    #         if not found_group:
    #             # If no such group is found, start a new group with the current box
    #             grouped_boxes.append([data])

    #     # return grouped_boxes
    #     return self.__merge_boxes(grouped_boxes)

    def __group_adjacent_boxes(self, merged_list, vertical_max_gap, horizontal_max_gap, length_threshold=1.7):
        # Sort the list by 'page', 'y1', and 'x1'
        sorted_list = sorted(merged_list, key=lambda data: (
            data['page'], data['content_bbox'][1], data['content_bbox'][0]))

        grouped_boxes = []
        flagged_segments = []
        for data in sorted_list:
            # If the content type is 'table' or 'image_text', start a new group with this data and
            # continue to the next iteration
            if data['content_type'] in ['table', 'image_text']:
                grouped_boxes.append([data])
                continue

            # Calculate the length of the segment
            length = self.__length(data['content_bbox'])

            # If the segment is significantly longer than the previous ones, flag it and continue
            if grouped_boxes:
                all_segments = [
                    seg for group in grouped_boxes for seg in group]
                last_segments = all_segments[-75:]
                avg_prev_length = sum(self.__length(
                    seg['content_bbox']) for seg in last_segments) / len(last_segments) if last_segments else 0
                if length > length_threshold * avg_prev_length:
                    grouped_boxes.append([data])
                    flagged_segments.append(data)
                    continue

            found_group = False
            for group in grouped_boxes:
                # Check if the current box is adjacent to any box in the group and on the same page
                if any(box['page'] == data['page']
                       and (box['content_type'] == data['content_type'] or length <= length_threshold * self.__length(box['content_bbox']))
                       and self.__is_adjacent(box['content_bbox'], data['content_bbox'], vertical_max_gap, horizontal_max_gap) for box in group
                       if box not in flagged_segments):
                    # If such a group is found, add the box to that group
                    group.append(data)
                    found_group = True
                    break

            if not found_group:
                # If no such group is found, start a new group with the current box
                grouped_boxes.append([data])

        # return grouped_boxes
        return self.__merge_boxes(grouped_boxes)

    def __length(self, bbox):
        # Assuming bbox is a tuple or list of the form (x1, y1, x2, y2)
        # Calculate the length as the difference in x-coordinates
        return bbox[2] - bbox[0]

    def __is_adjacent(self, bbox1, bbox2, threshold_tb, threshold_rl):
        # Check if the boxes are vertically adjacent
        vertical = abs(bbox1[3] - bbox2[1]) <= threshold_tb and (
            max(bbox1[0], bbox2[0]) <= min(bbox1[2], bbox2[2]))
        # Check if the boxes are horizontally adjacent
        horizontal = abs(bbox1[2] - bbox2[0]) <= threshold_rl and (
            max(bbox1[1], bbox2[1]) <= min(bbox1[3], bbox2[3]))
        # If either condition is met, the boxes are adjacent
        return vertical or horizontal

    def __merge_boxes(self, grouped_boxes):
        # Merge all bounding boxes in each group into a single larger bounding box
        merged_boxes = []
        for group in grouped_boxes:
            # Sort each group by 'y1' and 'x1'
            group.sort(key=lambda data: (
                data['content_bbox'][1], data['content_bbox'][0]))

            min_x1 = min(data['content_bbox'][0] for data in group)
            min_y1 = min(data['content_bbox'][1] for data in group)
            max_x2 = max(data['content_bbox'][2] for data in group)
            max_y2 = max(data['content_bbox'][3] for data in group)
            content = '\n'.join(data['content'] for data in group)

            # Create a copy of the first element to retain all other parameters
            merged_box = group[0].copy()
            # Update 'content_bbox' and 'content'
            merged_box.update(
                {'content_bbox': [min_x1, min_y1, max_x2, max_y2], 'content': content})

            merged_boxes.append(merged_box)

        return merged_boxes

    # def __merge_boxes(self, grouped_boxes):
    #         # Merge all bounding boxes in each group into a single larger bounding box
    #         merged_boxes = []
    #         for group in grouped_boxes:
    #             # Remove any bbox that is inside another bbox within the same group
    #             filtered_group = []
    #             for i, data_i in enumerate(group):
    #                 inside_another = False
    #                 for j, data_j in enumerate(group):
    #                     if i != j and self.__is_inside(data_i['content_bbox'], data_j['content_bbox']):
    #                         inside_another = True
    #                         break
    #                 if not inside_another:
    #                     filtered_group.append(data_i)

    #             # Proceed with merging the filtered group as before
    #             if filtered_group:
    #                 filtered_group.sort(key=lambda data: (data['content_bbox'][1], data['content_bbox'][0]))
    #                 min_x1 = min(data['content_bbox'][0] for data in filtered_group)
    #                 min_y1 = min(data['content_bbox'][1] for data in filtered_group)
    #                 max_x2 = max(data['content_bbox'][2] for data in filtered_group)
    #                 max_y2 = max(data['content_bbox'][3] for data in filtered_group)
    #                 content = '\n'.join(data['content'] for data in filtered_group)
    #                 merged_box = filtered_group[0].copy()
    #                 merged_box.update({'content_bbox': [min_x1, min_y1, max_x2, max_y2], 'content': content})
    #                 merged_boxes.append(merged_box)

    #         return merged_boxes

    # def __is_inside(self, bbox1, bbox2):
    #     # Check if bbox1 is completely inside bbox2
    #     return (bbox2[0] <= bbox1[0] <= bbox2[2] and bbox2[0] <= bbox1[2] <= bbox2[2] and
    #             bbox2[1] <= bbox1[1] <= bbox2[3] and bbox2[1] <= bbox1[3] <= bbox2[3])

    def __segment_data_insert(self, data):
        # Check the height of the new data's bounding box
        if data['content_bbox'][3] - data['content_bbox'][1] >= 1500:
            return

        overlapping_indices = []
        for i, existing_data in enumerate(self.segment_data_result_list):
            if existing_data['page'] == data['page'] and self.__overlaps(data['content_bbox'], existing_data['content_bbox']):
                overlapping_indices.append(i)

        if overlapping_indices and self.prefer_larger_segments:
            # Calculate the area of the new data's bounding box
            new_data_area = (data['content_bbox'][2] - data['content_bbox']
                             [0]) * (data['content_bbox'][3] - data['content_bbox'][1])

            # Check if the new data's bounding box is larger than all of the overlapping ones
            if all(new_data_area > (self.segment_data_result_list[i]['content_bbox'][2] - self.segment_data_result_list[i]['content_bbox'][0]) * (self.segment_data_result_list[i]['content_bbox'][3] - self.segment_data_result_list[i]['content_bbox'][1]) for i in overlapping_indices):
                for i in reversed(overlapping_indices):
                    del self.segment_data_result_list[i]
                self.segment_data_result_list.append(data)
        elif not overlapping_indices:
            # If there are no overlapping items, append the new data
            self.segment_data_result_list.append(data)

    def __overlaps(self, bbox1: list, bbox2: list):
        return not (bbox1[2] <= bbox2[0] or bbox1[0] >= bbox2[2] or bbox1[3] <= bbox2[1] or bbox1[1] >= bbox2[3])

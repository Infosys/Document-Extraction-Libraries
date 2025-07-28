# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import json
import infy_fs_utils
import infy_dpp_sdk
from infy_dpp_segmentation.segment_classifier.rules.rule_segment_base_class import RuleSegmentBaseClass


class RuleSegmentAutoDetect(RuleSegmentBaseClass):
    def __init__(self, file_sys_handler, logger, app_config) -> None:
        self.__file_sys_handler = file_sys_handler
        self.__app_config = app_config
        self.__logger = logger

    def classify_segment(self, segment_data_list: list, header: object, footer: object, ocr_file_path_list: list) -> list:
        if not ocr_file_path_list:
            return segment_data_list

        if header is None and footer is None:
            return segment_data_list

        doc_dimensions = []
        for ocr_file_path in ocr_file_path_list:
            data = json.loads(self.__file_sys_handler.read_file(
                ocr_file_path))
            doc_dimensions.append((data['height'], data['width']))

        new_segment_data_list = []
        for page_index, dimensions in enumerate(doc_dimensions):
            page_height, page_width = dimensions[0], dimensions[1]
            page_segments = [
                seg for seg in segment_data_list if seg['page'] == page_index + 1]

            # Rule 1: Identify potential headers/footers based on position
            potential_headers, potential_footers = self.identify_potential_headers_footers(
                page_segments, page_height, page_width)

            # Rule 2: Check for gap btw headers/footers segments vs segments
            potential_headers_gap, potential_footers_gap = self.check_for_gap(
                page_segments, potential_headers, potential_footers)

            for seg in page_segments:
                if seg in potential_headers_gap:
                    seg['content_type'] = 'header'
                elif seg in potential_footers_gap:
                    seg['content_type'] = 'footer'
                new_segment_data_list.append(seg)

        return new_segment_data_list

    def identify_potential_headers_footers(self, page_segments, page_height, page_width):
        headers = []
        footers = []
        for seg in page_segments:
            _, y1, _, y2 = seg['content_bbox']
            top_threshold = page_height * 0.1  # Top 10% of the page
            bottom_threshold = page_height * 0.9  # Bottom 90% of the page

            if y1 <= top_threshold:
                headers.append(seg)
            elif y2 >= bottom_threshold:
                footers.append(seg)
        return headers, footers

    def check_for_gap(self, page_segments, potential_headers, potential_footers):
        headers_with_gap = []
        footers_with_gap = []
        threshold = 75

        for header in potential_headers:
            _, header_y1, _, header_y2 = header['content_bbox']
            gaps_above = [header_y1 - seg['content_bbox'][3]
                          for seg in page_segments if 0 < header_y1 - seg['content_bbox'][3] <= threshold]
            gaps_below = [seg['content_bbox'][1] - header_y2 for seg in page_segments if 0 <
                          seg['content_bbox'][1] - header_y2 <= threshold]

            if (len(gaps_above) <= 2 and not gaps_below) or (len(gaps_below) <= 2 and not gaps_above):
                if len(gaps_above) == 2 and max(gaps_above) - min(gaps_above) > threshold:
                    continue
                if len(gaps_below) == 2 and max(gaps_below) - min(gaps_below) > threshold:
                    continue
                headers_with_gap.append(header)

        for footer in potential_footers:
            _, footer_y1, _, footer_y2 = footer['content_bbox']
            gaps_above = [footer_y1 - seg['content_bbox'][3]
                          for seg in page_segments if 0 < footer_y1 - seg['content_bbox'][3] <= threshold]
            gaps_below = [seg['content_bbox'][1] - footer_y2 for seg in page_segments if 0 <
                          seg['content_bbox'][1] - footer_y2 <= threshold]

            if (not gaps_above and len(gaps_below) <= 2) or (not gaps_below and len(gaps_above) <= 2):
                if len(gaps_above) == 2 and max(gaps_above) - min(gaps_above) > threshold:
                    continue
                if len(gaps_below) == 2 and max(gaps_below) - min(gaps_below) > threshold:
                    continue
                footers_with_gap.append(footer)

        return headers_with_gap, footers_with_gap

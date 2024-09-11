# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import json
import infy_fs_utils
import infy_dpp_sdk
from infy_dpp_segmentation.segment_classifier.rules.rule_segment_base_class import RuleSegmentBaseClass


class RuleSegmentManuallyDetect(RuleSegmentBaseClass):
    def __init__(self) -> None:
        self.__file_sys_handler = infy_fs_utils.manager.FileSystemManager(
        ).get_fs_handler(infy_dpp_sdk.common.Constants.FSH_DPP)

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
            page_height = dimensions[0]
            page_segments = [
                seg for seg in segment_data_list if seg['page'] == page_index + 1]

            if header:
                header_min_height_px = page_height * \
                    (header['min_height_percent'] / 100.0)
                header_max_height_px = page_height * \
                    (header['max_height_percent'] / 100.0)
            if footer:
                footer_min_height_px = page_height * \
                    (footer['min_height_percent'] / 100.0)
                footer_max_height_px = page_height * \
                    (footer['max_height_percent'] / 100.0)

            for segment_data in page_segments:
                bbox = segment_data.get('content_bbox')
                if bbox:
                    if header and header_min_height_px <= bbox[3] <= header_max_height_px:
                        segment_data['content_type'] = "header"
                    elif footer and footer_min_height_px <= bbox[1] <= footer_max_height_px:
                        segment_data['content_type'] = "footer"
                new_segment_data_list.append(segment_data)

        return new_segment_data_list

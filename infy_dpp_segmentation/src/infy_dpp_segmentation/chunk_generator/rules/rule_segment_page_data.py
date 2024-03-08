# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                   #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

from infy_dpp_segmentation.common.file_util import FileUtil
from infy_dpp_segmentation.chunk_generator.rules.rule_segment_base_class import RuleSegmentBaseClass


class RuleSegmentPageData(RuleSegmentBaseClass):
    def __init__(self) -> None:
        super().__init__()

    def pre_hook_page_list(self, page_list, exclude_types_list):
        self._page_list = page_list
        self._exclude_types_list = exclude_types_list

    def group_segment_data(self, segment_data_list: list) -> dict:
        output_dict = {}
        page_data_dict, meta_data_dict = {}, {}
        for idx, segment_data in enumerate(segment_data_list):
            # print(segment_data)
            page_no = segment_data['page']
            content_type = segment_data['content_type']
            if page_no in self._page_list and content_type not in self._exclude_types_list:
                if page_no in page_data_dict:
                    content = f'\n{segment_data["content"]}'
                    page_data_dict[page_no] += content
                else:
                    page_bbox = [min(x['content_bbox'][0] for x in segment_data_list if x['page'] == page_no),
                                 min(x['content_bbox'][1]
                                     for x in segment_data_list if x['page'] == page_no),
                                 max(x['content_bbox'][2]
                                     for x in segment_data_list if x['page'] == page_no),
                                 max(x['content_bbox'][3] for x in segment_data_list if x['page'] == page_no)]
                    content = f'{segment_data["content"]}'
                    page_data_dict[page_no] = content
                    meta_data_dict[f'{page_no}.txt_metadata'] = {
                        "chunk_id": FileUtil.get_uuid()[:5],
                        "page_no": page_no,
                        "sequence_no": 1,
                        "bbox_format": "X1,Y1,X2,Y2",
                        "bbox": page_bbox,
                        "doc_name": segment_data['doc_name'],
                        "document_id": segment_data['document_id']
                    }
        output_dict['page_data'] = page_data_dict
        output_dict['meta_data'] = meta_data_dict
        return output_dict

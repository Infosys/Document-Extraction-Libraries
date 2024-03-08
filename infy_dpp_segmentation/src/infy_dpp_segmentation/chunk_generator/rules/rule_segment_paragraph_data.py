# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                   #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

from infy_dpp_segmentation.common.file_util import FileUtil
from infy_dpp_segmentation.chunk_generator.rules.rule_segment_base_class import RuleSegmentBaseClass


class RuleSegmentParagraphData(RuleSegmentBaseClass):
    def __init__(self) -> None:
        super().__init__()

    def pre_hook_page_list(self,page_list,exclude_types_list):
        self._page_list = page_list
        self._exclude_types_list = exclude_types_list

    def group_segment_data(self, segment_data_list: list) -> dict:
        output_dict={}
        page_data_dict,meta_data_dict={},{}
        for idx,segment_data in enumerate(segment_data_list):
            # print(segment_data)
            page_no = segment_data['page']
            sequence_no = segment_data['sequence']
            content_type = segment_data['content_type']
            page_seq_comb = f'{page_no}_{sequence_no}'
            if page_no in self._page_list and content_type not in self._exclude_types_list:
                content = f'{segment_data["content"]}'
                page_data_dict[page_seq_comb] = content
                meta_data_dict[f'{page_seq_comb}.txt_metadata']={
                    "chunk_id":FileUtil.get_uuid()[:5],
                    "page_no":page_no,
                    "sequence_no": sequence_no,
                    "bbox_format": "X1,Y1,X2,Y2",
                    "bbox": segment_data['content_bbox'],
                    "doc_name": segment_data['doc_name'],
                    "document_id": segment_data['document_id']
                }
        output_dict['page_data'] = page_data_dict
        output_dict['meta_data'] = meta_data_dict
        return output_dict
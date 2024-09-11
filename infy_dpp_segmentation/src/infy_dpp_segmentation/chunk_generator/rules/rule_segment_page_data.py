# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                   #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

from langchain_text_splitters import RecursiveCharacterTextSplitter
from infy_dpp_segmentation.common.file_util import FileUtil
from infy_dpp_segmentation.chunk_generator.rules.rule_segment_base_class import RuleSegmentBaseClass


class RuleSegmentPageData(RuleSegmentBaseClass):
    def __init__(self) -> None:
        super().__init__()

    def pre_hook_page_list(self, page_list, exclude_types_list):
        self._page_list = page_list
        self._exclude_types_list = exclude_types_list

    def group_segment_data(self, segment_data_list: list, resources_file_path: str, max_char_limit: int, chunking_method: str) -> dict:
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
                    page_bbox = None
                    if any('content_bbox' in x and x['content_bbox'] for x in segment_data_list if x['page'] == page_no):
                        page_bbox = [min(x['content_bbox'][0] for x in segment_data_list if x['page'] == page_no),
                                     min(x['content_bbox'][1]
                                         for x in segment_data_list if x['page'] == page_no),
                                     max(x['content_bbox'][2]
                                         for x in segment_data_list if x['page'] == page_no),
                                     max(x['content_bbox'][3] for x in segment_data_list if x['page'] == page_no)]
                    content = f'{segment_data["content"]}'
                    page_data_dict[page_no] = content

                    meta_data_dict[f'{page_no}.txt_metadata'] = {
                        "chunk_id":  f'C-{FileUtil.get_uuid()[:5]}',
                        "page_no": page_no,
                        "sequence_no": 1,
                        "bbox_format": "X1,Y1,X2,Y2",
                        "bbox": page_bbox,
                        "doc_name": segment_data['doc_name'],
                        "document_id": segment_data['document_id'],
                        "char_count": f'{len(page_data_dict)}',
                        "resources": [
                            {
                                "type": "doc_path",
                                "path": resources_file_path
                            }
                        ]
                    }
            output_dict['page_data'] = page_data_dict
            output_dict['meta_data'] = meta_data_dict
       # If max_char_limit is not 0 and chunking maethod page_character  then split page data into character level data
        if chunking_method == 'page_character' and max_char_limit != 0:
            output_dict = self._split_page_data_character_level(
                output_dict, max_char_limit, resources_file_path)

        return output_dict

    def _split_page_data_character_level(self, output_dict, max_char_limit, resources_file_path):
        start_index = 1
        page_data = output_dict['page_data']
        doc_name = output_dict['meta_data']['1.txt_metadata']['doc_name']
        document_id = output_dict['meta_data']['1.txt_metadata']['document_id']
        output_dict, page_data_dict, meta_data_dict = {}, {}, {}
        for page_number, page_text in page_data.items():
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=max_char_limit,
                                                           chunk_overlap=0,
                                                           length_function=len,
                                                           is_separator_regex=False,)
            # Used the recursive_text_splitter to create documents from the current page_text
            character_data_list = text_splitter.create_documents([page_text])

            for page_no, segment_data in enumerate(character_data_list, start=start_index):
                page_seq_comb = f'{page_no}_page_char'
                content = f'{segment_data.page_content}'
                page_data_dict[page_seq_comb] = content
                meta_data_dict[f'{page_seq_comb}.txt_metadata'] = {
                    "chunk_id":  f'C-{FileUtil.get_uuid()[:5]}',
                    "page_no": page_no,
                    "sequence_no": 1,
                    "bbox_format": "X1,Y1,X2,Y2",
                    "bbox": [],
                    "doc_name": doc_name,
                    "document_id": document_id,
                    "char_count": f'{len(content)}',
                    "resources": [
                        {
                            "type": "doc_path",
                            "path": resources_file_path
                        }
                    ]
                }
            output_dict['page_data'] = page_data_dict
            output_dict['meta_data'] = meta_data_dict
            start_index = page_no + 1
        return output_dict

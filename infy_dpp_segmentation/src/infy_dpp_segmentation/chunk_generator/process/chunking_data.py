# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import copy
import re
from infy_dpp_segmentation.chunk_generator.rules.rule_segment_base_class import RuleSegmentBaseClass
from infy_dpp_segmentation.chunk_generator.common.common_util import CommonUtil


class ChunkingData:
    def __init__(self) -> None:
        pass

    def clean_data(self, segment_data_list):
        cleaned_data_list = []
        for segment_data in segment_data_list:
            # remove starting and trailing spaces.
            cleaned_content = re.sub(r"^\s+|\s+$", "", segment_data['content'])
            segment_data.update({'content': cleaned_content})
            cleaned_data_list.append(segment_data)
        return cleaned_data_list

    def group_chunk_data(self, segment_data_list, chunking_method, pages_list, exclude_types_list,
                         merge_title_paragraph):
        if chunking_method == 'page':
            rule_name = 'rule_segment_page_data'
        if chunking_method == 'paragraph':
            rule_name = 'rule_segment_paragraph_data'
            if merge_title_paragraph:
                segment_data_list = self.merge_title_paragraph(
                    segment_data_list)
        rule_class = CommonUtil.get_rule_class_instance(
            rule_name, rc_entity_name='')
        rule_instance: RuleSegmentBaseClass = rule_class()
        rule_result = rule_instance.template_method(
            copy.deepcopy(segment_data_list), pages_list, exclude_types_list)

        return rule_result

    def merge_title_paragraph(self, segment_data_list):
        # Initialize variables
        merged_output = []
        current_merged = None
        # Iterate through the output items
        for item in segment_data_list:
            if item['content_type'] == 'Title':
                if current_merged:
                    merged_output.append(current_merged)
                current_merged = {
                    "content_type": "Merged_Content",
                    "content": item['content'],
                    "content_bbox": item['content_bbox'],
                    "confidence_pct": item['confidence_pct'],
                    "page": item['page'],
                    "sequence": item['sequence'],
                    "doc_name": item['doc_name']
                }
            elif (item['content_type'] == 'List') or (item['content_type'] == 'Text'):

                if current_merged:
                    current_merged['content'] += ":" + item['content']
                else:
                    merged_output.append(item)
            else:
                merged_output.append(item)

        # Append the last merged item if present
        if current_merged:
            merged_output.append(current_merged)

        # Generate the final output JSON
        output_json = {
            "merged_output": merged_output
        }
        return merged_output

    # def merge_title_paragraph(self,segment_data_list):
    #     t_p_group, cur_p =[],[]
    #     for idx,segment_data in enumerate(segment_data_list):
    #         if segment_data['content_type']=='Title' and segment_data_list[idx+1].get('content_type')!='Title':
    #         # if segment_data['content_type']=='Title' and cur_p:
    #             t_p=[]
    #             t_p.append(segment_data)
    #             for i in segment_data_list[idx+1:]:
    #                 if i['content_type']=='Title' or i['page']!=segment_data['page']:
    #                     break
    #                 else:
    #                     t_p.append(i)
    #             t_p_group.append(t_p)
    #         # else:
    #         #     t_p_group.append(segment_data)
    #     return t_p_group

# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import copy
import re
from infy_dpp_segmentation.chunk_generator.rules.rule_segment_base_class import RuleSegmentBaseClass
from infy_dpp_segmentation.chunk_generator.common.common_util import CommonUtil


class ChunkingData:
    def __init__(self, file_sys_handler, logger, app_config) -> None:
        self.__logger = logger
        self.__app_config = app_config
        self.__file_sys_handler = file_sys_handler

    def clean_data(self, segment_data_list):
        cleaned_data_list = []
        for segment_data in segment_data_list:
            # remove starting and trailing spaces.
            cleaned_content = re.sub(r"^\s+|\s+$", "", segment_data['content'])
            segment_data.update({'content': cleaned_content})
            cleaned_data_list.append(segment_data)
        return cleaned_data_list

    def group_chunk_data(self, segment_data_list, chunking_method, pages_list, exclude_types_list, merge_title_paragraph, resource_file_dict):
        results = {}
        for method, config in chunking_method.items():
            if config.get('enabled', False):  # Check if the method is enabled
                if method == 'page':
                    rule_name = 'rule_segment_page_data'
                elif method == 'segment':
                    rule_name = 'rule_segment_segment_data'
                elif method == 'page_character':
                    rule_name = 'rule_segment_page_data'
                elif method == 'page_and_segment_type':
                    rule_name = 'rule_segment_page_segment_type_data'

                if rule_name:
                    rule_class = CommonUtil.get_rule_class_instance(
                        rule_name, rc_entity_name='')
                    rule_instance: RuleSegmentBaseClass = rule_class(
                        self.__file_sys_handler, self.__logger, self.__app_config)
                    rule_result = rule_instance.template_method(
                        copy.deepcopy(segment_data_list), pages_list, exclude_types_list, resource_file_dict, method, config)
                    results[method] = rule_result

        return results

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

    def replace_data(self, cleaned_segment_data_list, replace_dict):
        if replace_dict:
            for replace_item in replace_dict:
                find = replace_item["find"]
                replace = replace_item["replace"]
                for segment_data in cleaned_segment_data_list:
                    if find in segment_data['content']:
                        segment_data['content'] = segment_data['content'].replace(
                            find, replace)
        return cleaned_segment_data_list

    def delimit_segment(self, cleaned_segment_data_list, segment_delimeter):
        # Add the delimiter to the 'content' of each segment
        for item in cleaned_segment_data_list:
            item['content'] += segment_delimeter

        return cleaned_segment_data_list

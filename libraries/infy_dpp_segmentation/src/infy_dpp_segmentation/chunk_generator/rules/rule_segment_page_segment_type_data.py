# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

from langchain_text_splitters import RecursiveCharacterTextSplitter
from infy_dpp_segmentation.common.file_util import FileUtil
from infy_dpp_segmentation.chunk_generator.rules.rule_segment_base_class import RuleSegmentBaseClass


class RuleSegmentPageSegmentTypeData(RuleSegmentBaseClass):
    def __init__(self, file_sys_handler, logger, app_config) -> None:
        super().__init__()
        self.__file_sys_handler = file_sys_handler
        self.__app_config = app_config
        self.__logger = logger

    def pre_hook_page_list(self, page_list, exclude_types_list):
        self._page_list = page_list
        self._exclude_types_list = exclude_types_list

    def group_segment_data(self, segment_data_list: list, resource_file_dict: dict, chunking_method: str, config: object) -> dict:
        output_dict = {}
        page_data_dict, meta_data_dict = {}, {}
        keep_together = config.get('keep_together', {})
        keep_seperate = config.get('keep_seperate', {})
        if chunking_method == 'page_and_segment_type':
            for idx, segment_data in enumerate(segment_data_list):
                page_no_base = str(segment_data['page']) + '_page_segment_type'
                content_type = segment_data['content_type']
                if keep_together:
                    # append suffix based on enabled content type
                    suffixes = []
                    if keep_together.get('text', {}).get('enabled', False):
                        suffixes.append('text')
                    if keep_together.get('table', {}).get('enabled', False):
                        suffixes.append('table')
                    if keep_together.get('image', {}).get('enabled', False):
                        suffixes.append('image')
                    suffix_str = '_'.join(suffixes)
                    page_no = f"{page_no_base}_{suffix_str}_1"
                    chunking_method_with_suffix = f"{chunking_method}_{suffix_str}"

                    if int(page_no.split('_', maxsplit=1)[0]) in self._page_list and content_type not in self._exclude_types_list:
                        if (content_type == 'line' and keep_together.get('text', {}).get('enabled', False)) or \
                            (content_type == 'table' and keep_together.get('table', {}).get('enabled', False)) or \
                                (content_type == 'image_text' and keep_together.get('image', {}).get('enabled', False)):
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

                                page_data_dict[f'{page_no}'] = content
                                meta_data_dict[f'{page_no}.txt_metadata'] = {
                                    "chunk_id":  f'C-{FileUtil.get_uuid()[:5]}',
                                    "page_no": int(page_no.split('_', maxsplit=1)[0]),
                                    "sequence_no": 1,
                                    "bbox_format": "X1,Y1,X2,Y2",
                                    "bbox": page_bbox,
                                    "doc_name": segment_data['doc_name'],
                                    "document_id": segment_data['document_id'],
                                    "chunking_method": chunking_method_with_suffix,
                                    "char_count": f'{len(page_data_dict)}',
                                    "resources": [
                                        {
                                            "type": resource_file_dict.get('type', ''),
                                            "path": resource_file_dict.get('path', '')
                                        }
                                    ]
                                }
                    output_dict['page_data'] = page_data_dict
                    output_dict['meta_data'] = meta_data_dict
                if keep_seperate:
                    # append suffix based on enabled content type
                    sequence_no = 0
                    if keep_seperate.get('text', {}).get('enabled', False) and content_type == 'line':
                        page_no = f"{page_no_base}_text_1"
                        chunking_method_with_suffix = f"{chunking_method}_text"
                    elif keep_seperate.get('table', {}).get('enabled', False) and content_type == 'table':
                        sequence_no = sum(1 for x in page_data_dict if x.startswith(
                            f"{page_no_base}_table"))
                        page_no = f"{page_no_base}_table_{sequence_no + 1}"
                        chunking_method_with_suffix = f"{chunking_method}_table"
                    elif keep_seperate.get('image', {}).get('enabled', False) and content_type == 'image_text':
                        sequence_no = sum(1 for x in page_data_dict if x.startswith(
                            f"{page_no_base}_image"))
                        page_no = f"{page_no_base}_image_{sequence_no + 1}"
                        chunking_method_with_suffix = f"{chunking_method}_image"
                    else:
                        continue

                    if int(page_no.split('_', maxsplit=1)[0]) in self._page_list and content_type not in self._exclude_types_list:
                        if page_no in page_data_dict:
                            content = f'\n{segment_data["content"]}'
                            page_data_dict[page_no] += content
                        else:
                            page_bbox = None
                            if any('content_bbox' in x and x['content_bbox'] for x in segment_data_list if x['page'] == page_no_base):
                                page_bbox = [min(x['content_bbox'][0] for x in segment_data_list if x['page'] == page_no_base),
                                             min(x['content_bbox'][1]
                                                 for x in segment_data_list if x['page'] == page_no_base),
                                             max(x['content_bbox'][2]
                                                 for x in segment_data_list if x['page'] == page_no_base),
                                             max(x['content_bbox'][3] for x in segment_data_list if x['page'] == page_no_base)]
                            content = f'{segment_data["content"]}'

                            page_data_dict[f'{page_no}'] = content
                            meta_data_dict[f'{page_no}.txt_metadata'] = {
                                "chunk_id":  f'C-{FileUtil.get_uuid()[:5]}',
                                "page_no": int(page_no.split('_', maxsplit=1)[0]),
                                "sequence_no": sequence_no + 1,
                                "bbox_format": "X1,Y1,X2,Y2",
                                "bbox": page_bbox,
                                "doc_name": segment_data['doc_name'],
                                "document_id": segment_data['document_id'],
                                "chunking_method": chunking_method_with_suffix,
                                "char_count": f'{len(page_data_dict)}',
                                "resources": [
                                    {
                                        "type": resource_file_dict.get('type', ''),
                                        "path": resource_file_dict.get('path', '')
                                    }
                                ]
                            }
                    output_dict['page_data'] = page_data_dict
                    output_dict['meta_data'] = meta_data_dict

        return output_dict

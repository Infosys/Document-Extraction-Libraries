# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import re
import infy_dpp_sdk
import infy_fs_utils
from infy_dpp_sdk.data import *
from infy_dpp_core.common.file_util import FileUtil
from infy_dpp_segmentation.chunk_generator.process.chunking_data import ChunkingData
from infy_dpp_segmentation.chunk_generator.process.chunk_saver import ChunkSaver

PROCESSEOR_CONTEXT_DATA_NAME = "chunk_generator"


class ChunkGenerator(infy_dpp_sdk.interface.IProcessor):
    def __init__(self):
        self.__file_sys_handler = infy_fs_utils.manager.FileSystemManager(
        ).get_fs_handler(infy_dpp_sdk.common.Constants.FSH_DPP)

    def do_execute(self, document_data: DocumentData, context_data: dict, config_data: dict) -> ProcessorResponseData:
        chunking_data_obj = ChunkingData()
        save_chunk_data_obj = ChunkSaver()
        processor_response_data = ProcessorResponseData()
        context_data = context_data if context_data else {}
        processor_config_data = config_data['ChunkGenerator']
        processor_data = {
            "document_data": document_data.json(), "context_data": context_data}
        raw_data_dict = document_data.raw_data.dict()
        segment_data_list = raw_data_dict.get('segment_data')
        page_pattern_list = processor_config_data.get('page_num', [])
        # total_pages = len(set([i['page'] for i in segment_data_list]))
        total_pages = 100000
        extracted_page_list = set([i['page'] for i in segment_data_list])
        pages_list = self.lookp_up_page(total_pages, page_pattern_list)
        pages_list = list(set(pages_list).intersection(
            set(extracted_page_list)))
        cleaned_segment_data_list = chunking_data_obj.clean_data(
            segment_data_list)
        chunking_method = processor_config_data['chunking_method']
        max_char_limit = processor_config_data.get('max_char_limit', 0)
        replace_dict = processor_config_data.get('replace', [])
        cleaned_segment_data_list = chunking_data_obj.replace_data(
            cleaned_segment_data_list, replace_dict)
        segment_delimeter = processor_config_data.get('segment_delimeter', "")
        cleaned_segment_data_list = chunking_data_obj.delimit_segment(
            cleaned_segment_data_list, segment_delimeter)
        document_data.raw_data.segment_data = cleaned_segment_data_list
        exclude_types_list = processor_config_data.get('exclude', [])
        doc_name = document_data.metadata.standard_data.filename.value
        document_id = document_data.document_id
        # updating doc name in segment data
        _ = [i.update({'doc_name': doc_name,
                       'document_id': document_id})
             for i in cleaned_segment_data_list]
        merged_title_paragraph = processor_config_data.get(
            'merge_title_paragraph', False)

        # resource-saving logic
        doc_file_path = context_data.get(
            'request_creator', {}).get('work_file_path', '')
        document_id_start = document_id.split('-')[0]
        new_uuid = str(FileUtil.get_uuid()).split('-')
        new_uuid[0] = document_id_start
        combined_uuid = '-'.join(new_uuid)
        file_extension = '.' + doc_file_path.split('.')[-1]
        new_filename = f"{combined_uuid}{file_extension}"
        resource_base_path = processor_config_data.get(
            'resources', {}).get('resources_path', '')
        self.__file_sys_handler.create_folders(resource_base_path)
        resources_file_path = f"{resource_base_path}/{new_filename}"
        self.__file_sys_handler.copy_file(doc_file_path, resources_file_path)

        output_data = chunking_data_obj.group_chunk_data(
            cleaned_segment_data_list, chunking_method, pages_list, exclude_types_list, merged_title_paragraph, resources_file_path, max_char_limit)
        page_segment_data_dict, meta_data_dict = output_data['page_data'], output_data['meta_data']
        # raw_data=infy_dpp_sdk.data.RawData(table_data=[],key_value_data=[],heading_data=[],
        #                                         page_header_data=[],
        #                                         page_footer_data=[],other_data=[],segment_data=cleaned_segment_data_list)
        # document_data.raw_data = raw_data

        # chunk-saving logic
        save_chunk_config = processor_config_data['chunks']
        chunked_file_path_list, chunked_file_meta_data_path_list = save_chunk_data_obj.save_chunk_data(
            page_segment_data_dict, document_id, save_chunk_config, meta_data_dict)

        context_data[PROCESSEOR_CONTEXT_DATA_NAME] = {'cleaned_segment_data': cleaned_segment_data_list,
                                                      "page_segment_data": page_segment_data_dict,
                                                      "meta_data": meta_data_dict,
                                                      'chunked_data_list': chunked_file_path_list,
                                                      "chunked_file_meta_data_list": chunked_file_meta_data_path_list,
                                                      "chunking_method": chunking_method}

        # Populate response data
        processor_response_data.document_data = document_data
        processor_response_data.context_data = context_data

        return processor_response_data

    def lookp_up_page(self, total_pages, page_list):
        pages = []
        for pnum in page_list:
            pnum = pnum if (isinstance(pnum, str) and ((
                ":" in pnum) or ("-" in pnum))) else int(pnum)
            if isinstance(pnum, str):
                num_arr = [int(num)
                           for num in re.split('-|:', pnum) if len(num) > 0]
                if bool(re.match(r'^-?[0-9]+\:{1}-?[0-9]+$', pnum)):
                    page_arr = self.__get_range_val(total_pages+1)
                    if (num_arr[0] < 0 and num_arr[1] < 0) or (num_arr[0] > 0 and num_arr[1] > 0):
                        num_arr.sort()
                    num_arr[0] = num_arr[0] if num_arr[0] > 0 else num_arr[0]-1
                    num_arr[1] = num_arr[1] + \
                        1 if num_arr[1] > 0 else num_arr[1]

                    pages += page_arr[num_arr[0]: num_arr[1]]
                elif bool(re.match(r'^-?[0-9]+\:{1}$', pnum)):
                    page_arr = self.__get_range_val(total_pages)
                    pages += page_arr[num_arr[0]:]
                elif bool(re.match(r'^\:{1}-?[0-9]+$', pnum)):
                    page_arr = self.__get_range_val(
                        total_pages+1, position=1)
                    pages += page_arr[:num_arr[0]]
                else:
                    raise Exception
            elif pnum < 0:
                pages += [self.__get_range_val(
                    total_pages, position=1)[pnum]]
            elif pnum > 0:
                pages.append(pnum)
            else:
                raise Exception
        return pages

    def __get_range_val(self, n, position=0):
        return [i for i in range(position, n+1)]

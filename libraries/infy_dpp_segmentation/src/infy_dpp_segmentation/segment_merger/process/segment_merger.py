# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import os
import cv2
import infy_dpp_sdk
from infy_dpp_sdk.data import DocumentData, ProcessorResponseData
from infy_dpp_segmentation.common.file_util import FileUtil
from infy_dpp_segmentation.common.sorting_util import ImageSortUtil
from infy_dpp_segmentation.segment_merger.process.segment_data_merger_v import SegmentDataMerger

PROCESSOR_CONTEXT_DATA_NAME = "segment_merger"


class SegmentMerger(infy_dpp_sdk.interface.IProcessor):
    def __init__(self):
        self.__file_sys_handler = self.get_fs_handler()
        self.__app_config = self.get_app_config()
        self.__logger = self.get_logger()

    def do_execute(self, document_data: DocumentData, context_data: dict, config_data: dict) -> ProcessorResponseData:
        def __get_temp_file_path(work_file_path):
            local_file_path = f'{self.__app_config["CONTAINER"]["APP_DIR_TEMP_PATH"]}/{work_file_path}'
            FileUtil.create_dirs_if_absent(os.path.dirname(local_file_path))
            with self.__file_sys_handler.get_file_object(work_file_path) as input:
                with open(local_file_path, "wb") as output:
                    output.write(input.read())
            return local_file_path

        processor_response_data = ProcessorResponseData()
        context_data = context_data if context_data else {}
        org_files_full_path = context_data['request_creator']['work_file_path']
        from_files_full_path = __get_temp_file_path(org_files_full_path)
        out_file_full_path = f'{from_files_full_path}_files'
        merger_config = config_data['SegmentMerger']
        raw_data_dict = document_data.raw_data.dict()
        combined_segments_list = []
        combined_segments_list.append(raw_data_dict.get('segment_data'))
        technique_supported = False
        if not document_data.metadata.standard_data.filename.value.endswith('.txt'):
            technique_supported = True

        prefer_larger_segments = merger_config.get(
            'prefer_larger_segments')
        merge_requirements = merger_config.get('merge')
        if merge_requirements.get('enabled') and not technique_supported:
            merge_requirements['enabled'] = False
        if combined_segments_list:
            segment_data_merger_obj = SegmentDataMerger(
                combined_segments_list, prefer_larger_segments)
            merged_segments_list = segment_data_merger_obj.segment_data_merge(
                merge_requirements)

            if merger_config.get('plot_bbox_segments'):
                self.__plot_segments(merged_segments_list,
                                     out_file_full_path, "merged")
        else:
            merged_segments_list = []

        merged_data_dict = {"technique": "merged",
                            "segments": merged_segments_list}
        merged_data_list = []
        merged_data_list.append(merged_data_dict)
        document_data.raw_data.segment_data = merged_segments_list

        org_files_full_path = context_data['request_creator']['work_file_path']
        debug_config = merger_config.get('debug')
        extraction_technique = "merged"
        if debug_config.get('enabled'):
            if debug_config.get('generate_image'):
                self.__plot_bbox(merged_data_list, org_files_full_path,
                                 debug_config, extraction_technique)

        context_data[PROCESSOR_CONTEXT_DATA_NAME] = {
            'segment_data': merged_data_list}

        processor_response_data.document_data = document_data
        processor_response_data.context_data = context_data

        return processor_response_data

    def __plot_segments(self, segment_data_list, out_file_full_path, extraction_technique):
        def __insert_list(segment_data_list: list, page_number: int):
            page_list = []
            for item in segment_data_list:
                if (item['page'] == page_number):
                    page_list.append(item)
            return page_list

        def __draw_bbox(image_file_path: str, tokens: list):
            img_path = image_file_path
            file_extension = os.path.splitext(img_path)[-1]
            FileUtil.create_dirs_if_absent(
                f'{os.path.dirname(img_path)}/segment_data')
            bbox_img_file_path = f'{os.path.dirname(img_path)}/segment_data/{os.path.basename(img_path)}_{extraction_technique}_bbox{file_extension}'

            image_bbox = cv2.imread(img_path)
            token_bbox_list = [x['content_bbox'] for x in tokens]

            if token_bbox_list:
                for idx, bbox in enumerate(token_bbox_list):
                    start, end = (int(bbox[0]), int(
                        bbox[1])), (int(bbox[2]), int(bbox[3]))
                    cv2.rectangle(image_bbox, start, end, (0, 0, 255), 2)
                    cv2.putText(image_bbox, f"{idx+1}: {start},{end}", (
                        start[0], start[1]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)

            cv2.imwrite(bbox_img_file_path, image_bbox)
            return bbox_img_file_path

        page_segment_list = []
        if os.path.isdir(out_file_full_path) and any(os.path.isfile(os.path.join(out_file_full_path, file)) and file.endswith('.jpg') for file in os.listdir(out_file_full_path)):
            img_file_path_list = [os.path.join(out_file_full_path, file) for file in os.listdir(
                out_file_full_path) if file.endswith('.jpg')]
            img_file_path_list = ImageSortUtil.sort_image_files(
                img_file_path_list)
            for page_number in range(1, len(img_file_path_list)+1):
                group_list = __insert_list(segment_data_list, page_number)
                page_segment_list.append(group_list)
            for index, image_path in enumerate(img_file_path_list):
                __draw_bbox(image_path, page_segment_list[index])

    def __plot_bbox(self, merged_data_list, org_files_full_path, debug_config, extraction_technique):
        def __get_storage_file_path(org_files_full_path):
            org_files_full_path = f'{org_files_full_path}_files'
            self.__file_sys_handler.create_folders(org_files_full_path)
            return org_files_full_path

        def __insert_list(merged_data_list: list, page_number: int):
            page_list = []
            if merged_data_list:
                for item in merged_data_list[0]['segments']:
                    if (item['page'] == page_number):
                        page_list.append(item)
            return page_list

        def __draw_bbox(debug_file_path: str, image_file_path: str, tokens: list, output_dir: str, extraction_technique: str):
            img_path = image_file_path
            file_extension = img_path[img_path.rfind('.'):]
            filename = img_path[img_path.rfind('/') + 1:]
            debug_folder_path = f'{debug_file_path}/{output_dir}'
            self.__file_sys_handler.create_folders(debug_folder_path)
            bbox_img_file_path = f'{debug_folder_path}/{(filename)}_{extraction_technique}_bbox{file_extension}'
            abs_img_path = self.__file_sys_handler.get_abs_path(
                img_path).replace('filefile://', '')
            abs_bbox_img_file_path = self.__file_sys_handler.get_abs_path(
                bbox_img_file_path).replace('filefile://', '')

            image_bbox = cv2.imread(abs_img_path)
            token_bbox_list = [x['content_bbox'] for x in tokens]

            if token_bbox_list:
                for idx, bbox in enumerate(token_bbox_list):
                    start, end = (int(bbox[0]), int(
                        bbox[1])), (int(bbox[2]), int(bbox[3]))
                    cv2.rectangle(image_bbox, start, end, (0, 0, 255), 2)
                    cv2.putText(image_bbox, f"{idx+1}: {start},{end}", (
                        start[0], start[1]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)

            cv2.imwrite(abs_bbox_img_file_path, image_bbox)
            return bbox_img_file_path

        page_segment_list = []
        output_dir = debug_config.get('output_dir_path')
        debug_file_path = __get_storage_file_path(org_files_full_path)
        if self.__file_sys_handler.exists(debug_file_path) and self.__file_sys_handler.list_files(debug_file_path, file_filter='*.jpg'):
            img_file_path_list = [f"{file}" for file in self.__file_sys_handler.list_files(
                debug_file_path, file_filter='*.jpg')]
            img_file_path_list = ImageSortUtil.sort_image_files(
                img_file_path_list)
            for page_number in range(1, len(img_file_path_list)+1):
                group_list = __insert_list(merged_data_list, page_number)
                page_segment_list.append(group_list)
            for index, image_path in enumerate(img_file_path_list):
                __draw_bbox(debug_file_path, image_path,
                            page_segment_list[index], output_dir, extraction_technique)

# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                   #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import os
import cv2
import infy_dpp_sdk
from infy_dpp_sdk.data import DocumentData, ProcessorResponseData
from infy_dpp_segmentation.common.file_util import FileUtil
from infy_dpp_segmentation.segment_consolidator.process.segment_data_consolidator import SegmentDataConsolidator

PROCESSOR_CONTEXT_DATA_NAME = "segment_consolidator"


class SegmentConsolidator(infy_dpp_sdk.interface.IProcessor):
    def __init__(self):
        self.__app_config = infy_dpp_sdk.common.AppConfigManager().get_app_config()

    def do_execute(self, document_data: DocumentData, context_data: dict, config_data: dict) -> ProcessorResponseData:

        processor_response_data = ProcessorResponseData()
        context_data = context_data if context_data else {}

        consolidator_config = config_data['SegmentConsolidator']
        segment_data_list = context_data.get(
            'segment_generator')['segment_data']

        # segment_data_list = context_data.get('segment_generator')['segment_data']
        if consolidator_config.get('enabled'):
            technique_supported = False
            consolidated_segments = []
            for segment_data in segment_data_list:
                if segment_data.get("technique") != 'text' and not segment_data['technique'].startswith('column_'):
                    consolidated_segments.append(segment_data["segments"])
                    technique_supported = True
                elif segment_data.get("technique") == 'text':
                    consolidated_segments.extend(segment_data["segments"])

            if consolidated_segments and technique_supported:
                segment_consolidator_obj = SegmentDataConsolidator(
                    consolidated_segments)
                consolidated_segments = segment_consolidator_obj.segment_data_merge()

                org_files_full_path = context_data['request_creator']['work_file_path']
                debug_config = consolidator_config.get('debug')
                extraction_technique = "consolidated"
                if debug_config.get('enabled'):
                    if debug_config.get('generate_image'):
                        self.__plot_bbox(
                            consolidated_segments, org_files_full_path, debug_config, extraction_technique)

            consolidated_data_dict = {"technique": "consolidated",
                                      "segments": consolidated_segments}
            consolidated_data_list = []
            consolidated_data_list.append(consolidated_data_dict)
            document_data.raw_data.segment_data = consolidated_segments

            context_data[PROCESSOR_CONTEXT_DATA_NAME] = {
                'segment_data': consolidated_data_list}
        # Populate response data
        processor_response_data.document_data = document_data
        processor_response_data.context_data = context_data

        return processor_response_data

    def __plot_bbox(self, consolidated_segments, org_files_full_path, debug_config, extraction_technique):
        def __get_storage_file_path(org_files_full_path):
            org_files_full_path = f'{org_files_full_path}_files'
            local_file_path = f'{self.__app_config["CONTAINER"]["container_root_path"]}/{org_files_full_path}'
            local_file_path = local_file_path.replace("CONTAINER", "STORAGE")
            FileUtil.create_dirs_if_absent(os.path.dirname(local_file_path))
            return local_file_path

        def __insert_list(consolidated_segments: list, page_number: int):
            page_list = []
            for item in consolidated_segments:
                if (item['page'] == page_number):
                    page_list.append(item)
            return page_list

        def __draw_bbox(image_file_path: str, tokens: list, output_dir: str, extraction_technique: str):
            img_path = image_file_path
            file_extension = os.path.splitext(img_path)[-1]
            FileUtil.create_dirs_if_absent(
                f'{os.path.dirname(img_path)}/{output_dir}')
            bbox_img_file_path = f'{os.path.dirname(img_path)}/{output_dir}/{os.path.basename(img_path)}_{extraction_technique}_bbox{file_extension}'

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
        output_dir = debug_config.get('output_dir_path')
        debug_file_path = __get_storage_file_path(org_files_full_path)
        if os.path.isdir(debug_file_path) and any(os.path.isfile(os.path.join(debug_file_path, file)) and file.endswith('.jpg') for file in os.listdir(debug_file_path)):
            img_file_path_list = [os.path.join(debug_file_path, file) for file in os.listdir(
                debug_file_path) if file.endswith('.jpg')]
            for page_number in range(1, len(img_file_path_list)+1):
                group_list = __insert_list(consolidated_segments, page_number)
                page_segment_list.append(group_list)
            for index, image_path in enumerate(img_file_path_list):
                __draw_bbox(
                    image_path, page_segment_list[index], output_dir, extraction_technique)

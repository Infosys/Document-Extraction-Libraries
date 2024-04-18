# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                   #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import os
import cv2
import infy_dpp_sdk
from infy_dpp_sdk.data import DocumentData, ProcessorResponseData
from infy_dpp_segmentation.segment_sequencer.process.segment_data import SegementData
from infy_dpp_segmentation.common.file_util import FileUtil

PROCESSEOR_CONTEXT_DATA_NAME = "segment_sequencer"


class SegmentSequencer(infy_dpp_sdk.interface.IProcessor):
    def __init__(self):
        self.__app_config = infy_dpp_sdk.common.AppConfigManager().get_app_config()

    def do_execute(self, document_data: DocumentData, context_data: dict, config_data: dict) -> ProcessorResponseData:
        processor_response_data = ProcessorResponseData()
        context_data = context_data if context_data else {}
        sequencer_config = config_data['SegmentSequencer']
        raw_data_dict = document_data.raw_data.dict()
        segment_data_list = []
        segment_data_list = raw_data_dict.get('segment_data')

        pattern = None
        layout = None
        segments = context_data['page_column_detector']['segment_data'][0]['segments']
        if not segments:
            pages = {1: []}
        else:
            pages = {}
            for segment in segments:
                page = segment.get('page', 1)
                if page not in pages:
                    pages[page] = []
                pages[page].append(segment)

        for page, segments in pages.items():
            if len(segments) > 1:
                layout = 'multi-column'
            else:
                layout = 'single-column'

            if sequencer_config.get('pattern').get(layout):
                for sub_pattern_key, sub_val in sequencer_config.get('pattern').get(layout).items():
                    if sub_val.get('enabled'):
                        pattern = sub_pattern_key
                        break
                else:
                    if layout == 'single-column':
                        pattern = 'sequence-order'
                    elif layout == 'multi-column':
                        pattern = 'zig-zag'

            updated_segment_data_list = SegementData().update_sequence(
                segment_data_list, layout, pattern)
            document_data.raw_data.segment_data = updated_segment_data_list
            sequencer_technique = None
            sequencer_list = None
            sequencer_data_dict = []
            sequencer_technique = pattern
            sequencer_list = {"technique": sequencer_technique,
                              "segments": updated_segment_data_list}
            sequencer_data_dict.append(sequencer_list)

            org_files_full_path = context_data['request_creator']['work_file_path']
            debug_config = sequencer_config.get('debug')
            if debug_config.get('enabled'):
                if debug_config.get('generate_image'):
                    self.__plot_bbox(updated_segment_data_list,
                                     org_files_full_path, debug_config)

            context_data[PROCESSEOR_CONTEXT_DATA_NAME] = {
                'segment_data': sequencer_data_dict}

            processor_response_data.document_data = document_data
            processor_response_data.context_data = context_data

            return processor_response_data

    def __plot_bbox(self, updated_segment_data_list, org_files_full_path, debug_config):
        def __get_storage_file_path(org_files_full_path):
            org_files_full_path = f'{org_files_full_path}_files'
            local_file_path = f'{self.__app_config["CONTAINER"]["container_root_path"]}/{org_files_full_path}'
            local_file_path = local_file_path.replace("CONTAINER", "STORAGE")
            FileUtil.create_dirs_if_absent(os.path.dirname(local_file_path))
            return local_file_path

        def __insert_list(updated_segment_data_list: list, page_number: int):
            page_list = []
            for item in updated_segment_data_list:
                if (item['page'] == page_number):
                    page_list.append(item)
            return page_list

        def __draw_bbox(image_file_path: str, tokens: list, output_dir: str):
            img_path = image_file_path
            file_extension = os.path.splitext(img_path)[-1]
            FileUtil.create_dirs_if_absent(
                f'{os.path.dirname(img_path)}/{output_dir}')
            bbox_img_file_path = f'{os.path.dirname(img_path)}/{output_dir}/{os.path.basename(img_path)}_sequencer_bbox{file_extension}'

            image_bbox = cv2.imread(img_path)
            token_bbox_list = [x['content_bbox'] for x in tokens]

            if token_bbox_list:
                for idx, bbox in enumerate(token_bbox_list):
                    if len(bbox) == 4:
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
                group_list = __insert_list(
                    updated_segment_data_list, page_number)
                page_segment_list.append(group_list)
            for index, image_path in enumerate(img_file_path_list):
                __draw_bbox(image_path, page_segment_list[index], output_dir)

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

PROCESSOR_CONTEXT_DATA_NAME = "page_column_detector"


class PageColumnDetector(infy_dpp_sdk.interface.IProcessor):
    def __init__(self):
        self.__app_config = infy_dpp_sdk.common.AppConfigManager().get_app_config()

    def do_execute(self, document_data: DocumentData, context_data: dict, config_data: dict) -> ProcessorResponseData:
        processor_response_data = ProcessorResponseData()
        context_data = context_data if context_data else {}
        column_detector_config = config_data['PageColumnDetector']
        raw_data_dict = document_data.raw_data.dict()
        segment_data_list = raw_data_dict.get('segment_data')
        technique_supported = False
        if not document_data.metadata.standard_data.filename.value.endswith('.txt'):
            technique_supported = True

        if technique_supported:
            if column_detector_config.get('exclude'):
                exclude = column_detector_config.get('exclude')
                cleaned_segment_data_list = self.remove_headers_footers(
                    segment_data_list, exclude)
                document_data.raw_data.segment_data = cleaned_segment_data_list

            column_technique = None
            column_list = None

            for technique in column_detector_config['column_techniques']:
                if technique['enabled'] and technique['name'] == 'column_technique1':
                    column_technique = 'column_detection'
                    column_data = self.column_detection(
                        cleaned_segment_data_list)

            org_files_full_path = context_data['request_creator']['work_file_path']
            debug_config = column_detector_config.get('debug')
            if debug_config.get('enabled'):
                if debug_config.get('generate_image'):
                    self.__plot_bbox(
                        column_data, org_files_full_path, debug_config)
        elif not technique_supported:
            column_technique = "text"
            column_data = ""

        column_data_dict = []
        column_list = {"technique": column_technique,
                       "segments": column_data}
        column_data_dict.append(column_list)
        context_data[PROCESSOR_CONTEXT_DATA_NAME] = {
            'segment_data': column_data_dict}

        processor_response_data.document_data = document_data
        processor_response_data.context_data = context_data

        return processor_response_data

    def column_detection(self, cleaned_segment_data_list):
        sorted_data = sorted(cleaned_segment_data_list,
                             key=lambda x: (x['page'], x['content_bbox'][0]))

        columns_list = []
        current_column = [sorted_data[0]]
        br_x_max = sorted_data[0]['content_bbox'][2]
        current_page = sorted_data[0]['page']

        bbox = [sorted_data[0]['content_bbox'][0], sorted_data[0]['content_bbox'][1],
                sorted_data[0]['content_bbox'][2], sorted_data[0]['content_bbox'][3]]

        for i in range(1, len(sorted_data)):
            tl_x = sorted_data[i]['content_bbox'][0]
            br_x = sorted_data[i]['content_bbox'][2]
            page = sorted_data[i]['page']

            if page == current_page and tl_x <= br_x_max:
                current_column.append(sorted_data[i])
                br_x_max = max(br_x_max, br_x)

                bbox[0] = min(bbox[0], sorted_data[i]['content_bbox'][0])
                bbox[1] = min(bbox[1], sorted_data[i]['content_bbox'][1])
                bbox[2] = max(bbox[2], sorted_data[i]['content_bbox'][2])
                bbox[3] = max(bbox[3], sorted_data[i]['content_bbox'][3])
            else:
                column = sorted_data[i].copy()
                column['content_bbox'] = bbox
                column['sequence'] = len(columns_list) + 1
                column['content_type'] = 'column'
                column['content'] = ''
                column['page'] = current_page
                columns_list.append(column)

                current_column = [sorted_data[i]]
                br_x_max = br_x
                current_page = page

                bbox = [sorted_data[i]['content_bbox'][0], sorted_data[i]['content_bbox'][1],
                        sorted_data[i]['content_bbox'][2], sorted_data[i]['content_bbox'][3]]

        column = sorted_data[-1].copy()
        column['content_bbox'] = bbox
        column['sequence'] = len(columns_list) + 1
        column['content_type'] = 'column'
        column['content'] = ''
        column['page'] = current_page
        columns_list.append(column)

        return columns_list

    def remove_headers_footers(self, segment_data_list, exclude):
        cleaned_segment_data_list = []
        for segment_data in segment_data_list:
            if segment_data['content_type'] not in exclude:
                cleaned_segment_data_list.append(segment_data)
        return cleaned_segment_data_list

    def __plot_bbox(self, column_data, org_files_full_path, debug_config):
        def __get_storage_file_path(org_files_full_path):
            org_files_full_path = f'{org_files_full_path}_files'
            local_file_path = f'{self.__app_config["CONTAINER"]["container_root_path"]}/{org_files_full_path}'
            local_file_path = local_file_path.replace("CONTAINER", "STORAGE")
            FileUtil.create_dirs_if_absent(os.path.dirname(local_file_path))
            return local_file_path

        def insert_list(column_data, page_number):
            page_list = []
            for column in column_data:
                if column['page'] == page_number:
                    page_list.append(column)
            return page_list

        def draw_bbox(image_file_path, tokens, output_dir):
            img_path = image_file_path
            file_extension = os.path.splitext(img_path)[-1]
            FileUtil.create_dirs_if_absent(
                f'{os.path.dirname(img_path)}/{output_dir}')
            bbox_img_file_path = f'{os.path.dirname(img_path)}/{output_dir}/{os.path.basename(img_path)}column_bbox{file_extension}'

            image_bbox = cv2.imread(img_path)
            column_tokens = tokens

            if column_tokens:
                for idx, token in enumerate(column_tokens):
                    bbox = token['content_bbox']
                    start, end = (int(bbox[0]), int(
                        bbox[1])), (int(bbox[2]), int(bbox[3]))

                    cv2.rectangle(image_bbox, start, end, (0, 0, 255), 2)
                    cv2.putText(image_bbox, f"{idx+1}: {start},{end}",
                                (start[0], start[1]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)

                cv2.imwrite(bbox_img_file_path, image_bbox)

            return bbox_img_file_path

        page_segment_list = []
        output_dir = debug_config.get('output_dir_path')
        debug_file_path = __get_storage_file_path(org_files_full_path)
        if os.path.isdir(debug_file_path) and any(os.path.isfile(os.path.join(debug_file_path, file)) and file.endswith('.jpg') for file in os.listdir(debug_file_path)):
            img_file_path_list = [os.path.join(debug_file_path, file) for file in os.listdir(
                debug_file_path) if file.endswith('.jpg')]
            for page_number in range(1, len(img_file_path_list)+1):
                columns_for_page = insert_list(column_data, page_number)
                page_segment_list.append(columns_for_page)
                draw_bbox(
                    img_file_path_list[page_number-1], columns_for_page, output_dir)

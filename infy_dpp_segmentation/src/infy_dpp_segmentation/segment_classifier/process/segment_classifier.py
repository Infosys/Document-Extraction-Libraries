# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                   #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import os
import cv2
import infy_dpp_sdk
from infy_dpp_sdk.data import DocumentData, ProcessorResponseData
from infy_dpp_segmentation.segment_classifier.process.segment_classifier_rule_parser import SegmentClassifierRuleParser
from infy_dpp_segmentation.common.file_util import FileUtil

PROCESSEOR_CONTEXT_DATA_NAME = "segment_classifier"


class SegmentClassifier(infy_dpp_sdk.interface.IProcessor):
    def __init__(self):
        self.__app_config = infy_dpp_sdk.common.AppConfigManager().get_app_config()

    def do_execute(self, document_data: DocumentData, context_data: dict, config_data: dict) -> ProcessorResponseData:
        processor_response_data = ProcessorResponseData()
        context_data = context_data if context_data else {}
        segment_classifier_config = config_data['SegmentClassifier']
        raw_data_dict = document_data.raw_data.dict()
        segment_data_list = raw_data_dict.get('segment_data')
        technique_supported = False
        if not document_data.metadata.standard_data.filename.value.endswith('.txt'):
            technique_supported = True
        # data_dict = context_data['segment_generator']
        # segment_data_list = data_dict.get('segment_data')[0].get('segments')
        if technique_supported:
            header = None
            footer = None
            header_config = segment_classifier_config.get('header')
            if header_config and header_config.get('enabled'):
                header = header_config
            footer_config = segment_classifier_config.get('footer')
            if footer_config and footer_config.get('enabled'):
                footer = footer_config
            classified_segment_data_list = SegmentClassifierRuleParser().classify_segments(
                segment_data_list, header, footer)
            document_data.raw_data.segment_data = classified_segment_data_list
            classification_technique = None
            segment_list = None
            classification_technique = "header_footer"

            org_files_full_path = context_data['request_creator']['work_file_path']
            debug_config = segment_classifier_config.get('debug')
            if debug_config.get('enabled'):
                if debug_config.get('generate_image'):
                    self.__plot_bbox(classified_segment_data_list,
                                     org_files_full_path, debug_config)
        elif not technique_supported:
            classified_segment_data_list = segment_data_list
            classification_technique = "text"

        segment_data_dict = []
        segment_list = {"technique": classification_technique,
                        "segments": classified_segment_data_list}
        segment_data_dict.append(segment_list)
        context_data[PROCESSEOR_CONTEXT_DATA_NAME] = {
            'segment_data': segment_data_dict}

        processor_response_data.document_data = document_data
        processor_response_data.context_data = context_data

        return processor_response_data

    def __plot_bbox(self, classified_segment_data_list, org_files_full_path, debug_config):
        def __get_storage_file_path(org_files_full_path):
            org_files_full_path = f'{org_files_full_path}_files'
            local_file_path = f'{self.__app_config["CONTAINER"]["container_root_path"]}/{org_files_full_path}'
            local_file_path = local_file_path.replace("CONTAINER", "STORAGE")
            FileUtil.create_dirs_if_absent(os.path.dirname(local_file_path))
            return local_file_path

        def __insert_list(classified_segment_data_list: list, page_number: int):
            page_list = []
            for item in classified_segment_data_list:
                if (item['page'] == page_number):
                    page_list.append(item)
            return page_list

        def __draw_bbox(image_file_path: str, tokens: list, output_dir: str):
            img_path = image_file_path
            file_extension = os.path.splitext(img_path)[-1]
            FileUtil.create_dirs_if_absent(
                f'{os.path.dirname(img_path)}/{output_dir}')
            bbox_img_file_path = f'{os.path.dirname(img_path)}/{output_dir}/{os.path.basename(img_path)}header_footer__bbox{file_extension}'

            image_bbox = cv2.imread(img_path)
            header_tokens = [
                x for x in tokens if x['content_type'] == 'header']
            footer_tokens = [
                x for x in tokens if x['content_type'] == 'footer']

            for token_list, color in [(header_tokens, (0, 255, 0)), (footer_tokens, (255, 0, 0))]:
                if token_list:
                    min_x = min(token['content_bbox'][0]
                                for token in token_list)
                    min_y = min(token['content_bbox'][1]
                                for token in token_list)
                    max_x = max(token['content_bbox'][2]
                                for token in token_list)
                    max_y = max(token['content_bbox'][3]
                                for token in token_list)

                    cv2.rectangle(image_bbox,  (int(min_x), int(
                        min_y)), (int(max_x), int(max_y)), color, 2)
                    for idx, token in enumerate(token_list):
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
                group_list = __insert_list(
                    classified_segment_data_list, page_number)
                page_segment_list.append(group_list)
            for index, image_path in enumerate(img_file_path_list):
                __draw_bbox(image_path, page_segment_list[index], output_dir)

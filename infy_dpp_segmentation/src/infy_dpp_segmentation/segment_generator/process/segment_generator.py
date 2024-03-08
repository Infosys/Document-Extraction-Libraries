# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                   #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#
import os
import re
import json
import cv2
import numpy as np
from jsonpath_ng import parse
import infy_dpp_sdk
from infy_dpp_sdk.data import *
from infy_dpp_segmentation.common.file_util import FileUtil

from infy_dpp_segmentation.segment_generator.process.pdf_box_based_segment_generator import PdfBoxBasedSegmentGenerator
from infy_dpp_segmentation.segment_generator.process.ocr_based_segment_generator import OcrBasedSegmentGenerator
from infy_dpp_segmentation.segment_generator.process.segment_data_merger_v import SegmentDataMerger

PROCESSEOR_CONTEXT_DATA_NAME = "segment_generator"


class SegmentGenerator(infy_dpp_sdk.interface.IProcessor):
    def __init__(self):
        self.__file_sys_handler = self.get_fs_handler()
        self.__app_config = infy_dpp_sdk.common.AppConfigManager().get_app_config()
        self.__logger = self.get_logger()

    def do_execute(self, document_data: DocumentData, context_data: dict, config_data: dict) -> ProcessorResponseData:
        def __get_temp_file_path(work_file_path):
            local_file_path = f'{self.__app_config["CONTAINER"]["APP_DIR_TEMP_PATH"]}/{work_file_path}'
            FileUtil.create_dirs_if_absent(os.path.dirname(local_file_path))
            with self.__file_sys_handler.get_file_object(work_file_path) as input:
                with open(local_file_path, "wb") as output:
                    output.write(input.read())
            return local_file_path

        segment_data_list = []
        model_provider_dict = {}
        self._processor_response_data = ProcessorResponseData()
        segment_gen_config_data = config_data.get('SegmentGenerator', {})
        # from_files_full_path = document_data.metadata.standard_data.filepath.value
        org_files_full_path = context_data['request_creator']['work_file_path']
        from_files_full_path = __get_temp_file_path(org_files_full_path)
        _, extension = os.path.splitext(from_files_full_path)
        for technique in segment_gen_config_data.get('techniques', []):
            if not technique.get("enabled"):
                continue
            else:
                input_file_type = technique.get("input_file_type")
                text_provider_name = technique.get("text_provider_name")
                model_provider_name = technique.get("model_provider_name")
                technique_name = technique.get('name')
                if (text_provider_name):
                    text_provider_dict = [textProviders for textProviders in segment_gen_config_data.get(
                        "textProviders") if textProviders.get("provider_name") == text_provider_name][0]
                if (model_provider_name):
                    model_provider_dict = [modelProviders for modelProviders in segment_gen_config_data.get(
                        "modelProviders") if modelProviders.get("provider_name") == model_provider_name][0]
                if input_file_type == 'json' and extension == '.json':
                    extraction_technique = 'json'
                    template_file_path = text_provider_dict.get(
                        "properties").get('template1_file_path')
                elif not input_file_type == 'json' and extension != '.json':
                    if input_file_type == 'pdf' and extension == '.pdf':
                        if model_provider_name:
                            extraction_technique = 'ocr_based'
                        else:
                            extraction_technique = 'native_pdf'
                    elif input_file_type == 'image' and extension in ['.jpg', '.jpeg', '.png']:
                        # ,'.tif','.tiff'
                        extraction_technique = 'ocr_based'  
                    elif input_file_type == 'txt' and extension == '.txt':
                        extraction_technique = 'text'
                    else:
                        continue
                else:
                    continue
            context_data = context_data if context_data else {}
            processor_data = {
                "document_data": document_data.json(), "context_data": context_data}
            out_file_full_path = f'{from_files_full_path}_files'
            if extraction_technique == 'native_pdf':
                pdf_box_seg_gen_obj = PdfBoxBasedSegmentGenerator(
                    text_provider_dict)
                segments_list = pdf_box_seg_gen_obj.get_segment_data(
                    from_files_full_path, out_file_full_path)
                segment_data_dict = {"technique": extraction_technique,
                                     "segments": segments_list}
                segment_data_list.append(segment_data_dict)
            if extraction_technique == 'ocr_based':
                ocr_based_seg_gene_obj = OcrBasedSegmentGenerator(
                    text_provider_dict, model_provider_dict)
                segments_list = ocr_based_seg_gene_obj.get_segment_data(
                    from_files_full_path, out_file_full_path)
                segment_data_dict = {"technique": extraction_technique,
                                     "segments": segments_list}
                segment_data_list.append(segment_data_dict)
            if extraction_technique == 'json':
                flattened_text = self.get_plain_text(
                    template_file_path, from_files_full_path)
                segments_list = []
                segment_data = {}
                segment_data["content_type"] = "document"
                segment_data["content"] = flattened_text
                segment_data["bbox_format"] = "X1,Y1,X2,Y2"
                segment_data["content_bbox"] = []
                segment_data["confidence_pct"] = -1
                segment_data["page"] = 1
                segment_data["sequence"] = -1
                segments_list.append(segment_data)
                segment_data_dict = {"technique": extraction_technique,
                                     "segments": segments_list}
                segment_data_list.append(segment_data_dict)
            if extraction_technique == 'text':
                segments_list = self.get_segment_data_from_text(
                    from_files_full_path)
                segment_data_dict = {"technique": extraction_technique,
                                     "segments": segments_list}
                segment_data_list.append(segment_data_dict)
            
        combined_segments_list = []
        for segment_data in segment_data_list:
            combined_segments_list.append(segment_data["segments"])

        prefer_larger_segments = segment_gen_config_data.get(
            'prefer_larger_segments')
        merge_requirements = segment_gen_config_data.get('merge')
        segment_data_merger_obj = SegmentDataMerger(
            combined_segments_list, prefer_larger_segments)
        merged_segments_list = segment_data_merger_obj.segment_data_merge(
            merge_requirements)

        # plot bbox
        if segment_gen_config_data.get('plot_bbox_segments'):
            self.__plot_segments(merged_segments_list,
                                 out_file_full_path, "merged")

        segment_data_dict = {"technique": "merged",
                             "segments": merged_segments_list}
        segment_data_list.append(segment_data_dict)

        raw_data = infy_dpp_sdk.data.RawData(table_data=[], key_value_data=[], heading_data=[],
                                             page_header_data=[],
                                             page_footer_data=[], other_data=[],
                                             segment_data=[segment_data["segments"] for segment_data in segment_data_list if segment_data["technique"] == "merged"][0])
        document_data.raw_data = raw_data
        context_data[PROCESSEOR_CONTEXT_DATA_NAME] = {
            'segment_data': segment_data_list}
        # Populate response data
        self._processor_response_data.document_data = document_data
        self._processor_response_data.context_data = context_data

        return self._processor_response_data

    def get_plain_text(self, template_file_path, json_data_file_path) -> str:
        place_holder_dict = {}
        template_file_data = self.__file_sys_handler.read_file(
            template_file_path)
        pattern = r'\{\$\.([^}]+)\}'
        pattern_matches = re.findall(pattern, template_file_data)
        pattern_matches = list(set(pattern_matches))

        delimiter_dict = {}
        pattern_matches_list = []
        for i in pattern_matches:
            l1 = i.split(",", 1)
            pattern_matches_list.append(l1[0])
            if len(l1) > 1:
                val = l1[1].split("=")[1]
                delimiter_dict[f"$.{l1[0]}"] = val

        variable_list = [f"$.{match}" for match in pattern_matches_list]
        json_data = None
        with open(json_data_file_path, "r") as file:
            json_data = json.load(file)
        for variable in variable_list:
            jsonpath_expr = parse(variable)
            matches = jsonpath_expr.find(json_data)
            for match_data in matches:
                value = match_data.value
                # print(f'{{{variable}}}')
                if variable in delimiter_dict:
                    delimiter = delimiter_dict[variable]
                    place_holder_dict[f'{{{variable},delimiter={delimiter}}}'] = delimiter.join(
                        value)
                else:
                    place_holder_dict[f'{{{variable}}}'] = str(value)
        # print(place_holder_dict)
        for k, v in place_holder_dict.items():
            template_file_data = template_file_data.replace(k, v)
        print("...AFTER REPLACING...", template_file_data)
        return template_file_data

    def get_segment_data_from_text(self, text_file_path):
        '''getting segment data from text file'''
        segment_data_list = []
        with open(text_file_path, 'r',encoding='utf-8') as file:
            text = file.read()
            paragraphs = text.split('\n')  
            for i, paragraph in enumerate(paragraphs):
                if paragraph.strip() != '':  
                    segment_data = {}
                    segment_data["content_type"] = "paragraph"
                    segment_data["content"] = paragraph
                    segment_data["bbox_format"] = "X1,Y1,X2,Y2"
                    segment_data["content_bbox"] = []
                    segment_data["confidence_pct"] = -1
                    segment_data["page"] = 1
                    segment_data["sequence"] = -1  
                    segment_data_list.append(segment_data)
        return segment_data_list

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
                    start, end = (bbox[0], bbox[1]), (bbox[2], bbox[3])
                    cv2.rectangle(image_bbox, start, end, (0, 0, 255), 2)
                    cv2.putText(image_bbox, f"{start},{end}", (
                        start[0], start[1]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)

            cv2.imwrite(bbox_img_file_path, image_bbox)
            return bbox_img_file_path

        page_segment_list = []
        img_file_path_list = [os.path.join(out_file_full_path, file) for file in os.listdir(
            out_file_full_path) if file.endswith('.jpg')]
        for page_number in range(1, len(img_file_path_list)+1):
            group_list = __insert_list(segment_data_list, page_number)
            page_segment_list.append(group_list)
        for index, image_path in enumerate(img_file_path_list):
            __draw_bbox(image_path, page_segment_list[index])

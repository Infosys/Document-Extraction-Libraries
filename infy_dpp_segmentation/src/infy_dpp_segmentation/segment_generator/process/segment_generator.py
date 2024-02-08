# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import os
import re
import json
from jsonpath_ng import parse
import infy_dpp_sdk
from infy_dpp_sdk.data import *
from infy_dpp_segmentation.common.app_config_manager import AppConfigManager
from infy_dpp_segmentation.common.file_util import FileUtil
from infy_dpp_segmentation.common.logger_factory import LoggerFactory

from infy_dpp_segmentation.segment_generator.process.pdf_box_based_segment_generator import PdfBoxBasedSegmentGenerator
from infy_dpp_segmentation.segment_generator.process.ocr_based_segment_generator import OcrBasedSegmentGenerator
from infy_dpp_segmentation.common.file_system_manager import FileSystemManager

PROCESSEOR_CONTEXT_DATA_NAME = "segment_generator"


class SegmentGenerator(infy_dpp_sdk.interface.IProcessor):
    def __init__(self):
        self.__file_sys_handler = FileSystemManager().get_file_system_handler()
        self.__app_config = AppConfigManager().get_app_config()
        self._processor_response_data = ProcessorResponseData()
        self.__logger = LoggerFactory().get_logger()
        # self.__converter_path = os.environ["FORMAT_CONVERTER_HOME"]

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
                # ocr_based_seg_gene_obj = OcrBasedSegmentGenerator(
                #     config_data.get('SegmentGenerator', {}))
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
            # TODO: Rashmi: to be uncommented for multi technique pdfs
            # detectron_segment_data_dict = {
            #     "technique": "detectron",
            #     "segments": detectron_segment_data_list
            # }
            # pdfbox_segment_data_dict = {
            #     "technique": "detectron",
            #     "segments": pdfbox_segment_data_list
            # }
            # segment_data_list = [
            #     detectron_segment_data_dict, pdfbox_segment_data_dict]

        # if len(segment_data_list)==2:
        combined_segments_list = []
        for segment_data in segment_data_list:
            combined_segments_list.append(segment_data["segments"])
        merged_segments_list = self.merge_segment_data(combined_segments_list)
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

    def merge_segment_data(self, segments_list_of_list: list) -> list:
        try:
            if len(segments_list_of_list) == 1:
                return segments_list_of_list[0]
            segment_data_list = []
            i = 0
            j = 0
            list_one_length = len(segments_list_of_list[0])
            list_two_length = len(segments_list_of_list[1])
            count_one = 0
            count_two = 0
            counter = 0
            while (True):
                segment_data_one = segments_list_of_list[0][i]
                page_detail_one = segment_data_one['page']
                bbox_one = segment_data_one['content_bbox']
                content_one = segment_data_one['content']

                segment_data_two = segments_list_of_list[1][j]
                page_detail_two = segment_data_two['page']
                bbox_two = segment_data_two['content_bbox']
                content_two = segment_data_two['content']

                sd_last_element = len(segment_data_list) - 1

                if (count_one == 0 and count_two == 0):
                    if (page_detail_one == page_detail_two):
                        if (bbox_one[1] <= bbox_two[1] and count_one == 0):
                            if (i == (list_one_length - 1)):
                                count_one = count_one + 1
                            if (j == (list_two_length - 1)):
                                count_two = count_two + 1

                            if len(segment_data_list):
                                last_element_data = segment_data_list[sd_last_element]
                                last_element_bbox = last_element_data['content_bbox'][3]

                                if (last_element_data['page'] < page_detail_one):
                                    segment_data_list.append(segment_data_one)
                                    if (i == list_one_length - 1):
                                        count_one = count_one + 1
                                elif (last_element_bbox < bbox_one[1] and content_one != ""):
                                    if segment_data_one not in segment_data_list:
                                        segment_data_list.append(
                                            segment_data_one)
                                        if (i == list_one_length - 1):
                                            count_one = count_one + 1
                            else:
                                if (content_one != ""):
                                    segment_data_list.append(segment_data_one)

                            if (i < (list_one_length - 1)):
                                i = i + 1
                            elif (j < (list_two_length - 1)):
                                j = j + 1

                        else:
                            if (i == (list_one_length - 1)):
                                count_one = count_one + 1
                            if (j == (list_two_length - 1)):
                                count_two = count_two + 1

                            if len(segment_data_list):
                                last_element_data = segment_data_list[sd_last_element]
                                last_element_bbox = last_element_data['content_bbox'][3]

                                if (last_element_data['page'] < page_detail_two):
                                    segment_data_list.append(segment_data_two)
                                    if (j == (list_two_length - 1)):
                                        count_two = count_two + 1
                                elif (last_element_bbox < bbox_two[1] and content_two != ""):
                                    if segment_data_two not in segment_data_list:
                                        segment_data_list.append(
                                            segment_data_two)
                                        if (j == (list_two_length - 1)):
                                            count_two = count_two + 1
                            else:
                                if (content_two != ""):
                                    segment_data_list.append(segment_data_two)

                            if (j < (list_two_length - 1)):
                                j = j + 1
                            elif (i < (list_one_length - 1)):
                                i = i + 1

                    elif (page_detail_one < page_detail_two):
                        if len(segment_data_list):
                            if (content_one != ""):
                                if segment_data_one not in segment_data_list:
                                    segment_data_list.append(segment_data_one)
                        else:
                            if (content_one != ""):
                                segment_data_list.append(segment_data_one)

                        if (i < (list_one_length - 1)):
                            i = i + 1
                        elif (j < (list_two_length - 1)):
                            j = j + 1

                    else:
                        if len(segment_data_list):
                            if (content_two != ""):
                                if segment_data_two not in segment_data_list:
                                    segment_data_list.append(segment_data_two)
                        else:
                            if (content_two != ""):
                                segment_data_list.append(segment_data_two)

                        if (j < (list_two_length - 1)):
                            j = j + 1
                        elif (i < (list_one_length - 1)):
                            i = i + 1
                elif (count_one != 0):
                    if len(segment_data_list):
                        last_element_data = segment_data_list[sd_last_element]
                        last_element_bbox = last_element_data['content_bbox'][3]

                        if (last_element_data['page'] < page_detail_two):
                            segment_data_list.append(segment_data_two)
                        elif (last_element_bbox < bbox_two[1] and content_two != ""):
                            if segment_data_two not in segment_data_list:
                                segment_data_list.append(segment_data_two)
                    else:
                        if (content_two != ""):
                            segment_data_list.append(segment_data_two)

                    if (j < (list_two_length - 1)):
                        j = j + 1
                elif (count_two != 0):
                    if len(segment_data_list):
                        last_element_data = segment_data_list[sd_last_element]
                        last_element_bbox = last_element_data['content_bbox'][3]

                        if (last_element_data['page'] < page_detail_one):
                            segment_data_list.append(segment_data_one)
                        elif (last_element_bbox < bbox_one[1] and content_one != ""):
                            if segment_data_one not in segment_data_list:
                                segment_data_list.append(segment_data_one)
                    else:
                        if (content_one != ""):
                            segment_data_list.append(segment_data_one)

                    if (i < (list_one_length - 1)):
                        i = i + 1
                if (i == (list_one_length - 1) and j == (list_two_length - 1)):
                    counter = counter + 1
                    if counter > 1:
                        break
        except Exception as ex:
            self.__logger.debug(
                f'....Exception in merge_segment_data : {ex}....')
        return segment_data_list

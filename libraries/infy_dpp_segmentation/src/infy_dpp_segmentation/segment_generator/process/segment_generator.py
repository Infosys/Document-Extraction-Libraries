# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#
"""This python file is for Segment generation."""
import os
import re
import json
import cv2
from jsonpath_ng import parse
import infy_dpp_sdk
from infy_dpp_sdk.data import DocumentData, ProcessorResponseData
from infy_dpp_segmentation.common.file_util import FileUtil
from infy_dpp_segmentation.common.sorting_util import ImageSortUtil
from infy_dpp_segmentation.segment_generator.process.pdf_box_based_segment_generator import PdfBoxBasedSegmentGenerator
from infy_dpp_segmentation.segment_generator.process.ocr_based_segment_generator import OcrBasedSegmentGenerator

PROCESSOR_CONTEXT_DATA_NAME = "segment_generator"


class SegmentGenerator(infy_dpp_sdk.interface.IProcessor):
    """Segment generation processor class."""

    def __init__(self):
        self.__file_sys_handler = self.get_fs_handler()
        self.__app_config = self.get_app_config()
        self.__logger = self.get_logger()

    def do_execute(self, document_data: DocumentData, context_data: dict, config_data: dict) -> ProcessorResponseData:
        def __get_temp_file_path(work_file_path):
            local_file_path = f'{self.__app_config["CONTAINER"]["APP_DIR_TEMP_PATH"]}/{work_file_path}'
            FileUtil.create_dirs_if_absent(os.path.dirname(local_file_path))
            with self.__file_sys_handler.get_file_object(work_file_path) as input_file:
                with open(local_file_path, "wb") as output:
                    output.write(input_file.read())
            return local_file_path

        segment_data_list = []
        model_provider_dict = {}
        processor_response_data = ProcessorResponseData()
        segment_gen_config_data = config_data.get('SegmentGenerator', {})
        # For parallel pipeline
        if not segment_gen_config_data:
            for key, val in config_data.items():
                # PROCESSOR_CONTEXT_DATA_NAME = key
                segment_gen_config_data = val
                break
        # from_files_full_path = document_data.metadata.standard_data.filepath.value
        org_files_full_path = context_data['request_creator']['work_file_path']
        from_files_full_path = __get_temp_file_path(org_files_full_path)
        _, extension = os.path.splitext(from_files_full_path)
        for technique in segment_gen_config_data.get('techniques', []):
            segments_list = []
            table_data_list = []
            image_data_list = []
            if not technique.get("enabled"):
                continue
            else:
                input_file_type = technique.get("input_file_type")
                text_provider_name = technique.get("text_provider_name")
                model_provider_name = technique.get("model_provider_name")
                if text_provider_name:
                    text_provider_dict = [textProviders for textProviders in segment_gen_config_data.get(
                        "textProviders") if textProviders.get("provider_name") == text_provider_name][0]
                if model_provider_name:
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
                        elif text_provider_name == "ContentExtractor.table_contents_file_path":
                            extraction_technique = 'pdf_plumber_table_extraction'
                        elif text_provider_name == "ContentExtractor.img_yolox_infy_table_extractor_file_path":
                            extraction_technique = 'yolox_infy_table_extraction'
                        elif text_provider_name == "ContentExtractor.image_contents_file_path":
                            extraction_technique = 'pdf_box_with_OCR_image_extraction'
                        elif text_provider_name in ["tesseract_ocr_provider", "infy_ocr_engine_provider", "azure_read_ocr_provider"]:
                            extraction_technique = 'pdf_scanned_ocr_extraction'
                        elif text_provider_name == "ContentExtractor.img_docling_td_tsr_file_path":
                            extraction_technique = 'docling_table_extraction'
                        else:
                            extraction_technique = 'native_pdf'
                    elif input_file_type == 'image' and extension in ['.jpg', '.jpeg', '.png', '.tif', '.tiff']:
                        # ,'.tif','.tiff'
                        if text_provider_name == "ContentExtractor.img_yolox_infy_table_extractor_file_path":
                            extraction_technique = 'yolox_infy_table_extraction'
                        elif text_provider_name == "ContentExtractor.img_docling_td_tsr_file_path":
                            extraction_technique = 'docling_table_extraction'
                        else:
                            extraction_technique = 'ocr_based'
                    elif input_file_type == 'txt' and extension == '.txt':
                        extraction_technique = 'text'
                    else:
                        continue
                else:
                    continue
            context_data = context_data if context_data else {}
            if 'content_extractor' in context_data:
                content_extracted = context_data.get('content_extractor')
            else:
                # For separate table & (text,img)content extractor node in pipeline
                content_extracted = {}
                for processor_name, processor_val in context_data.items():
                    if processor_name.startswith('content_extractor'):
                        content_extracted[processor_name] = processor_val
            # processor_data = {
            #     "document_data": document_data.json(), "context_data": context_data}
            out_file_full_path = f'{from_files_full_path}_files'
            if extraction_technique == 'native_pdf':
                if content_extracted:
                    if content_extracted.get('content_extractor_text', {}).get('ocr_files_path_list'):
                        ocr_files_path_list = content_extracted.get('content_extractor_text').get(
                            'ocr_files_path_list')
                        pdf_box_seg_gen_obj = PdfBoxBasedSegmentGenerator(
                            text_provider_dict, self.__file_sys_handler, self.__logger, self.__app_config)
                        segments_list = pdf_box_seg_gen_obj.get_segment_data(
                            from_files_full_path, out_file_full_path, ocr_files_path_list)
                        segment_data_dict = {"technique": extraction_technique,
                                             "segments": segments_list}
                        segment_data_list.append(segment_data_dict)
            if extraction_technique == 'ocr_based':
                ocr_files_list = []
                # content_extracted = context_data.get('content_extractor')
                if content_extracted:
                    if content_extracted.get('content_extractor_image', {}).get('image_ocr').get('image_ocr_file_path'):
                        ocr_files_list = [content_extracted.get('content_extractor_image', {}).get(
                            'image_ocr').get('image_ocr_file_path')]
                    elif content_extracted.get('content_extractor_image', {}).get('tiff_image_ocr').get('tiff_image_ocr_file_path_list'):
                        ocr_files_list = content_extracted.get('content_extractor_image', {}).get(
                            'tiff_image_ocr').get('tiff_image_ocr_file_path_list')
                    ocr_based_seg_gene_obj = OcrBasedSegmentGenerator(
                        text_provider_dict, model_provider_dict, self.__file_sys_handler, self.__logger, self.__app_config)
                    segments_list = ocr_based_seg_gene_obj.get_segment_data(
                        from_files_full_path, out_file_full_path, ocr_files_list)
                    segment_data_dict = {"technique": extraction_technique,
                                         "segments": segments_list}
                    segment_data_list.append(segment_data_dict)
            if extraction_technique == 'json':
                # Emailworkbench
                flattened_text = self.__get_plain_text(
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
                segments_list = self.__get_segment_data_from_text(
                    from_files_full_path)
                segment_data_dict = {"technique": extraction_technique,
                                     "segments": segments_list}
                segment_data_list.append(segment_data_dict)
            if extraction_technique == 'pdf_plumber_table_extraction':
                # content_extracted = context_data.get('content_extractor')
                if content_extracted:
                    if content_extracted.get('content_extractor_table', {}).get('table_contents_file_path'):
                        table_content_path = content_extracted.get('content_extractor_table').get(
                            'table_contents_file_path')
                        table_data_list = self.__get_table_content(
                            text_provider_dict, table_content_path, from_files_full_path)
                extraction_technique = 'pdf_plumber_table_extraction'
                table_data_dict = {"technique": extraction_technique,
                                   "segments": table_data_list}
                segment_data_list.append(table_data_dict)
            if extraction_technique == 'yolox_infy_table_extraction':
                # content_extracted = context_data.get('content_extractor')
                if content_extracted:
                    if content_extracted.get('content_extractor_table', {}).get('img_yolox_infy_table_extractor_file_path'):
                        table_content_path = content_extracted.get('content_extractor_table', {}).get(
                            'img_yolox_infy_table_extractor_file_path')
                        table_data_list = self.__get_table_content(
                            text_provider_dict, table_content_path, from_files_full_path)
                extraction_technique = 'yolox_infy_table_extraction'
                table_data_dict = {"technique": extraction_technique,
                                   "segments": table_data_list}
                segment_data_list.append(table_data_dict)
            if extraction_technique == 'docling_table_extraction':
                if content_extracted:
                    if content_extracted.get('content_extractor_table', {}).get('img_docling_td_tsr_file_path'):
                        table_content_path = content_extracted.get('content_extractor_table', {}).get(
                            'img_docling_td_tsr_file_path')
                        table_data_list = self.__get_table_content(
                            text_provider_dict, table_content_path, from_files_full_path)
                extraction_technique = 'docling_table_extraction'
                table_data_dict = {"technique": extraction_technique,
                                   "segments": table_data_list}
                segment_data_list.append(table_data_dict)
            if extraction_technique == 'pdf_box_with_OCR_image_extraction':
                # content_extracted = context_data.get('content_extractor')
                if content_extracted:
                    if content_extracted.get('content_extractor_image', {}).get('image_contents_file_path'):
                        image_content_path = content_extracted.get('content_extractor_image', {}).get(
                            'image_contents_file_path')
                        image_data_list = self.__get_image_content(
                            image_content_path, from_files_full_path)
                extraction_technique = 'pdf_box_with_OCR_image_extraction'
                image_data_dict = {"technique": extraction_technique,
                                   "segments": image_data_list}
                segment_data_list.append(image_data_dict)
            if extraction_technique == 'pdf_scanned_ocr_extraction':
                # content_extracted = context_data.get('content_extractor')
                if content_extracted:
                    if content_extracted.get('content_extractor_text', {}).get('pdf_scanned_ocr_path_list'):
                        pdf_scanned_ocr_path_list = content_extracted.get('content_extractor_text', {}).get(
                            'pdf_scanned_ocr_path_list')
                        ocr_based_seg_gene_obj = OcrBasedSegmentGenerator(
                            text_provider_dict, model_provider_dict, self.__file_sys_handler, self.__logger, self.__app_config)
                        segments_list = ocr_based_seg_gene_obj.get_segment_data(
                            from_files_full_path, out_file_full_path, pdf_scanned_ocr_path_list)
                        segment_data_dict = {"technique": extraction_technique,
                                             "segments": segments_list}
                        segment_data_list.append(segment_data_dict)

            # ToDo: R: to be uncommented for multi technique pdfs
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

            debug_config = segment_gen_config_data.get('debug')
            if debug_config.get('enabled'):
                if debug_config.get('generate_image'):
                    self.__plot_bbox(
                        segment_data_list, org_files_full_path, debug_config, extraction_technique)

        raw_data = infy_dpp_sdk.data.RawData(table_data=[], key_value_data=[], heading_data=[],
                                             page_header_data=[],
                                             page_footer_data=[], other_data=[],
                                             segment_data=[segment_data["segments"] if
                                                           len(segment_data_list) == 1 else []
                                                           for segment_data in segment_data_list]
                                             [0] if segment_data_list else None)
        document_data.raw_data = raw_data
        if 'SegmentGenerator' in config_data:
            context_data[PROCESSOR_CONTEXT_DATA_NAME] = {
                'segment_data': segment_data_list}
        else:
            # For parallel pipeline
            context_data[PROCESSOR_CONTEXT_DATA_NAME+'_'+segment_data_list[0].get('technique')] = {
                'segment_data': segment_data_list}

        processor_response_data.document_data = document_data
        processor_response_data.context_data = context_data

        return processor_response_data

    def __get_plain_text(self, template_file_path, json_data_file_path) -> str:
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
        with open(json_data_file_path, "r", encoding='utf-8') as file:
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

    def __get_segment_data_from_text(self, text_file_path):
        '''getting segment data from text file'''
        segment_data_list = []
        with open(text_file_path, 'r', encoding='utf-8') as file:
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

    def __plot_bbox(self, segment_data_list, org_files_full_path, debug_config, extraction_technique):
        def __get_storage_file_path(org_files_full_path):
            org_files_full_path = f'{org_files_full_path}_files'
            self.__file_sys_handler.create_folders(org_files_full_path)
            return org_files_full_path

        def __insert_list(segment_data_list: list, page_number: int):
            page_list = []
            for item in segment_data_list[0]['segments']:
                if item['page'] == page_number:
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
                group_list = __insert_list(segment_data_list, page_number)
                page_segment_list.append(group_list)
            for index, image_path in enumerate(img_file_path_list):
                __draw_bbox(debug_file_path,
                            image_path, page_segment_list[index], output_dir, extraction_technique)

    def __rescale_content_bbox(self, bbox, page_number, page_width, page_height, storage_dir_path):
        page_content_path = f'{storage_dir_path}/{page_number}.jpg_pdfbox.json'
        if not self.__file_sys_handler.exists(page_content_path):
            return bbox
        page_content = json.loads(
            self.__file_sys_handler.read_file(page_content_path))
        # page_content_path = f'{from_files_full_path}_files/{page_number}.jpg_pdfbox.json'
        # page_content = FileUtil.load_json(page_content_path)
        image_width = page_content['width']
        image_height = page_content['height']

        width_ratio = image_width / page_width
        height_ratio = image_height / page_height

        rescaled_bbox = [bbox[0] * width_ratio, bbox[1] * height_ratio,
                         bbox[2] * width_ratio, bbox[3] * height_ratio]

        return rescaled_bbox

    def __get_image_content(self, image_content_path, from_files_full_path):
        image_content = json.loads(
            self.__file_sys_handler.read_file(image_content_path))
        images_list = []
        storage_dir_path = os.path.dirname(image_content_path)
        for page in image_content:
            for image in page['tokens']:
                if image:
                    bbox = self.__rescale_content_bbox(
                        image['bbox'], page['page'], page['width'], page['height'],
                        storage_dir_path)

                    image_data = {}
                    image_data["content_type"] = "image_text"
                    image_data["content"] = image['text']
                    image_data["bbox_format"] = "X1,Y1,X2,Y2"
                    image_data["content_bbox"] = bbox
                    image_data["confidence_pct"] = -1
                    image_data["page"] = page['page']
                    image_data["sequence"] = -1
                    images_list.append(image_data)

        return images_list

    def __get_table_content(self, text_provider_dict, table_content_path, from_files_full_path):
        extract_hyperlink = text_provider_dict.get(
            'properties').get('extract_hyperlink', False)
        table_content = json.loads(
            self.__file_sys_handler.read_file(table_content_path))
        tables_list = []
        storage_dir_path = os.path.dirname(table_content_path)
        for page in table_content:
            for table in page['tables']:
                if table:
                    bbox = self.__rescale_content_bbox(
                        table['bbox'], page['page_number'], page['page_width'], page['page_height'],
                        storage_dir_path)

                    table_data = {}
                    table_data["content_type"] = "table"
                    if extract_hyperlink:
                        table_data["content"] = json.dumps(table['data_html'])
                    else:
                        table_data["content"] = json.dumps(table['data'])
                    table_data["bbox_format"] = "X1,Y1,X2,Y2"
                    table_data["content_bbox"] = bbox
                    table_data["confidence_pct"] = -1
                    table_data["page"] = page['page_number']
                    table_data["sequence"] = -1
                    tables_list.append(table_data)

        return tables_list

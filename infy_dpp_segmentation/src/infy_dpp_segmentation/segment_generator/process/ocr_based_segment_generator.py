# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                   #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import os
import time


from infy_ocr_parser import ocr_parser
from infy_ocr_parser.providers.tesseract_ocr_data_service_provider \
    import TesseractOcrDataServiceProvider as tesseract_parser
from infy_ocr_generator import ocr_generator
from infy_ocr_generator.providers.infy_ocr_engine_data_service_provider \
    import InfyOcrEngineDataServiceProvider
from infy_ocr_generator.providers.tesseract_ocr_data_service_provider \
    import TesseractOcrDataServiceProvider
from infy_ocr_parser.providers.azure_read_ocr_data_service_provider \
    import AzureReadOcrDataServiceProvider as azure_read_parser
from infy_ocr_parser.providers.apache_pdfbox_data_service_provider \
    import ApachePdfboxDataServiceProvider as pdf_box_parser
from infy_ocr_generator.providers.azure_read_ocr_data_service_provider \
    import AzureReadOcrDataServiceProvider
from infy_ocr_generator.providers.apache_pdfbox_data_service_provider \
    import ApachePdfboxDataServiceProvider

# from infy_dpp_segmentation.segment_generator.service.segment_generator_service import SegmentGeneratorService
from infy_dpp_segmentation.common.app_constant import OcrType
import infy_dpp_sdk
import infy_fs_utils


class OcrBasedSegmentGenerator:
    """Ocr based segment generator class
    """

    def __init__(self, text_provider_dict: dict, model_provider_dict: dict) -> None:
        self.__logger = infy_fs_utils.manager.FileSystemLoggingManager(
        ).get_fs_logging_handler(infy_dpp_sdk.common.Constants.FSLH_DPP).get_logger()
        self.__app_config = infy_dpp_sdk.common.AppConfigManager().get_app_config()
        self.__file_sys_handler = infy_fs_utils.manager.FileSystemManager(
        ).get_fs_handler(infy_dpp_sdk.common.Constants.FSH_DPP)

        self.__model_provider_dict = model_provider_dict
        self.__text_provider_dict = text_provider_dict
        self.__converter_path = self.__text_provider_dict.get(
            'properties').get('format_converter_home', '')
        if self.__converter_path == '':
            raise Exception(
                'Format converter path is not configured in the config file')
        self.__pytesseract_path = self.__text_provider_dict.get(
            'properties').get('tesseract_path', '')
        self.__ocr_engine_exe_dir_path = self.__text_provider_dict.get(
            'properties').get('ocr_engine_exe_dir_path', '')
        self.__ocr_engine_model_dir_path = self.__text_provider_dict.get(
            'properties').get('ocr_engine_model_dir_path', '')
        self.__ocr_engine_language = self.__text_provider_dict.get(
            'properties').get('ocr_engine_language', '')
        self._org_file_path = None

    def get_segment_data(self, from_files_full_path, out_file_full_path, ocr_files_list):

        segment_data_list = []
        # # api get box
        # if self.__model_provider_dict:
        #     self.__logger.info('...Segment generation started...')
        #     sg_ser_obj = SegmentGeneratorService(
        #         self.__model_provider_dict.get('properties'))
        #     segment_data_list = sg_ser_obj.get_segment_data(images_path_list)
        # else:
        #     segment_data_list = []

        ocr_files_path_list = []
        self.__logger.info('...OCR parsing started...')
        for ocr_file in ocr_files_list:
            ocr_file_full_path = self.__file_sys_handler.get_bucket_name() + ocr_file
            ocr_files_path_list.append(ocr_file_full_path)
        combined_segment_data_list = self.get_content_from_bbox(
            ocr_files_path_list, segment_data_list)

        return combined_segment_data_list

    def get_content_from_bbox(self, ocr_file_list, segment_data_list):
        '''get content from bbox using ocr parser'''
        updated_segment_data_list = []
        token_type_value = 3
        # ocr_tool = self.__config_data.get('ocr_tool')
        if self.__text_provider_dict.get('provider_name').startswith(OcrType.TESSERACT):
            ocr_parser_data_service_provider = tesseract_parser()
        if self.__text_provider_dict.get('provider_name').startswith(OcrType.INFY_OCR_ENGINE):
            ocr_parser_data_service_provider = tesseract_parser()
        if self.__text_provider_dict.get('provider_name').startswith(OcrType.AZURE_READ):
            ocr_parser_data_service_provider = azure_read_parser()
        if self.__text_provider_dict.get('provider_name').startswith(OcrType.PDF_BOX):
            ocr_parser_data_service_provider = pdf_box_parser()
            token_type_value = 2
        for ocr_file in ocr_file_list:
            if self.__text_provider_dict.get('provider_name').startswith(OcrType.TESSERACT):
                page_no = os.path.basename(ocr_file).replace('.jpg.hocr', '')
            if self.__text_provider_dict.get('provider_name').startswith(OcrType.INFY_OCR_ENGINE):
                page_no = os.path.basename(ocr_file).replace('.jpg.hocr', '')
            if self.__text_provider_dict.get('provider_name').startswith(OcrType.AZURE_READ):
                page_no = os.path.basename(ocr_file).replace(
                    '.jpg_azure_read.json', '')
            if self.__text_provider_dict.get('provider_name').startswith(OcrType.PDF_BOX):
                page_no = os.path.basename(
                    ocr_file).replace('.jpg_pdfbox.json', '')
            ocr_obj = ocr_parser.OcrParser([ocr_file],
                                           data_service_provider=ocr_parser_data_service_provider,
                                           config_params_dict={
                'match_method': 'regex', 'similarity_score': 1})
            if self.__model_provider_dict:
                for single_segment_data in segment_data_list:
                    if single_segment_data.get('page_no') == page_no:
                        for segment_data in single_segment_data.get('output'):
                            segment_data["bbox_format"] = "X1,Y1,X2,Y2"
                            content_bbox = segment_data.get('content_bbox')
                            within_bbox = [content_bbox[0], content_bbox[1],
                                           content_bbox[2]-content_bbox[0],
                                           content_bbox[3]-content_bbox[1]]
                            phrases_dict_list = ocr_obj.get_tokens_from_ocr(
                                token_type_value=token_type_value, within_bbox=within_bbox,
                                pages=[int(page_no)], scaling_factor={'hor': 1, 'ver': 1})
                        # TODO:line separtaer will be added.
                            segment_data['content'] = ' '.join([phrase_dict.get('text')
                                                                for phrase_dict in phrases_dict_list])
                            if segment_data['content'].strip() != '':
                                updated_segment_data_list.append(segment_data)
            else:
                lines_dict_list = ocr_obj.get_tokens_from_ocr(
                    token_type_value=token_type_value)
                for token in lines_dict_list:
                    if token["text"].strip() != '':
                        segment_data = {}
                        segment_data["content_type"] = "line"
                        segment_data["content"] = token["text"]
                        segment_data["bbox_format"] = "X1,Y1,X2,Y2"
                        segment_data["content_bbox"] = [token["bbox"][0], token["bbox"][1],
                                                        token["bbox"][0] +
                                                        token["bbox"][2],
                                                        token["bbox"][1]+token["bbox"][3]]
                        segment_data["confidence_pct"] = -1
                        segment_data["page"] = int(page_no)
                        segment_data["sequence"] = -1
                        updated_segment_data_list.append(segment_data)

        return updated_segment_data_list

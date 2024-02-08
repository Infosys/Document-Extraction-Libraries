# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import os
import time

from infy_ocr_parser import ocr_parser
from infy_ocr_parser.providers.tesseract_ocr_data_service_provider \
    import TesseractOcrDataServiceProvider as tesseract_parser
from infy_ocr_generator import ocr_generator
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

from infy_dpp_segmentation.segment_generator.service.image_generator_service import ImageGeneratorService
from infy_dpp_segmentation.segment_generator.service.segment_generator_service import SegmentGeneratorService
from infy_dpp_segmentation.common.app_constant import OcrType
from infy_dpp_segmentation.common.file_system_manager import FileSystemManager
from infy_dpp_segmentation.common.app_config_manager import AppConfigManager
from infy_dpp_segmentation.common.logger_factory import LoggerFactory


class OcrBasedSegmentGenerator:
    """Ocr based segment generator class
    """

    def __init__(self, text_provider_dict: dict, model_provider_dict: dict) -> None:
        self.__logger = LoggerFactory().get_logger()
        self.__app_config = AppConfigManager().get_app_config()
        self.__file_sys_handler = FileSystemManager().get_file_system_handler()

        # self.__config_data = config_data.get('ocr_based', {})
        self.__model_provider_dict = model_provider_dict
        self.__text_provider_dict = text_provider_dict
        self.__converter_path = self.__text_provider_dict.get(
            'properties').get('format_converter_home', '')
        # if self.__converter_path == '':
        #     raise Exception(
        #         'Format converter path is not configured in the config file')
        self.__pytesseract_path = self.__text_provider_dict.get(
            'properties').get('tesseract_path', '')
        self._org_file_path = None

    def get_segment_data(self, from_files_full_path, out_file_full_path):
        """getting segment data"""
        self._org_file_path = from_files_full_path
        self.__doc_extension = os.path.splitext(
            self._org_file_path)[1].lower()
        if self.__doc_extension == '.pdf':
            raise NotImplementedError(
                'PDF file processing is not supported in this version')
        # pdf to image
        config_data_dict = {
            "format_converter": {
                "pages": [
                ],
                "to_dir": os.path.abspath(out_file_full_path),
                "dpi": 300
            },
            "format_converter_home": self.__converter_path
        }

        image_generator_service_obj = ImageGeneratorService()
        if self.__doc_extension == '.pdf':
            self.__logger.info('...PDF to JPG conversion started...')
            # images_path_list, _ = image_generator_service_obj.convert_pdf_to_image(
            #     os.path.abspath(self._org_file_path), config_data_dict)
        elif self.__doc_extension in ['.jpg', '.png', '.jpeg']:
            self.__logger.info('...IMG to JPG conversion started...')
            images_path_list, _ = image_generator_service_obj.convert_img_to_jpg(
                os.path.abspath(self._org_file_path), config_data_dict)
        else:
            self.__logger.error(
                f'{self.__doc_extension} is not supported in OCR Segment generation')
            raise Exception(
                f'{self.__doc_extension} is not supported in OCR Segment generation')
        # ocr generator
        self.__logger.info('...OCR generation started...')
        ocr_files_path_list = self.generate_ocr(
            images_path_list, out_file_full_path)
        # api get box
        if self.__model_provider_dict:
            self.__logger.info('...Segment generation started...')
            sg_ser_obj = SegmentGeneratorService(
                self.__model_provider_dict.get('properties'))
            segment_data_list = sg_ser_obj.get_segment_data(images_path_list)
        else:
            segment_data_list = []
        # ocr parser  = object
        self.__logger.info('...OCR parsing started...')
        combined_segment_data_list = self.get_content_from_bbox(
            ocr_files_path_list, segment_data_list)
        return combined_segment_data_list

    def generate_ocr(self, image_path_list, out_file_full_path):
        '''generate ocr'''
        ocr_path_list = []
        # provider_setting = self.__config_data.get('ocr_provider_settings')
        # ocr_tool = self.__config_data.get('ocr_tool')
        ocr_data_gen_obj, ocr_data_ser_provider = self.__init_data_service_provider_objects(
            self.__text_provider_dict, out_file_full_path)
        if self.__text_provider_dict.get('provider_name').startswith(OcrType.TESSERACT):
            to_be_ocr_gen_img_list, generated_ocr_file_list = self._check_existing_ocr_files(
                image_path_list, '.hocr')
            if len(to_be_ocr_gen_img_list) > 0:
                doc_data_list = [
                    {
                        "doc_path": doc_file_path,
                        "pages": os.path.basename(doc_file_path).replace('.jpg', '')
                    } for index, doc_file_path in enumerate(to_be_ocr_gen_img_list)
                ]
                ocr_result_list = ocr_data_gen_obj.generate(
                    doc_data_list=doc_data_list)
                ocr_path_list = [ocr_result.get(
                    'output_doc') for ocr_result in ocr_result_list]
        if self.__text_provider_dict.get('provider_name').startswith(OcrType.AZURE_READ):
            to_be_ocr_gen_img_list, generated_ocr_file_list = self._check_existing_ocr_files(
                image_path_list, '_azure_read.json')
            self.__logger.info(
                f"Already generated azure read ocr files: {generated_ocr_file_list}")
            self.__logger.info(
                f"Azure Read Ocr to be generated for : {to_be_ocr_gen_img_list}")
            if len(to_be_ocr_gen_img_list) > 0:
                doc_data_list = [
                    {
                        "doc_path": doc_file_path,
                        "pages": os.path.basename(doc_file_path).replace('.jpg', '')
                    } for index, doc_file_path in enumerate(to_be_ocr_gen_img_list)
                ]
                submit_req_result = ocr_data_gen_obj.submit_request(
                    doc_data_list=doc_data_list
                )
                time.sleep(7)
                re_res_result = ocr_data_gen_obj.receive_response(
                    submit_req_result)
                ocr_result_list = ocr_data_gen_obj.generate(
                    api_response_list=re_res_result)
                ocr_path_list = [ocr_result.get('output_doc').replace('\\', '/').replace('//', '/')
                                 for ocr_result in ocr_result_list]
        if self.__text_provider_dict.get('provider_name').startswith(OcrType.PDF_BOX):
            to_be_ocr_gen_img_list, generated_ocr_file_list = self._check_existing_ocr_files(
                image_path_list, '_pdfbox.json')
            doc_data_list = [
                {
                    "doc_path": os.path.abspath(self._org_file_path)
                }
            ]
            ocr_result_list = ocr_data_gen_obj.generate(
                doc_data_list=doc_data_list)
            raw_ocr_file_path = [ocr_result.get(
                'output_doc') for ocr_result in ocr_result_list][0]
            if len(to_be_ocr_gen_img_list) > 0:
                rescale_data_list = [{
                    'doc_page_num': os.path.basename(x).split('.', 1)[0],
                    'doc_page_width': 0,
                    'doc_page_height': 0,
                    'doc_file_path': os.path.abspath(x),
                    'doc_file_extension': 'jpg'
                } for x in to_be_ocr_gen_img_list]
                page_ocr_list = ocr_data_ser_provider.rescale_dimension(
                    raw_ocr_file_path, rescale_data_list)
                ocr_path_list = [ocr_result.get('output_doc').replace('\\', '/').replace('//', '/')
                                 for ocr_result in page_ocr_list]
        ocr_path_list.extend(generated_ocr_file_list)
        # upload the ocr files to the work location
        server_file_dir = os.path.dirname(ocr_path_list[0].replace('\\', '/').replace('//', '/').replace(
            self.__app_config["CONTAINER"]["APP_DIR_TEMP_PATH"].replace('\\', '/').replace('//', '/'), ''))
        local_dir = os.path.dirname(ocr_path_list[0])
        self._upload_data(f'{local_dir}', f'{server_file_dir}')
        # FileUtil.empty_dir(local_dir)
        return ocr_path_list

    def _check_existing_ocr_files(self, image_path_list, ocr_file_name):
        azure_read_ocr_file_tup_list = [(f'{x}{ocr_file_name}', os.path.exists(
            f'{x}{ocr_file_name}')) for x in image_path_list]
        to_be_ocr_gen_img_list = [x[0].replace(ocr_file_name, '').replace(
            '\\', '/').replace('//', '/')
            for x in azure_read_ocr_file_tup_list if not x[1]]
        generated_ocr_file_list = [x[0].replace('\\', '/').replace('//', '/')
                                   for x in azure_read_ocr_file_tup_list if x[1]]
        return to_be_ocr_gen_img_list, generated_ocr_file_list

    def _upload_data(self, local_file_path, server_file_path):
        try:
            # TODO: uploading is not working in local
            self.__file_sys_handler.put_folder(
                local_file_path, os.path.dirname(server_file_path))
            self.__logger.info(
                f'Folder {local_file_path} uploaded successfully')
        except Exception as e:
            self.__logger.error(
                f'Error while uploading data to {server_file_path} : {e}')
            raise e

    def get_content_from_bbox(self, ocr_file_list, segment_data_list):
        '''get content from bbox using ocr parser'''
        updated_segment_data_list = []
        token_type_value = 3
        # ocr_tool = self.__config_data.get('ocr_tool')
        if self.__text_provider_dict.get('provider_name').startswith(OcrType.TESSERACT):
            ocr_parser_data_service_provider = tesseract_parser()
        if self.__text_provider_dict.get('provider_name').startswith(OcrType.AZURE_READ):
            ocr_parser_data_service_provider = azure_read_parser()
        if self.__text_provider_dict.get('provider_name').startswith(OcrType.PDF_BOX):
            ocr_parser_data_service_provider = pdf_box_parser()
            token_type_value = 2
        for ocr_file in ocr_file_list:
            if self.__text_provider_dict.get('provider_name').startswith(OcrType.TESSERACT):
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

    def __init_data_service_provider_objects(self, provider_settings, out_file_full_path):
        def _format_azure_config_param(config_params_dict, provider_key):
            # temp_dict = config_params_dict[f"azure_{provider_key}"]
            temp_dict = config_params_dict.get("properties")
            # if provider_settings.get("provider_name").startswith(f"azure_{provider_key}")
            new_dict = {}
            new_dict['computer_vision'] = {
                'subscription_key': temp_dict.get('subscription_key'),
                f'api_{provider_key}': temp_dict
            }
            return {"azure": new_dict}

        ocr_gen_obj = None
        if self.__text_provider_dict.get('provider_name').startswith(OcrType.TESSERACT):
            data_service_provider = TesseractOcrDataServiceProvider(
                config_params_dict={'tesseract': {
                    'pytesseract_path': self.__pytesseract_path}},
                logger=self.__logger,
                output_dir=out_file_full_path)
            ocr_gen_obj = ocr_generator.OcrGenerator(
                data_service_provider=data_service_provider
            )
        if self.__text_provider_dict.get('provider_name').startswith(OcrType.AZURE_READ):
            data_service_provider = AzureReadOcrDataServiceProvider(
                config_params_dict=_format_azure_config_param(
                    provider_settings, 'read'), logger=self.__logger,
                output_dir=out_file_full_path)
            ocr_gen_obj = ocr_generator.OcrGenerator(
                data_service_provider=data_service_provider
            )
        if self.__text_provider_dict.get('provider_name').startswith(OcrType.PDF_BOX):
            data_service_provider = ApachePdfboxDataServiceProvider(
                config_params_dict={
                    "format_converter": {
                        "format_converter_path": self.__converter_path
                    }
                }, logger=self.__logger, output_dir=out_file_full_path)
            ocr_gen_obj = ocr_generator.OcrGenerator(
                data_service_provider=data_service_provider
            )
        return ocr_gen_obj, data_service_provider

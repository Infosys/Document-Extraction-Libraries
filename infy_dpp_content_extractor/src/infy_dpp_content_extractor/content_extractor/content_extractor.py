# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#
import os
import infy_dpp_sdk
from infy_dpp_sdk.data import DocumentData, ProcessorResponseData

from infy_dpp_content_extractor.content_extractor.process.pdf_plumber_table_extractor import PdfPlumberTableExtractor
from infy_dpp_content_extractor.content_extractor.process.pdf_box_images_extractor import PdfBoxImagesExtractor
from infy_dpp_content_extractor.content_extractor.process.pdf_to_images_converter import PdfToImagesConverter
from infy_dpp_content_extractor.content_extractor.process.pdf_box_based_ocr_generator import PdfBoxBasedOcrGenerator
from infy_dpp_content_extractor.content_extractor.process.images_text_extractor import ImagesTextExtractor
from infy_dpp_content_extractor.common.file_util import FileUtil

PROCESSEOR_CONTEXT_DATA_NAME = "content_extractor"


class ContentExtractor(infy_dpp_sdk.interface.IProcessor):
    def __init__(self):
        self.__file_sys_handler = self.get_fs_handler()
        self.__app_config = infy_dpp_sdk.common.AppConfigManager().get_app_config()
        self.__logger = self.get_logger()

    def do_execute(self, document_data: DocumentData, context_data: dict, config_data: dict) -> ProcessorResponseData:
        def __get_temp_file_path(work_file_path):
            local_file_path = f'{self.__app_config["CONTAINER"]["APP_DIR_TEMP_PATH"]}/{work_file_path}'
            FileUtil.create_dirs_if_absent(os.path.dirname(local_file_path))
            with self.__file_sys_handler.get_file_object(work_file_path) as f:
                with open(local_file_path, "wb") as output:
                    output.write(f.read())
            return local_file_path

        self.__logger.debug('Content Extraction Started')
        table_content_file_path = ""
        images_content_file_path = ""
        ocr_file_path = ""
        image_file_path = ""
        pdf_apache_pdfbox_ocr_file_path = ""
        pdf_to_images_files_path_list = []
        ocr_files_path_list = []
        processor_response_data = ProcessorResponseData()
        content_extractor_config_data = config_data.get('ContentExtractor', {})
        org_files_full_path = context_data['request_creator']['work_file_path']
        from_files_full_path = __get_temp_file_path(org_files_full_path)
        _, extension = os.path.splitext(from_files_full_path)
        context_data[PROCESSEOR_CONTEXT_DATA_NAME] = {}
        for technique in content_extractor_config_data.get('techniques', []):
            if not technique.get("enabled"):
                continue
            else:
                input_file_type = technique.get("input_file_type")
                text_provider_name = technique.get("text_provider_name")
                technique_name = technique.get("name")
                if text_provider_name:
                    text_provider_dict = [textProviders for textProviders in content_extractor_config_data.get(
                        "textProviders") if textProviders.get("provider_name") == text_provider_name][0]

                if input_file_type == 'pdf' and extension == '.pdf':
                    out_file_full_path = f'{from_files_full_path}_files'
                    if not os.path.exists(out_file_full_path):
                        os.makedirs(out_file_full_path)
                    if technique_name == "pdf_image_converter":
                        pdf_to_images_converter_obj = PdfToImagesConverter(
                            text_provider_dict)
                        pdf_to_images_files_path_list = pdf_to_images_converter_obj.get_images_path_list(
                            from_files_full_path, out_file_full_path)
                    context_data[PROCESSEOR_CONTEXT_DATA_NAME]["pdf_to_images_files_path_list"] = pdf_to_images_files_path_list

                    if technique_name == "pdf_apache_pdfbox":
                        pdf_box_based_ocr_generator_obj = PdfBoxBasedOcrGenerator(
                            text_provider_dict)
                        pdf_apache_pdfbox_ocr_file_path = pdf_box_based_ocr_generator_obj.generate_ocr_json_for_pdf(
                            from_files_full_path, out_file_full_path)
                    context_data[PROCESSEOR_CONTEXT_DATA_NAME]["pdf_apache_pdfbox_ocr_file_path"] = pdf_apache_pdfbox_ocr_file_path

                    if technique_name == "pdf_image_apache_pdfbox":
                        # pdf_image_apache_pdfbox is dependent on pdf_image_converter and pdf_apache_pdfbox

                        # pdf_to_images_converter_obj = PdfToImagesConverter(
                        #     text_provider_dict)
                        # pdf_to_images_files_path_list = pdf_to_images_converter_obj.get_images_path_list(
                        #     from_files_full_path, out_file_full_path)
                        pdf_to_images_files_path_list = context_data[
                            PROCESSEOR_CONTEXT_DATA_NAME]["pdf_to_images_files_path_list"]
                        pdf_apache_pdfbox_ocr_file_path = context_data[
                            PROCESSEOR_CONTEXT_DATA_NAME]["pdf_apache_pdfbox_ocr_file_path"]
                        pdf_box_based_ocr_generator_obj = PdfBoxBasedOcrGenerator(
                            text_provider_dict)
                        ocr_files_path_list = pdf_box_based_ocr_generator_obj.generate_ocr(
                            pdf_to_images_files_path_list, from_files_full_path, out_file_full_path, pdf_apache_pdfbox_ocr_file_path)
                    context_data[PROCESSEOR_CONTEXT_DATA_NAME]["ocr_files_path_list"] = ocr_files_path_list

                    if technique_name == "pdf_plumber_table_extractor":
                        pdf_plumber_table_extractor_obj = PdfPlumberTableExtractor()
                        table_content_file_path = pdf_plumber_table_extractor_obj.get_tables_content(
                            from_files_full_path, out_file_full_path)
                        if table_content_file_path:
                            self.__logger.debug("Table/s detected in PDF file")
                    context_data[PROCESSEOR_CONTEXT_DATA_NAME]['table_contents_file_path'] = table_content_file_path

                    if technique_name == "pdf_box_image_extractor":
                        pdf_box_images_extractor_obj = PdfBoxImagesExtractor(
                            text_provider_dict)
                        images_content_file_path = pdf_box_images_extractor_obj.get_images_content(
                            from_files_full_path, out_file_full_path)

                        if images_content_file_path:
                            self.__logger.debug("Image/s detected in PDF file")
                            technique_dict = [techniques for techniques in content_extractor_config_data.get(
                                "techniques")
                                if techniques.get("input_file_type") == "image"
                                and techniques.get("enabled") == True][0]
                            text_provider_name = technique_dict.get(
                                "text_provider_name")
                            if text_provider_name:
                                text_provider_dict = [textProviders for textProviders in content_extractor_config_data.get(
                                    "textProviders") if textProviders.get("provider_name") == text_provider_name][0]

                            images_text_extractor_obj = ImagesTextExtractor(
                                text_provider_dict)
                            images_text_extractor_obj.get_images_text(
                                from_files_full_path, out_file_full_path)
                    context_data[PROCESSEOR_CONTEXT_DATA_NAME]['image_contents_file_path'] = images_content_file_path

                elif input_file_type == 'image' and extension in ['.jpg', '.jpeg', '.png']:
                    out_file_full_path = f'{from_files_full_path}_files'
                    if not os.path.exists(out_file_full_path):
                        os.makedirs(out_file_full_path)
                    # if technique_name in ['img_infy_ocr_engine_extractor','img_tesseracct_ocr_extractor','img_azure_read_ocr_extractor']
                    image_to_ocr_extractor_obj = ImagesTextExtractor(
                        text_provider_dict)
                    ocr_file_path, image_file_path = image_to_ocr_extractor_obj.get_ocr_from_images(
                        from_files_full_path, out_file_full_path)
                context_data[PROCESSEOR_CONTEXT_DATA_NAME]['image_ocr'] = {
                    'image_ocr_file_path': ocr_file_path,
                    'image_file_path': image_file_path
                }

        # context_data[PROCESSEOR_CONTEXT_DATA_NAME] = {
        #     # 'table_contents_file_path': table_content_file_path,
        #     # 'image_contents_file_path': images_content_file_path,
        #     # 'image_ocr': {
        #     #     'image_ocr_file_path': ocr_file_path,
        #     #     'image_file_path': image_file_path
        #     # },
        #     # 'pdf_to_images_files_path_list': pdf_to_images_files_path_list,
        #     'ocr_files_path_list': ocr_files_path_list,
        #     # 'pdf_apache_pdfbox_ocr_file_path': pdf_apache_pdfbox_ocr_file_path
        # }
        # Populate response data
        processor_response_data.document_data = document_data
        processor_response_data.context_data = context_data

        self.__logger.debug('Content Extraction Completed')
        return processor_response_data

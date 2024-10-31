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
from infy_dpp_content_extractor.content_extractor.process.yolox_table_extractor import YoloxTableExtactor
from infy_dpp_content_extractor.content_extractor.process.pdf_scanned_ocr_extractor import PdfScannedOcrExtractor

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
        yolox_tables_content_file_path = ""
        images_content_file_path = ""
        ocr_file_path = ""
        image_file_path = ""
        ocr_file_path_list = []
        image_file_path_list = []
        pdf_apache_pdfbox_ocr_file_path = ""
        pdf_to_images_files_path_list = []
        ocr_files_path_list = []
        yolox_file_path_list = []
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
                model_provider_name = technique.get("model_provider_name")
                table_debug = technique.get("debug")
                technique_name = technique.get("name")
                if text_provider_name:
                    text_provider_dict = [textProviders for textProviders in content_extractor_config_data.get(
                        "textProviders") if textProviders.get("provider_name") == text_provider_name][0]

                if model_provider_name:
                    model_provider_dict = [modelProviders for modelProviders in content_extractor_config_data.get(
                        "modelProviders") if modelProviders.get("provider_name") == model_provider_name][0]

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

                    if technique_name == "img_yolox_infy_table_extractor":
                        yolox_table_extactor_obj = YoloxTableExtactor(
                            model_provider_dict, text_provider_dict, technique.get("line_detection_method"))
                        images_file_path_list = context_data[
                            PROCESSEOR_CONTEXT_DATA_NAME]["pdf_to_images_files_path_list"]
                        yolox_tables_content_file_path, yolox_file_path_list = yolox_table_extactor_obj.get_tables_content(
                            images_file_path_list, from_files_full_path, out_file_full_path, table_debug)
                    context_data[PROCESSEOR_CONTEXT_DATA_NAME]['yolox_file_path_list'] = yolox_file_path_list
                    context_data[PROCESSEOR_CONTEXT_DATA_NAME]['img_yolox_infy_table_extractor_file_path'] = yolox_tables_content_file_path

                    if technique_name == "pdf_scanned_ocr_extractor":
                        # pdf_image_infy_ocr_engine_extractor is dependent on pdf_apache_pdfbox, pdf_box_image_extractor and pdf_image_converter
                        pdf_apache_pdfbox_ocr_file_path = context_data[
                            PROCESSEOR_CONTEXT_DATA_NAME]["pdf_apache_pdfbox_ocr_file_path"]
                        images_content_file_path = context_data[
                            PROCESSEOR_CONTEXT_DATA_NAME]["image_contents_file_path"]
                        pdf_to_images_files_path_list = context_data[
                            PROCESSEOR_CONTEXT_DATA_NAME]["pdf_to_images_files_path_list"]

                        if pdf_apache_pdfbox_ocr_file_path and images_content_file_path:
                            image_to_ocr_extractor_obj = PdfScannedOcrExtractor(
                                text_provider_dict)
                            scanned_pages_resource_path_list, scanned_pages_full_path_list = image_to_ocr_extractor_obj.get_scanned_pages(
                                from_files_full_path, out_file_full_path, pdf_apache_pdfbox_ocr_file_path, images_content_file_path, pdf_to_images_files_path_list)
                        else:
                            self.__logger.error(
                                "The following techniques are required and should be enabled to run this technique: 1. pdf_apache_pdfbox, 2. pdf_box_image_extractor, 3. pdf_image_converter."
                            )
                        if scanned_pages_resource_path_list and scanned_pages_full_path_list:
                            image_to_ocr_extractor_obj = ImagesTextExtractor(
                                text_provider_dict)
                            ocr_paths = image_to_ocr_extractor_obj.generate_ocr(
                                scanned_pages_full_path_list, out_file_full_path)
                            ocr_file_path_list = [
                                f"/{path.split('//')[1]}" for path in ocr_paths]

                            for pages in scanned_pages_resource_path_list:
                                self.__file_sys_handler.delete_file(pages)
                    context_data[PROCESSEOR_CONTEXT_DATA_NAME]['pdf_scanned_ocr_path_list'] = ocr_file_path_list

                elif input_file_type == 'image' and extension in ['.jpg', '.jpeg', '.png', '.tiff', '.tif']:
                    out_file_full_path = f'{from_files_full_path}_files'
                    if not os.path.exists(out_file_full_path):
                        os.makedirs(out_file_full_path)
                    if technique_name in ['img_infy_ocr_engine_extractor', 'img_tesseracct_ocr_extractor', 'img_azure_read_ocr_extractor']:
                        if extension == '.tiff' or extension == '.tif':
                            image_to_ocr_extractor_obj = ImagesTextExtractor(
                                text_provider_dict)
                            ocr_file_path_list, image_file_path_list = image_to_ocr_extractor_obj.get_ocr_from_images(
                                from_files_full_path, out_file_full_path)
                        else:
                            image_to_ocr_extractor_obj = ImagesTextExtractor(
                                text_provider_dict)
                            ocr_file_path, image_file_path = image_to_ocr_extractor_obj.get_ocr_from_images(
                                from_files_full_path, out_file_full_path)
                    context_data[PROCESSEOR_CONTEXT_DATA_NAME]['image_ocr'] = {
                        'image_ocr_file_path': ocr_file_path,
                        'image_file_path': image_file_path
                    }
                    context_data[PROCESSEOR_CONTEXT_DATA_NAME]['tiff_image_ocr'] = {
                        'tiff_image_ocr_file_path_list': ocr_file_path_list,
                        'tiff_image_file_path_list': image_file_path_list
                    }

                    if technique_name == "img_yolox_infy_table_extractor":
                        yolox_table_extactor_obj = YoloxTableExtactor(
                            model_provider_dict, text_provider_dict, technique.get("line_detection_method"))
                        if extension == '.tiff' or extension == '.tif':
                            images_file_path_list = context_data[
                                PROCESSEOR_CONTEXT_DATA_NAME]["tiff_image_ocr"]["tiff_image_file_path_list"]
                        else:
                            images_file_path_list = [context_data[
                                PROCESSEOR_CONTEXT_DATA_NAME]["image_ocr"]["image_file_path"]]
                        yolox_tables_content_file_path, yolox_file_path_list = yolox_table_extactor_obj.get_tables_content(
                            images_file_path_list, from_files_full_path, out_file_full_path, table_debug)
                    context_data[PROCESSEOR_CONTEXT_DATA_NAME]['yolox_file_path_list'] = yolox_file_path_list
                    context_data[PROCESSEOR_CONTEXT_DATA_NAME]['img_yolox_infy_table_extractor_file_path'] = yolox_tables_content_file_path

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

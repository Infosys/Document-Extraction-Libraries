# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#
import os
import re
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
from infy_dpp_content_extractor.content_extractor.process.docling_table_extractor import DoclingTableExtactor
PROCESSOR_CONTEXT_DATA_NAME = "content_extractor"


class ContentExtractor(infy_dpp_sdk.interface.IProcessor):
    def __init__(self):
        self.__file_sys_handler = self.get_fs_handler()
        self.__app_config = self.get_app_config()
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
        docling_tables_content_file_path = ""
        docling_file_path_list = []
        processor_response_data = ProcessorResponseData()
        content_extractor_config_data = config_data.get('ContentExtractor', {})
        # For two separate nodes for (text,image) and table extraction in sequence pipeline
        if not content_extractor_config_data:
            for key, val in config_data.items():
                processor_name = key
                content_extractor_config_data = val
                break
        org_files_full_path = context_data['request_creator']['work_file_path']
        from_files_full_path = __get_temp_file_path(org_files_full_path)
        _, extension = os.path.splitext(from_files_full_path)

        processor_context_data_name = PROCESSOR_CONTEXT_DATA_NAME
        if 'ContentExtractor' in config_data:
            context_data[processor_context_data_name] = {}
            context_data[processor_context_data_name]["content_extractor_text"] = {}
            context_data[processor_context_data_name]["content_extractor_image"] = {}
            context_data[processor_context_data_name]["content_extractor_table"] = {}
        else:
            # For two separate nodes - (text ,image) and table extraction in sequence pipeline
            def __camel_to_snake(name):
                name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
                return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()
            if processor_name:
                processor_context_data_name = __camel_to_snake(
                    processor_name)
                context_data[processor_context_data_name] = {}
                if "content_extractor_text" not in context_data:
                    context_data["content_extractor_text"] = {}
                elif "content_extractor_image" not in context_data:
                    context_data["content_extractor_image"] = {}
                elif "content_extractor_table" not in context_data:
                    context_data["content_extractor_table"] = {}

        for technique in content_extractor_config_data.get('techniques', []):
            text_provider_dict, model_provider_dict = {}, {}
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
                            text_provider_dict, self.__file_sys_handler, self.__logger, self.__app_config)
                        pdf_to_images_files_path_list = pdf_to_images_converter_obj.get_images_path_list(
                            from_files_full_path, out_file_full_path)

                    if technique_name == "pdf_apache_pdfbox":
                        pdf_box_based_ocr_generator_obj = PdfBoxBasedOcrGenerator(
                            text_provider_dict,  self.__file_sys_handler, self.__logger, self.__app_config)
                        pdf_apache_pdfbox_ocr_file_path = pdf_box_based_ocr_generator_obj.generate_ocr_json_for_pdf(
                            from_files_full_path, out_file_full_path)

                    if technique_name == "pdf_image_apache_pdfbox":
                        # ---- Note: pdf_image_apache_pdfbox is dependent on pdf_image_converter and pdf_apache_pdfbox ----#
                        if processor_context_data_name != PROCESSOR_CONTEXT_DATA_NAME:
                            # Read dependent tech data for two separate nodes - (text ,image) and table extraction sequence pipeline
                            pdf_to_images_files_path_list = context_data[
                                "content_extractor_text"]["pdf_to_images_files_path_list"]
                            pdf_apache_pdfbox_ocr_file_path = context_data[
                                "content_extractor_text"]["pdf_apache_pdfbox_ocr_file_path"]
                        else:
                            pdf_to_images_files_path_list = context_data[
                                processor_context_data_name]["content_extractor_text"]["pdf_to_images_files_path_list"]
                            pdf_apache_pdfbox_ocr_file_path = context_data[
                                processor_context_data_name]["content_extractor_text"]["pdf_apache_pdfbox_ocr_file_path"]
                        pdf_box_based_ocr_generator_obj = PdfBoxBasedOcrGenerator(
                            text_provider_dict, self.__file_sys_handler, self.__logger, self.__app_config)
                        ocr_files_path_list = pdf_box_based_ocr_generator_obj.generate_ocr(
                            pdf_to_images_files_path_list, from_files_full_path, out_file_full_path, pdf_apache_pdfbox_ocr_file_path)

                    if technique_name == "pdf_plumber_table_extractor":
                        pdf_plumber_table_extractor_obj = PdfPlumberTableExtractor(
                            self.__file_sys_handler, self.__logger, self.__app_config, text_provider_dict)
                        table_content_file_path = pdf_plumber_table_extractor_obj.get_tables_content(
                            from_files_full_path, out_file_full_path)
                        if table_content_file_path:
                            self.__logger.debug("Table/s detected in PDF file")

                    if technique_name == "pdf_box_image_extractor":
                        pdf_box_images_extractor_obj = PdfBoxImagesExtractor(
                            text_provider_dict,  self.__file_sys_handler, self.__logger, self.__app_config)
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
                                text_provider_dict, self.__file_sys_handler, self.__logger, self.__app_config)
                            images_text_extractor_obj.get_images_text(
                                from_files_full_path, out_file_full_path)

                    if technique_name == "pdf_img_yolox_td":
                        # ---- Note: pdf_img_yolox_td is dependent on pdf_image_converter ---- #
                        yolox_table_extactor_obj = YoloxTableExtactor(
                            model_provider_dict, text_provider_dict, self.__file_sys_handler, self.__logger, self.__app_config, technique.get("line_detection_method"))
                        if processor_context_data_name != PROCESSOR_CONTEXT_DATA_NAME:
                            # Read dependent tech data for two separate nodes - (text ,image) and table extraction sequence pipeline
                            images_file_path_list = context_data["content_extractor_text"]["pdf_to_images_files_path_list"]
                        else:
                            images_file_path_list = context_data[processor_context_data_name][
                                "content_extractor_text"]["pdf_to_images_files_path_list"]
                        yolox_tables_content_file_path, yolox_file_path_list = yolox_table_extactor_obj.get_tables_content(
                            images_file_path_list, from_files_full_path, out_file_full_path, table_debug)

                    if technique_name == "pdf_img_docling_td_tsr":
                        # ---- Note: pdf_img_docling_td_tsr is dependent on pdf_image_converter ---- #
                        docling_table_extactor_obj = DoclingTableExtactor(
                            model_provider_dict, text_provider_dict, self.__file_sys_handler,
                            self.__logger, self.__app_config)
                        if processor_context_data_name != PROCESSOR_CONTEXT_DATA_NAME:
                            # Read dependent tech data for two separate nodes - (text ,image) and table extraction sequence pipeline
                            images_file_path_list = context_data["content_extractor_text"]["pdf_to_images_files_path_list"]
                        else:
                            images_file_path_list = context_data[processor_context_data_name][
                                "content_extractor_text"]["pdf_to_images_files_path_list"]

                        docling_tables_content_file_path, docling_file_path_list = docling_table_extactor_obj.get_tables_content(
                            images_file_path_list, from_files_full_path, out_file_full_path, table_debug)

                    if technique_name == "pdf_scanned_ocr_extractor":
                        # ---- Note: pdf_image_infy_ocr_engine_extractor is dependent on pdf_apache_pdfbox, pdf_box_image_extractor and pdf_image_converter ---#
                        if processor_context_data_name != PROCESSOR_CONTEXT_DATA_NAME:
                            # Read dependent tech data for two separate nodes - (text ,image) and table extraction sequence pipeline
                            pdf_apache_pdfbox_ocr_file_path = context_data[
                                "content_extractor_text"]["pdf_apache_pdfbox_ocr_file_path"]
                            images_content_file_path = context_data[
                                "content_extractor_image"]["image_contents_file_path"]
                            pdf_to_images_files_path_list = context_data[
                                "content_extractor_text"]["pdf_to_images_files_path_list"]
                        else:
                            pdf_apache_pdfbox_ocr_file_path = context_data[
                                processor_context_data_name]["content_extractor_text"]["pdf_apache_pdfbox_ocr_file_path"]
                            images_content_file_path = context_data[
                                processor_context_data_name]["content_extractor_image"]["image_contents_file_path"]
                            pdf_to_images_files_path_list = context_data[
                                processor_context_data_name]["content_extractor_text"]["pdf_to_images_files_path_list"]

                        image_to_ocr_extractor_obj = PdfScannedOcrExtractor(
                            text_provider_dict, self.__file_sys_handler, self.__logger, self.__app_config)
                        scanned_pages_resource_path_list, scanned_pages_full_path_list = image_to_ocr_extractor_obj.get_scanned_pages(
                            from_files_full_path, out_file_full_path, pdf_apache_pdfbox_ocr_file_path, images_content_file_path, pdf_to_images_files_path_list)

                        if scanned_pages_resource_path_list and scanned_pages_full_path_list:
                            image_to_ocr_extractor_obj = ImagesTextExtractor(
                                text_provider_dict,  self.__file_sys_handler, self.__logger, self.__app_config)
                            ocr_paths = image_to_ocr_extractor_obj.generate_ocr(
                                scanned_pages_full_path_list, out_file_full_path)
                            ocr_file_path_list = [
                                f"/{path.split('//')[1]}" for path in ocr_paths]

                            for pages in scanned_pages_resource_path_list:
                                self.__file_sys_handler.delete_file(pages)

                elif input_file_type == 'image' and extension in ['.jpg', '.jpeg', '.png', '.tiff', '.tif']:
                    out_file_full_path = f'{from_files_full_path}_files'
                    if not os.path.exists(out_file_full_path):
                        os.makedirs(out_file_full_path)
                    if technique_name in ['img_infy_ocr_engine_extractor', 'img_tesseracct_ocr_extractor', 'img_azure_read_ocr_extractor']:
                        if extension == '.tiff' or extension == '.tif':
                            image_to_ocr_extractor_obj = ImagesTextExtractor(
                                text_provider_dict, self.__file_sys_handler, self.__logger, self.__app_config)
                            ocr_file_path_list, image_file_path_list = image_to_ocr_extractor_obj.get_ocr_from_images(
                                from_files_full_path, out_file_full_path)
                        else:
                            image_to_ocr_extractor_obj = ImagesTextExtractor(
                                text_provider_dict,  self.__file_sys_handler, self.__logger, self.__app_config)
                            ocr_file_path, image_file_path = image_to_ocr_extractor_obj.get_ocr_from_images(
                                from_files_full_path, out_file_full_path)

                    if technique_name == "img_yolox_td":
                        # --- Note: img_yolox_td is dependent on either of 'img_infy_ocr_engine_extractor', 'img_tesseracct_ocr_extractor', 'img_azure_read_ocr_extractor' ---#
                        yolox_table_extactor_obj = YoloxTableExtactor(
                            model_provider_dict, text_provider_dict, self.__file_sys_handler, self.__logger, self.__app_config, technique.get("line_detection_method"))
                        if extension == '.tiff' or extension == '.tif':
                            if processor_context_data_name != PROCESSOR_CONTEXT_DATA_NAME:
                                # Read dependent tech data for two separate nodes - (text ,image) and table extraction sequence pipeline
                                images_file_path_list = context_data["content_extractor_image"][
                                    "tiff_image_ocr"]["tiff_image_file_path_list"]
                            else:
                                images_file_path_list = context_data[
                                    processor_context_data_name]["content_extractor_image"]["tiff_image_ocr"]["tiff_image_file_path_list"]
                        else:
                            if processor_context_data_name != PROCESSOR_CONTEXT_DATA_NAME:
                                # Read dependent tech data for two separate nodes - (text ,image) and table extraction sequence pipeline
                                images_file_path_list = [
                                    context_data["content_extractor_image"]["image_ocr"]["image_file_path"]]
                            else:
                                images_file_path_list = [context_data[
                                    processor_context_data_name]["content_extractor_image"]["image_ocr"]["image_file_path"]]
                        yolox_tables_content_file_path, yolox_file_path_list = yolox_table_extactor_obj.get_tables_content(
                            images_file_path_list, from_files_full_path, out_file_full_path, table_debug)

                    if technique_name == "img_docling_td_tsr":
                        docling_table_extactor_obj = DoclingTableExtactor(
                            model_provider_dict, text_provider_dict, self.__file_sys_handler,
                            self.__logger, self.__app_config)
                        if extension == '.tiff' or extension == '.tif':
                            if processor_context_data_name != PROCESSOR_CONTEXT_DATA_NAME:
                                # Read dependent tech data for two separate nodes - (text ,image) and table extraction sequence pipeline
                                images_file_path_list = context_data["content_extractor_image"][
                                    "tiff_image_ocr"]["tiff_image_file_path_list"]
                            else:
                                images_file_path_list = context_data[
                                    processor_context_data_name]["content_extractor_image"]["tiff_image_ocr"]["tiff_image_file_path_list"]
                        else:
                            if processor_context_data_name != PROCESSOR_CONTEXT_DATA_NAME:
                                # Read dependent tech data for two separate nodes - (text ,image) and table extraction sequence pipeline
                                images_file_path_list = [
                                    context_data["content_extractor_image"]["image_ocr"]["image_file_path"]]
                            else:
                                images_file_path_list = [context_data[
                                    processor_context_data_name]["content_extractor_image"]["image_ocr"]["image_file_path"]]
                        docling_tables_content_file_path, docling_file_path_list = docling_table_extactor_obj.get_tables_content(
                            images_file_path_list, from_files_full_path, out_file_full_path, table_debug)
                # Populate context_data
                if processor_context_data_name != PROCESSOR_CONTEXT_DATA_NAME:
                    # For TF pipline, separate table node in sequence to content_extractor's (text,image) node
                    if processor_context_data_name == "content_extractor_table":
                        context_data["content_extractor_table"]['yolox_file_path_list'] = yolox_file_path_list
                        context_data["content_extractor_table"]['img_yolox_infy_table_extractor_file_path'] = yolox_tables_content_file_path
                        context_data["content_extractor_table"]['table_contents_file_path'] = table_content_file_path
                        context_data["content_extractor_table"]['docling_file_path_list'] = docling_file_path_list
                        context_data["content_extractor_table"]['img_docling_td_tsr_file_path'] = docling_tables_content_file_path

                    else:
                        context_data["content_extractor_text"]["pdf_to_images_files_path_list"] = pdf_to_images_files_path_list
                        context_data["content_extractor_text"]["pdf_apache_pdfbox_ocr_file_path"] = pdf_apache_pdfbox_ocr_file_path
                        context_data["content_extractor_text"]["ocr_files_path_list"] = ocr_files_path_list
                        context_data["content_extractor_image"]['image_contents_file_path'] = images_content_file_path
                        context_data["content_extractor_text"]['pdf_scanned_ocr_path_list'] = ocr_file_path_list
                        context_data["content_extractor_image"]['image_ocr'] = {
                            'image_ocr_file_path': ocr_file_path,
                            'image_file_path': image_file_path
                        }
                        context_data["content_extractor_image"]['tiff_image_ocr'] = {
                            'tiff_image_ocr_file_path_list': ocr_file_path_list,
                            'tiff_image_file_path_list': image_file_path_list
                        }

                else:
                    context_data[processor_context_data_name]["content_extractor_text"][
                        "pdf_to_images_files_path_list"] = pdf_to_images_files_path_list
                    context_data[processor_context_data_name]["content_extractor_text"][
                        "pdf_apache_pdfbox_ocr_file_path"] = pdf_apache_pdfbox_ocr_file_path
                    context_data[processor_context_data_name]["content_extractor_text"]["ocr_files_path_list"] = ocr_files_path_list
                    context_data[processor_context_data_name]["content_extractor_table"][
                        'table_contents_file_path'] = table_content_file_path
                    context_data[processor_context_data_name]["content_extractor_image"][
                        'image_contents_file_path'] = images_content_file_path
                    context_data[processor_context_data_name]["content_extractor_table"]['yolox_file_path_list'] = yolox_file_path_list
                    context_data[processor_context_data_name]["content_extractor_table"][
                        'img_yolox_infy_table_extractor_file_path'] = yolox_tables_content_file_path
                    context_data[processor_context_data_name]["content_extractor_table"]['docling_file_path_list'] = docling_file_path_list
                    context_data[processor_context_data_name]["content_extractor_table"][
                        'img_docling_td_tsr_file_path'] = docling_tables_content_file_path
                    context_data[processor_context_data_name]["content_extractor_text"]['pdf_scanned_ocr_path_list'] = ocr_file_path_list
                    context_data[processor_context_data_name]["content_extractor_image"]['image_ocr'] = {
                        'image_ocr_file_path': ocr_file_path,
                        'image_file_path': image_file_path
                    }
                    context_data[processor_context_data_name]["content_extractor_image"]['tiff_image_ocr'] = {
                        'tiff_image_ocr_file_path_list': ocr_file_path_list,
                        'tiff_image_file_path_list': image_file_path_list
                    }

        # Populate response data
        processor_response_data.document_data = document_data
        processor_response_data.context_data = context_data

        self.__logger.debug('Content Extraction Completed')
        return processor_response_data

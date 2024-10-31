# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import json
import infy_dpp_sdk
import infy_fs_utils


class PdfScannedOcrExtractor:
    def __init__(self, text_provider_dict):
        self.__logger = infy_fs_utils.manager.FileSystemLoggingManager().get_fs_logging_handler(
            infy_dpp_sdk.common.Constants.FSLH_DPP).get_logger()
        self.__app_config = infy_dpp_sdk.common.AppConfigManager().get_app_config()
        self.__file_sys_handler = infy_fs_utils.manager.FileSystemManager(
        ).get_fs_handler(infy_dpp_sdk.common.Constants.FSH_DPP)

        self.__text_provider_dict = text_provider_dict
        self.__converter_path = self.__text_provider_dict.get(
            'properties').get('format_converter_home', '')
        if self.__converter_path == '':
            raise Exception(
                'Format converter path is not configured in the config file')
        self._org_pdf_file_path = None

    def get_scanned_pages(self, from_files_full_path, out_file_full_path, pdf_apache_pdfbox_ocr_file_path, images_content_file_path, pdf_to_images_files_path_list) -> list:
        ''' Get list of scanned pages from the input pdf file '''

        scanned_pages_path_list, scanned_pages_full_path_list = [], []
        if self.__text_provider_dict.get('properties').get('scanned_pdf'):
            pdfbox_file = json.loads(self.__file_sys_handler.read_file(
                pdf_apache_pdfbox_ocr_file_path))
            image_content_file = json.loads(self.__file_sys_handler.read_file(
                images_content_file_path))

            scanned_pages_path_list = []
            scanned_pages_resource_path_list = []
            for i in range(min(len(pdfbox_file), len(image_content_file))):
                pdfbox_tokens = pdfbox_file[i].get('tokens', [])
                image_content_tokens = image_content_file[i].get('tokens', [])

                if not pdfbox_tokens and len(image_content_tokens) == 1:
                    scanned_pages_path_list.append(
                        pdf_to_images_files_path_list[i])

                    for token in image_content_file[i].get('tokens', []):
                        token_id = token.get('id', '')
                        if token_id:
                            jpg_path = f"/{out_file_full_path.split('//')[1]}/{token_id}.jpg"
                            hocr_path = f"{jpg_path}.hocr"
                            scanned_pages_resource_path_list.append(jpg_path)
                            scanned_pages_resource_path_list.append(hocr_path)

            scanned_pages_full_path_list = []
            for page in scanned_pages_path_list:
                full_path = (self.__file_sys_handler.get_abs_path(
                    page)).replace('filefile://', '')
                scanned_pages_full_path_list.append(full_path)
        else:
            self.__logger.debug(
                'Scanned PDF is not enabled, returning empty list')

        return scanned_pages_resource_path_list, scanned_pages_full_path_list

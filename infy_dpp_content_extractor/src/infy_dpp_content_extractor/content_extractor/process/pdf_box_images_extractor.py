# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#
import os
import infy_dpp_sdk
import infy_fs_utils

from infy_dpp_content_extractor.content_extractor.service import ImagesFromPdfExtractorService
from infy_dpp_content_extractor.common.file_util import FileUtil


class PdfBoxImagesExtractor:
    def __init__(self, text_provider_dict):
        self.__logger = infy_fs_utils.manager.FileSystemLoggingManager().get_fs_logging_handler(
            infy_dpp_sdk.common.Constants.FSLH_DPP).get_logger()
        self.__app_config = infy_dpp_sdk.common.AppConfigManager().get_app_config()
        self.__file_sys_handler = infy_fs_utils.manager.FileSystemManager(
        ).get_fs_handler(infy_dpp_sdk.common.Constants.FSH_DPP)

        self.__converter_path = text_provider_dict.get(
            'properties').get('format_converter_home', '')
        if self.__converter_path == '':
            raise Exception(
                'Format converter path is not configured in the config file')
        self._org_pdf_file_path = None

    def get_images_content(self, from_files_full_path, out_file_full_path) -> list:
        '''getting images from pdf file'''
        self._org_pdf_file_path = from_files_full_path
        # Pdf to image bbox
        config_data_dict = {
            "format_converter": {
                "to_dir": os.path.abspath(out_file_full_path),
                "saveresource": True
            },
            "format_converter_home": self.__converter_path
        }
        self.__logger.info('...PDF to images extraction started...')
        image_generator_service_obj = ImagesFromPdfExtractorService()
        images_content_path, _ = image_generator_service_obj.get_images_from_pdf(
            os.path.abspath(self._org_pdf_file_path), config_data_dict)

        images_content = FileUtil.load_json(images_content_path)
        # Iterate over each page in images_content
        for page in images_content:
            # Check if 'tokens' key exists in the page and if all tokens are empty
            if 'tokens' in page and all(not token for token in page['tokens']):
                FileUtil.delete_file(images_content_path)
                return ""
            else:
                break

        # upload the json file to the work location
        server_file_dir = os.path.dirname(images_content_path.replace('\\', '/').replace('//', '/').replace(
            self.__app_config["CONTAINER"]["APP_DIR_TEMP_PATH"].replace('\\', '/').replace('//', '/'), ''))
        local_dir = os.path.dirname(images_content_path)
        self._upload_data(f'{local_dir}', f'{server_file_dir}')

        images_content_path_file_path = images_content_path.replace('\\', '/').replace('//', '/').replace(
            self.__app_config["CONTAINER"]["APP_DIR_TEMP_PATH"].replace('\\', '/').replace('//', '/'), '')

        return images_content_path_file_path

    def _upload_data(self, local_file_path, server_file_path):
        try:
            self.__file_sys_handler.put_folder(
                local_file_path, os.path.dirname(server_file_path))
            self.__logger.info(
                f'Folder {local_file_path} uploaded successfully')
        except Exception as e:
            self.__logger.error(
                f'Error while uploading data to {server_file_path} : {e}')
            raise e

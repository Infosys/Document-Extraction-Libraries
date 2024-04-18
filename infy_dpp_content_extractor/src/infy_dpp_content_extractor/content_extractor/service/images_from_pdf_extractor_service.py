# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#
import copy
import infy_dpp_sdk
import infy_fs_utils
import infy_common_utils.format_converter as format_converter
from infy_common_utils.format_converter import ConvertAction, FormatConverter
from infy_dpp_content_extractor.common.file_util import FileUtil


class ImagesFromPdfExtractorService:
    def __init__(self):
        self.__logger = infy_fs_utils.manager.FileSystemLoggingManager(
        ).get_fs_logging_handler(infy_dpp_sdk.common.Constants.FSLH_DPP).get_logger()

    def get_images_from_pdf(self, pdf_file_path, config_param_dict):
        self.__logger.info(f"[IMG_FRM_PDF]: Extract File - {pdf_file_path}")
        config_param_dict_cp = copy.deepcopy(
            config_param_dict.get("format_converter"))
        format_converter.format_converter_jar_home = config_param_dict.get(
            "format_converter_home")
        # PDF_TO_IMAGE_BBOX
        img_files, error = FormatConverter.execute(
            pdf_file_path, convert_action=ConvertAction.PDF_TO_IMAGE_BBOX, config_param_dict=config_param_dict_cp)
        img_files = img_files.replace("\n", "")
        return img_files, error

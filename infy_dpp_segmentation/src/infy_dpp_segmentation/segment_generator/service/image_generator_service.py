# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#


import os
import copy
from PIL import Image
# import infy_common_utils.format_converter as format_converter
# from infy_common_utils.format_converter import ConvertAction, FormatConverter
from infy_dpp_segmentation.common.logger_factory import LoggerFactory
from infy_dpp_segmentation.common.singleton import Singleton
from infy_dpp_segmentation.common.file_util import FileUtil


class ImageGeneratorService(metaclass=Singleton):

    def __init__(self):
        self.__logger = LoggerFactory().get_logger()
    # Commented by Rashmi to remove format converter import
    # def convert_pdf_to_image(self, pdf_file_path, config_param_dict):
    #     self.__logger.info(f"[PDF2IMG]: Convert File - {pdf_file_path}")
    #     config_param_dict_cp = copy.deepcopy(
    #         config_param_dict.get("format_converter"))
    #     work_doc_file = self.__manage_converter_config(
    #         pdf_file_path, config_param_dict_cp)
    #     format_converter.format_converter_jar_home = config_param_dict.get(
    #         "format_converter_home")
    #     # PDF_TO_IMAGE
    #     img_files, error = FormatConverter.execute(
    #         pdf_file_path, convert_action=ConvertAction.PDF_TO_IMAGE, config_param_dict=config_param_dict_cp)
    #     if not img_files:
    #         img_files = []
    #     # FileUtil.delete_file(work_doc_file)
    #     return img_files, error

    def convert_img_to_jpg(self, filepath, config_param_dict):
        self.__logger.info(f"[IMG2JPG]: Convert File - {filepath}")
        doc_extension = os.path.splitext(
            filepath)[1].lower()
        config_param_dict_cp = copy.deepcopy(
            config_param_dict.get("format_converter"))
        if doc_extension in ['.jpg', '.png', '.jpeg']:
            work_folder = self.__manage_converter_config(
                filepath, config_param_dict_cp)
            save_image_path = f'{work_folder}/1{doc_extension}'
            image_path = self.__convert_image_to_jpg(
                filepath, save_image_path)
        return [image_path], ''

    def __convert_image_to_jpg(self, orig_image_path, save_as_path):
        parent_path = os.path.dirname(save_as_path)
        if not os.path.exists(parent_path):
            os.makedirs(parent_path)
        # save the image as it is
        with Image.open(orig_image_path) as img:
            # if os.path.splitext(orig_image_path)[-1].lower() == '.png':
            #     img.convert('RGB').save(save_as_path, quality=100)
            # else:
            img.save(save_as_path, quality=100)
            print('File saved =', save_as_path)
        return save_as_path

    def __manage_converter_config(self, pdf_file_path, config_param_dict):
        if not config_param_dict.get("to_dir"):
            work_doc_file, error_val = FileUtil.copy_to_work_dir(
                config_param_dict.get("to_dir"), None, '', pdf_file_path)
            config_param_dict["to_dir"] = FileUtil.create_dirs_if_absent(
                f"{work_doc_file}_files")
            if error_val:
                raise Exception(error_val)
        else:
            work_doc_file = config_param_dict.get("to_dir")

        return work_doc_file

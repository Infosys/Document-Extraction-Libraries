# ===============================================================================================================#
#
# Copyright 2023 Infosys Ltd.
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at
# http://www.apache.org/licenses/
#
# ===============================================================================================================#

import os
import io
import enum
import glob
import json
import traceback
import logging
import copy
import imageio
import shutil
import subprocess
from pathlib import Path
from infy_ocr_generator.internal.file_util import FileUtil
from infy_ocr_generator.interface.data_service_provider_interface import (
    GENERATE_API_RES_STRUCTURE, RESCALE_DATA, DataServiceProviderInterface,
    DOC_DATA)

JAR_GENERAL_ERROR_MSG = 'Error occurred in main method'
format_converter_jar_home = ''

FOR_CONV_CONFIG_PARAMS_DICT = {
    "to_dir": None,
    "hocr_file": None,
    "dpi": 300,
    "pages": [],
    "angles": [],
    "bboxes": [[]],
    "water_mark": None,
    "plotbbox": None,
    "page_dimension": {
        "width": 0,
        "height": 0
    }
}
CONFIG_PARAMS_DICT = {
    "format_converter": {
        "format_converter_path": "",
        "format_converter_config_dict": FOR_CONV_CONFIG_PARAMS_DICT
    }
}
ENCODING_LIST = ['utf-8', 'ascii', 'ansi']


class ApachePdfboxDataServiceProvider(DataServiceProviderInterface):
    """Implementation of DataServiceProvider for  apache pdfbox"""
    class ConvertAction(enum.Enum):
        """Enum class to Convert Action
        Args:
            enum (str): Enum Action
        """
        PDF_TO_TEXT_BBOX = "PdfToTextBbox"

    class FormatConverter:
        """Class to convert document format.
        """

        def __init__(self):
            pass

        @ classmethod
        def execute(cls, from_file, convert_action=None,
                    config_param_dict: FOR_CONV_CONFIG_PARAMS_DICT = None):
            """Convertes given file based on action chosen.

            Args:
                from_file (str): Required file to change to other format.
                convert_action (enum, optional): Action to proceed on given document. Defaults to ConvertAction.PDF_TO_JSON.
                config_param_dict (dict, optional): Additional params to chosen action. Defaults to CONFIG_PARAM_DICT.

            Returns:
                [json]: if convert_action=ConvertAction.PDF_TO_JSON.
                [str]: if convert_action=ConvertAction.PDF_TO_TXT.
            """
            config_param_dict = FileUtil.get_updated_config_dict(
                config_param_dict, FOR_CONV_CONFIG_PARAMS_DICT)
            run_command = ['java', '-jar', cls.__get_tool_path(),
                           convert_action.value, '--fromfile', from_file]

            if config_param_dict["to_dir"]:
                run_command += ["--todir", config_param_dict["to_dir"]]
            if config_param_dict["hocr_file"]:
                run_command += ["--hocrfile", config_param_dict["hocr_file"]]
            if config_param_dict["water_mark"]:
                run_command += ["--watermarktext",
                                config_param_dict["water_mark"]]
            if config_param_dict["dpi"]:
                run_command += ["--dpi", str(config_param_dict["dpi"])]
            if config_param_dict["plotbbox"]:
                run_command += ["--plotbbox",
                                str(config_param_dict["plotbbox"])]
            if config_param_dict["angles"]:
                run_command += ["--angles", ",".join(str(angle)
                                                     for angle in config_param_dict["angles"])]
            if config_param_dict["pages"]:
                run_command += ['--pages', ",".join(str(page)
                                                    for page in config_param_dict["pages"])]
            if config_param_dict["bboxes"] and config_param_dict["bboxes"][0]:
                for i, bbox in enumerate(config_param_dict["bboxes"]):
                    run_command += [f"--bbox{i+1}",
                                    ",".join([str(reg) for reg in bbox])]
            page_dim = config_param_dict["page_dimension"]
            if page_dim and page_dim["width"] > 0 and page_dim["height"] > 0:
                run_command += ['--pagewidth', str(config_param_dict["page_dimension"]["width"]),
                                '--pageheight', str(config_param_dict["page_dimension"]["height"])]

            sub_process = subprocess.Popen(
                run_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            stdout, stderr = sub_process.communicate()
            if (not stdout and stderr) or (JAR_GENERAL_ERROR_MSG in stdout):
                logger = logging.getLogger(os.path.basename(__file__))
                logger.error(stderr)
                return None, stderr

            if convert_action in [ApachePdfboxDataServiceProvider.ConvertAction.PDF_TO_TEXT_BBOX]:
                return stdout.strip().split('\n'), None
            else:
                return stdout, None

        @classmethod
        def __get_tool_path(cls):
            JAR_FILE_FORMAT = "infy-format-converter-*.jar"
            tool_path = str(
                f"{format_converter_jar_home}/{JAR_FILE_FORMAT}")
            format_convert_jars = glob.glob(tool_path)
            format_convert_jars.sort(reverse=True)
            if format_convert_jars:
                tool_path = str(Path(format_convert_jars[0]).resolve())
            else:
                raise Exception(
                    f"Could not find any jar file of format '{JAR_FILE_FORMAT}' at provided path '{format_converter_jar_home}'")
            return tool_path

    def __init__(self, config_params_dict: CONFIG_PARAMS_DICT,
                 output_dir: str = None,
                 output_to_supporting_folder: bool = False,
                 overwrite: bool = False,
                 logger: logging.Logger = None,
                 log_level: int = None):
        """Creates an instance of Apache Pdfbox Ocr Data Service Provider

        Args:
            config_params_dict (CONFIG_PARAMS_DICT): Provider CONFIG values.
            output_dir (str, optional): Directory to generate OCR file,
                if not given will generate into same file location. Defaults to None.
            output_to_supporting_folder (bool, optional): If True, OCR file will be generated to
                same file location but into supporting folder named `* _files`. Defaults to False.
            overwrite (bool, optional): If True, existing OCR file will be overwritten. Defaults to False.
            logger (logging.Logger, optional): logger object. Defaults to None.
            log_level (int, optional):log level. Defaults to None.

        Raises:
            FileNotFoundError: Raises an error if the file is not found.
        """
        super(ApachePdfboxDataServiceProvider,
              self).__init__(logger, log_level)
        global format_converter_jar_home
        self.config_params_dict = self.get_updated_config_dict(
            config_params_dict['format_converter'], CONFIG_PARAMS_DICT['format_converter'])
        if output_dir and not os.path.exists(output_dir):
            raise FileNotFoundError(f"{output_dir} not found")
        self.output_dir = output_dir
        self.output_to_supporting_folder = output_to_supporting_folder
        self.overwrite = overwrite
        if self.config_params_dict["format_converter_path"]:
            format_converter_jar_home = self.config_params_dict[
                "format_converter_path"]
        if self.config_params_dict["format_converter_config_dict"]:
            self.format_converter_config_dict = self.config_params_dict[
                "format_converter_config_dict"]

    def submit_request(self, doc_data_list: [DOC_DATA]) -> list:
        """API to submit tesseract ocr data service request for asynchorouns call

        Args:
            doc_data_list ([DOC_DATA]): List of input documents. e.g, ['c:/1.jpg','c:/1.pdf']

        Raises:
            NotImplementedError: Raises an error if the method is not implemented

        Returns:
            list: [SUB_RE_API_STRUCTURE]
        """
        raise NotImplementedError

    def receive_response(self, submit_req_response_list: list, rerun_unsucceeded_mode: bool = False) -> list:
        """API of tesseract ocr data service to Received response of asynchorouns call submit request.

        Args:
            submit_req_response_list (list): Response structure of `submit_request` api
            rerun_unsucceeded_mode (bool, optional): Enabling this mode and passing same request
             -will rerun for unsuccessful call. Defaults to False.

        Raises:
            NotImplementedError: Raises an error if the method is not implemented.

        Returns:
            list: [SUB_RE_API_STRUCTURE]
        """
        raise NotImplementedError

    def generate(self, doc_data_list: [DOC_DATA] = None, api_response_list: list = None) -> list:
        """API to generate OCR based on OCR provider given

        Args:
            doc_data_list ([DOC_DATA], optional): Use these input files to
                -implement technique and generate output files. Defaults to None.
            api_response_list (list, optional): API response will be generated into output file. Defaults to None.

        Returns:
            list: List of generated ocr file path.
        """
        def __detect_encoding(file_path):
            encodings = ENCODING_LIST
            for enc in encodings:
                try:
                    with io.open(file_path, 'r', encoding=enc) as f:
                        f.read()
                    return enc
                except UnicodeDecodeError:
                    continue

        def _call_pdfbox(in_doc_obj):
            gen_res_dict = copy.deepcopy(GENERATE_API_RES_STRUCTURE)
            pdf_file = in_doc_obj['doc_path']
            gen_res_dict['input_doc'] = pdf_file
            pages = in_doc_obj.get('pages', "")
            if pages:
                # TODO: max page no
                page_list = FileUtil.lookp_up_page(100, [pages])
            else:
                page_list = []

            output_doc = self.get_output_file(
                pdf_file, self.output_dir, self.output_to_supporting_folder,
                suffix='_pdfbox.json')

            gen_res_dict['output_doc'] = output_doc
            if not self.overwrite and os.path.exists(output_doc):
                return gen_res_dict

            config_param_dict = {
                "to_dir": os.path.abspath(os.path.dirname(output_doc)),
                "plotbbox": self.format_converter_config_dict.get('plotbbox'),
                "pages": page_list
            }
            output_files_list, _ = ApachePdfboxDataServiceProvider.FormatConverter().execute(
                os.path.abspath(in_doc_obj['doc_path']),
                convert_action=ApachePdfboxDataServiceProvider.ConvertAction.PDF_TO_TEXT_BBOX,
                config_param_dict=config_param_dict)
            output_bbox_file = [x for x in output_files_list if os.path.splitext(
                os.path.basename(x))[1] == '.json'][0]
            encoding = __detect_encoding(output_bbox_file)
            if encoding != 'utf-8':
                with open(output_bbox_file, encoding=encoding) as file:
                    raw_segment_data = json.load(file)
                FileUtil.save_to_json(output_bbox_file, raw_segment_data)
            # renmaing the file to proper format
            shutil.move(output_bbox_file, output_doc)
            return gen_res_dict

        if len(doc_data_list) == 0:
            raise Exception("Valid doc_data_list arg is required")
        ocr_list = []

        for in_doc_obj in doc_data_list:
            try:
                ocr_list.append(_call_pdfbox(in_doc_obj))
            except Exception:
                full_trace_error = traceback.format_exc()
                self.logger.error(full_trace_error)

        return ocr_list

    def rescale_dimension(self, doc_ocr_file_path, rescale_data_list: [RESCALE_DATA]) -> list:
        rescaled_data_list = []
        doc_ocr_data_list = FileUtil.load_json(doc_ocr_file_path)
        extracted_pages_list = [str(x['page']) for x in doc_ocr_data_list]
        for rescale_data in rescale_data_list:
            rescaled_data_dict = {}
            doc_page_num = rescale_data.get('doc_page_num')
            doc_page_width = rescale_data.get('doc_page_width')
            doc_page_height = rescale_data.get('doc_page_height')
            doc_file_path = rescale_data.get('doc_file_path')
            doc_file_extension = rescale_data.get('doc_file_extension')
            ocr_file_root_path = os.path.dirname(doc_ocr_file_path)
            if doc_page_num in extracted_pages_list:
                dpi = 0
                page_wise_ocr_data_dict = [
                    x for x in doc_ocr_data_list if str(x['page']) == doc_page_num][0]
                if doc_file_path and os.path.exists(doc_file_path) and doc_file_path.endswith(tuple(['png', 'jpg', 'jpeg'])):
                    doc_page_details = self.get_image_details(doc_file_path)
                    doc_page_width = doc_page_details['width']
                    doc_page_height = doc_page_details['height']
                    dpi = doc_page_details['dpi']
                    ocr_file_root_path = os.path.dirname(doc_file_path)
                    doc_file_extension = os.path.basename(
                        doc_file_path).rsplit('.', 1)[-1]
                ocr_width = page_wise_ocr_data_dict['width']
                ocr_height = page_wise_ocr_data_dict['height']
                scaling_factor = {'hor': doc_page_width /
                                  ocr_width, 'ver': doc_page_height/ocr_height}
                _ = [x.update({'bbox': FileUtil.get_updated_within_box(x['bbox'], scaling_factor)}) for x in
                     page_wise_ocr_data_dict.get('tokens')]
                infy_ocr_generator_metadata = {"dpi": dpi,
                                               "width": doc_page_width,
                                               "height": doc_page_height,
                                               "doc_page_num": doc_page_num
                                               }
                page_wise_ocr_data_dict.update({"width": doc_page_width,
                                                "height": doc_page_height,
                                                "infy_ocr_generator_metadata": infy_ocr_generator_metadata})
                ocr_file_path = f'{ocr_file_root_path}/{doc_page_num}.{doc_file_extension}_pdfbox.json'
                FileUtil.save_to_json(ocr_file_path, page_wise_ocr_data_dict)
                rescaled_data_dict['input_doc'] = doc_ocr_file_path
                rescaled_data_dict['output_doc'] = ocr_file_path
                rescaled_data_list.append(rescaled_data_dict)
            else:
                self.logger(
                    f'Either Page = {doc_page_num} is not extracted or is not present in doc')
                raise Exception(
                    f'Either Page = {doc_page_num} is not extracted or is not present in doc')
        return rescaled_data_list

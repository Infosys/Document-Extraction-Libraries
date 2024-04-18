# ===============================================================================================================#
# Copyright 2020 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import os
import enum
import json
from pathlib import Path
import glob
import subprocess
import logging
from infy_common_utils.internal.file_util import FileUtil


CONFIG_PARAM_DICT = {
    "to_dir": None,
    "hocr_file": None,
    "dpi": 300,
    "pages": [],
    "angles": [],
    "bboxes": [[]],
    "water_mark": None,
    "plotbbox": None,
    "saveresource": None,
    "page_dimension": {
        "width": 0,
        "height": 0
    }
}

JAR_GENERAL_ERROR_MSG = 'Error occurred in main method'

# Module variable to set jar home path. E.g. C:/ProgramFiles/InfyFormatConverter
format_converter_jar_home = ''


class ConvertAction(enum.Enum):
    """Enum class to Convert Action
    Args:
        enum (str): Enum Action
    """
    PDF_TO_JSON = "PdfToJson"
    PDF_TO_TXT = "PdfToText"
    PDF_TO_IMAGE = "PdfToImg"
    PDF_TO_MULTIPDF = "PdfToMultiPdf"
    PDF_TO_TEXT_BBOX = "PdfToTextBbox"
    PDF_TO_IMAGE_BBOX = "PdfToImageBbox"
    ROTATE_PDF_PAGE = "RotatePdfPage"
    IMG_TO_PDF = "ImgToPdf"
    PLOT_BBOX = "PlotBbox"


class FormatConverter:
    """Class to convert document format.
    """
    @classmethod
    def execute(cls, from_file, convert_action=ConvertAction.PDF_TO_JSON,
                config_param_dict: CONFIG_PARAM_DICT = None):
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
            config_param_dict, CONFIG_PARAM_DICT)
        run_command = ['java', '-jar', cls.__get_tool_path(),
                       convert_action.value, '--fromfile', from_file]

        if config_param_dict["to_dir"]:
            run_command += ["--todir", config_param_dict["to_dir"]]
        if config_param_dict["hocr_file"]:
            run_command += ["--hocrfile", config_param_dict["hocr_file"]]
        if config_param_dict["water_mark"]:
            run_command += ["--watermarktext", config_param_dict["water_mark"]]
        if config_param_dict["dpi"]:
            run_command += ["--dpi", str(config_param_dict["dpi"])]
        if config_param_dict["saveresource"]:
            run_command += ["--saveresource",
                            str(config_param_dict["saveresource"])]
        if config_param_dict["plotbbox"]:
            run_command += ["--plotbbox", str(config_param_dict["plotbbox"])]
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

        if convert_action in [ConvertAction.PDF_TO_JSON]:
            return json.loads(stdout), None
        elif convert_action in [ConvertAction.PDF_TO_TEXT_BBOX]:
            return stdout.strip().split('\n'), None
        elif convert_action in [ConvertAction.PDF_TO_IMAGE, ConvertAction.PDF_TO_MULTIPDF,
                                ConvertAction.ROTATE_PDF_PAGE]:
            return stdout.strip().split('\n'), None
        else:
            return stdout, None

    @classmethod
    def __get_tool_path(cls):
        JAR_FILE_FORMAT = "infy-format-converter-*.jar"
        tool_path = str(
            f"{format_converter_jar_home}/{JAR_FILE_FORMAT}")
        format_convert_jars = glob.glob(tool_path)
        if format_convert_jars:
            tool_path = str(Path(format_convert_jars[0]).resolve())
        else:
            raise Exception(
                f"Could not find any jar file of format '{JAR_FILE_FORMAT}' at provided path '{format_converter_jar_home}'")
        return tool_path

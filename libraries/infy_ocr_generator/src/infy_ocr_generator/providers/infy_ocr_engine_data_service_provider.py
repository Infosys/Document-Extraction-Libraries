# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import os
import glob
import traceback
import logging
import copy
from pathlib import Path
import subprocess
import imageio
from infy_ocr_generator.interface.data_service_provider_interface import (
    GENERATE_API_RES_STRUCTURE, DataServiceProviderInterface,
    DOC_DATA)

JAR_GENERAL_ERROR_MSG = 'Error occurred in main method'
ocr_engine_jar_home = ''


class OcrConstants():
    """Constant class"""
    MAX_INT16 = 32767


CONFIG_PARAMS_DICT = {
    'ocr_engine': {
        'exe_dir_path': '',
        'model_dir_path': '',
        'ocr_format': '',  # hocr or txt
        'lang': 'eng'
    }
}


class InfyOcrEngineDataServiceProvider(DataServiceProviderInterface):
    """Implementation of DataServiceProvider for Tesseract 5"""

    def __init__(self, config_params_dict: CONFIG_PARAMS_DICT,
                 output_dir: str = None,
                 output_to_supporting_folder: bool = False,
                 overwrite: bool = False,
                 logger: logging.Logger = None,
                 log_level: int = None):
        """Creates an instance of Tesseract Ocr Data Service Provider

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
        Example:
            >>> import logging
            >>> logging.disable(logging.CRITICAL)
            >>> import os
            >>> CONFIG_PARAMS_DICT = {
            ...     "ocr_engine": {
            ...         "exe_dir_path": "C:/MyProgramFiles/InfyOcrEngine",
            ...         "model_dir_path": "C:/MyProgramFiles/AI/models/tessdata",
            ...         "ocr_format": "hocr",
            ...         "lang": "eng"
            ...     }
            ... }
            >>> provider = InfyOcrEngineDataServiceProvider(config_params_dict=CONFIG_PARAMS_DICT)
            >>> logging.disable(logging.NOTSET)
        """

        super(InfyOcrEngineDataServiceProvider,
              self).__init__(logger, log_level)
        global ocr_engine_jar_home
        self.config_params_dict = self.get_updated_config_dict(
            config_params_dict['ocr_engine'], CONFIG_PARAMS_DICT['ocr_engine'])
        if output_dir and not os.path.exists(output_dir):
            raise FileNotFoundError(f"{output_dir} not found")
        self.output_dir = output_dir
        self.output_to_supporting_folder = output_to_supporting_folder
        self.overwrite = overwrite

        if self.config_params_dict["exe_dir_path"]:
            ocr_engine_jar_home = self.config_params_dict["exe_dir_path"]

    def submit_request(self, doc_data_list: [DOC_DATA]) -> list:
        """API to submit tesseract ocr data service request for asynchorouns call

        Args:
            doc_data_list ([DOC_DATA]): List of input documents. e.g, ['c:/1.jpg','c:/1.pdf']

        Raises:
            NotImplementedError: Raises an error if the method is not implemented

        Returns:
            list: [SUB_RE_API_STRUCTURE]
        Example:
            >>> import logging
            >>> logging.disable(logging.CRITICAL)
            >>> import os
            >>> CONFIG_PARAMS_DICT = {
            ...     "ocr_engine": {
            ...         "exe_dir_path": "C:/MyProgramFiles/InfyOcrEngine",
            ...         "model_dir_path": "C:/MyProgramFiles/AI/models/tessdata",
            ...         "ocr_format": "hocr",
            ...         "lang": "eng"
            ...     }
            ... }
            >>> provider = InfyOcrEngineDataServiceProvider(config_params_dict=CONFIG_PARAMS_DICT)
            >>> provider.submit_request(['./data/sample_1.png'])
            Traceback (most recent call last):
            ...
            NotImplementedError
            >>> logging.disable(logging.NOTSET)
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
        Example:
            >>> import logging
            >>> logging.disable(logging.CRITICAL)
            >>> import os
            >>> CONFIG_PARAMS_DICT = {
            ...     "ocr_engine": {
            ...         "exe_dir_path": "C:/MyProgramFiles/InfyOcrEngine",
            ...         "model_dir_path": "C:/MyProgramFiles/AI/models/tessdata",
            ...         "ocr_format": "hocr",
            ...         "lang": "eng"
            ...     }
            ... }
            >>> provider = InfyOcrEngineDataServiceProvider(config_params_dict=CONFIG_PARAMS_DICT)
            >>> provider.receive_response([])
            Traceback (most recent call last):
            ...
            NotImplementedError
            >>> logging.disable(logging.NOTSET)
        """
        raise NotImplementedError

    def generate(self, doc_data_list: [DOC_DATA] = None, api_response_list: list = None) \
            -> [GENERATE_API_RES_STRUCTURE]:
        """API to generate OCR based on OCR provider given

        Args:
            doc_data_list ([DOC_DATA], optional): Use these input files to
                -implement technique and generate output files. Defaults to None.
            api_response_list (list, optional): API response will be generated into output file. Defaults to None.

        Returns:
            list: List of generated ocr file path.
        Example:
            >>> import logging
            >>> logging.disable(logging.CRITICAL)
            >>> import os
            >>> CONFIG_PARAMS_DICT = {
            ...     "ocr_engine": {
            ...         "exe_dir_path": "C:/MyProgramFiles/InfyOcrEngine",
            ...         "model_dir_path": "C:/MyProgramFiles/AI/models/tessdata",
            ...         "ocr_format": "hocr",
            ...         "lang": "eng"
            ...     }
            ... }
            >>> provider = InfyOcrEngineDataServiceProvider(config_params_dict=CONFIG_PARAMS_DICT)
            >>> doc_data_list = [{'doc_path': './data/sample_1.png', 'pages': '1'}]
            >>> provider.generate(doc_data_list)  # doctest: +ELLIPSIS
            [{'input_doc': './data/sample_1.png', 'output_doc': './data/sample_1.png.hocr', 'error': ''}]
            >>> logging.disable(logging.NOTSET)
        """
        def _call_exe(img_file, model_dir_path, ocr_format, lang, output_dir):
            run_command = ['java', '-jar', _get_tool_path(),
                           '--fromfile', img_file, '--modeldir', model_dir_path,
                           '--ocrformat', ocr_format, '--lang', lang
                           ]
            if output_dir:
                run_command.extend(['--todir', output_dir])

            sub_process = subprocess.Popen(
                run_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            stdout, stderr = sub_process.communicate()
            if (not stdout and stderr) or (JAR_GENERAL_ERROR_MSG in stdout):
                logger = logging.getLogger(os.path.basename(__file__))
                logger.error(stderr)
                return None, stderr

            return stdout, None

        def _get_tool_path():
            JAR_FILE_FORMAT = "infy-ocr-engine-*.jar"
            tool_path = str(
                f"{ocr_engine_jar_home}/{JAR_FILE_FORMAT}")
            ocr_engine_jars = glob.glob(tool_path)
            ocr_engine_jars.sort(reverse=True)
            if ocr_engine_jars:
                tool_path = str(Path(ocr_engine_jars[0]).resolve())
            else:
                raise Exception(
                    f"Could not find any jar file of format '{JAR_FILE_FORMAT}' at provided path '{ocr_engine_jar_home}'")
            return tool_path

        def _call_infy_ocr_engine(in_doc_obj):
            gen_res_dict = copy.deepcopy(GENERATE_API_RES_STRUCTURE)
            img_file = in_doc_obj['doc_path']
            gen_res_dict['input_doc'] = img_file
            _image = imageio.imread(img_file)

            if (_image.shape[0] > OcrConstants.MAX_INT16 or _image.shape[1] > OcrConstants.MAX_INT16):
                error = f"Image too large: ({_image.shape[1]},{_image.shape[0]}). The max width and"
                error += f"height of image size should be ({OcrConstants.MAX_INT16},{OcrConstants.MAX_INT16})"
                gen_res_dict['error'] = error
                return gen_res_dict

            ocr_format = self.config_params_dict['ocr_format']

            output_doc = self.get_output_file(
                img_file, self.output_dir, self.output_to_supporting_folder,
                suffix=f'.{ocr_format}')

            gen_res_dict['output_doc'] = output_doc
            if not self.overwrite and os.path.exists(output_doc):
                return gen_res_dict
            model_dir_path = self.config_params_dict['model_dir_path']
            ocr_format = self.config_params_dict['ocr_format']
            lang = self.config_params_dict['lang']
            ocr_data, _ = _call_exe(
                img_file, model_dir_path, ocr_format, lang, self.output_dir)
            output_doc = ocr_data.split('\n', maxsplit=1)[0]
            if os.path.normpath(gen_res_dict['output_doc']) != os.path.normpath(output_doc):
                error = 'Expected path and actual path generated by tool are different.'
                error += f'Expected: {gen_res_dict["output_doc"]}, Actual: {output_doc}'
                gen_res_dict['error'] = error
                gen_res_dict['output_doc'] = output_doc

            return gen_res_dict

        if len(doc_data_list) == 0:
            raise Exception("Valid doc_data_list arg is required")
        ocr_list = []

        for in_doc_obj in doc_data_list:
            try:
                ocr_list.append(_call_infy_ocr_engine(in_doc_obj))
            except Exception:
                full_trace_error = traceback.format_exc()
                self.logger.error(full_trace_error)
                gen_res_dict = copy.deepcopy(GENERATE_API_RES_STRUCTURE)
                gen_res_dict['error'] = full_trace_error
                ocr_list.append(gen_res_dict)

        return ocr_list

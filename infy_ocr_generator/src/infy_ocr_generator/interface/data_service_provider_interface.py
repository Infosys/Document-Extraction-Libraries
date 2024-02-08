# ===============================================================================================================#
#
# Copyright 2021 Infosys Ltd.
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at
# http://www.apache.org/licenses/
#
# ===============================================================================================================#

import os
import abc
import logging
import sys
import datetime
import getpass
import socket
import time
import copy
import json
import imageio

SUB_RE_API_STRUCTURE = {
    "input_doc": '',
    "submit_api": {
        "query_params": {},
        "response": {}
    },
    "receive_api": {
        "response": {}
    },
    "error": None
}

GENERATE_API_RES_STRUCTURE = {
    'input_doc': '',
    'output_doc': '',
    'error': ''
}

DOC_DATA = {
    'doc_path': '',
    'pages': ''
}

RESCALE_DATA = {
    'doc_page_num': '',
    'doc_page_width': 0,
    'doc_page_height': 0,
    'doc_file_path': '',
    'doc_file_extension': 'jpg'
}


class DataServiceProviderInterface(metaclass=abc.ABCMeta):
    """Interface class"""
    @ classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'generate') and
                callable(subclass.generate) and
                hasattr(subclass, 'submit_request') and
                callable(subclass.submit_request) and
                hasattr(subclass, 'receive_response') and
                callable(subclass.receive_response) or
                NotImplemented)

    def __init__(self, logger: logging.Logger = None,
                 log_level: int = None):
        """constructor

        Args:
            logger (logging.Logger, optional): logger object. Defaults to None.
            log_level (int, optional): log level. Defaults to None.
        """
        self.__set_logger(logger, log_level)
        self.__init_api_logger()

    @ abc.abstractmethod
    def submit_request(self, doc_data_list: [DOC_DATA]) -> [SUB_RE_API_STRUCTURE]:
        """API to submit request for asynchorouns call

        Args:
            doc_data_list ([DOC_DATA]): List of input documents. e.g, ['c:/1.jpg','c:/1.pdf']

        Raises:
            NotImplementedError: Raises an error if the method is not implemented

        Returns:
            [SUB_RE_API_STRUCTURE]: List of dictionary
        """
        raise NotImplementedError

    @ abc.abstractmethod
    def receive_response(self, submit_req_response_list: [SUB_RE_API_STRUCTURE],
                         rerun_unsucceeded_mode: bool = False) -> [SUB_RE_API_STRUCTURE]:
        """API to Received response of asynchorouns call submit request

        Args:
            submit_req_response_list ([SUB_RE_API_STRUCTURE]): Response structure of `submit_request` api
            rerun_unsucceeded_mode (bool, optional): Enabling this mode and passing same request
             -will rerun for unsuccessful call. Defaults to False.

        Raises:
            NotImplementedError: Raises an error if the method is not implemented

        Returns:
            [SUB_RE_API_STRUCTURE]: List of dictionary
        """
        raise NotImplementedError

    @ abc.abstractmethod
    def generate(self, doc_data_list: [DOC_DATA] = None,
                 api_response_list: list = None) -> [GENERATE_API_RES_STRUCTURE]:
        """API to generate OCR based on OCR provider given

        Args:
            doc_data_list ([DOC_DATA], optional): Use these input files to
                -implement technique and generate output files. Defaults to None.
            api_response_list (list, optional): API response will be generated into output file. Defaults to None.

        Raises:
            NotImplementedError: Raises an error if the method is not implemented

        Returns:
            [GENERATE_API_RES_STRUCTURE]: List of generated ocr file path.
        """
        raise NotImplementedError

    def get_updated_config_dict(self, from_dict: dict, default_dict: str) -> dict:
        """Method to update default value into user given config dict.

        Args:
            from_dict (dict): User given config.
            default_dict (dict): Default dict configured at provider level.

        Returns:
            dict: Returns updated user config dict with default values
        """
        config_dict_temp = copy.deepcopy(default_dict)
        for key in from_dict:
            if isinstance(from_dict[key], dict):
                config_dict_temp[key] = self.get_updated_config_dict(
                    from_dict[key], config_dict_temp[key])
            else:
                config_dict_temp[key] = from_dict[key]
        return config_dict_temp

    def set_api_log(self, api: str, pretty_print=True):
        """API to write external api details into log

        Args:
            api (str): Target API name.
            pretty_print (bool, optional): Pretty printing API Log. Defaults to True.
        """
        self.__api_logger.info(api, extra={'pretty_print': pretty_print})

    def get_output_file(self, in_doc: str, output_dir: str,
                        output_to_supporting_folder: bool,
                        pages: str = '',
                        suffix: str = '.txt') -> str:
        """Method to derive output file path.

        Args:
            in_doc (str): input file path.
            output_dir (str): provided output directory.
            output_to_supporting_folder (bool): Flag to generate file in
                - supporting folder. e.g, *_files/1.txt
            pages (str, optional): Array string of pages provided in request.
                - Defaults to ''.
            suffix (str, optional): Output file suffix name with extension.
                - Defaults to '.txt'.

        Returns:
            str: derived output file path.
        """
        file_name = os.path.basename(in_doc)
        output_doc = in_doc
        if output_dir:
            output_doc = f"{output_dir}/{file_name}"
        if output_to_supporting_folder:
            output_doc = f"{output_doc}_files"
            try:
                os.makedirs(output_doc)
            except Exception:
                pass
            output_doc = f"{output_doc}/{file_name}"
        # only to pdf add given pages in filename
        pages = f"[{pages}]" if pages and in_doc.lower().endswith(
            '.pdf') else ""
        return f"{output_doc}{pages}{suffix}"

    def get_image_details(self, img_path: str) -> dict:
        """Returns image details

        Args:
            img_path (str): Image full file path.

        Returns:
            dict: Returns dictinary containing image information.
        """
        detail_dict = {
            'dpi': 0,
            'width': 0,
            'height': 0
        }
        try:
            img_obj = imageio.imread(img_path)
            (h, w) = img_obj.shape[:2]
            detail_dict['width'] = w
            detail_dict['height'] = h
            detail_dict['dpi'] = img_obj.meta.get('dpi', (0, 0))[0]
        except Exception as e:
            self.logger.error(e)
        return detail_dict

    def __set_logger(self, logger, log_level):
        self.logger = logger
        LOG_FORMAT = logging.Formatter(
            '%(asctime)s.%(msecs)03d %(levelname)s [%(threadName)s] [%(module)s] [%(funcName)s:%(lineno)d] %(message)s')
        if logger is None:
            log_level = logging.INFO if log_level is None else log_level
            self.logger = logging.getLogger(__name__)
            self.logger.setLevel(log_level)
            # Add sysout hander
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(log_level)
            console_handler.setFormatter(LOG_FORMAT)
            self.logger.addHandler(console_handler)
            self.logger.info('log initialized')
        else:
            hndlr = self.logger.handlers[0]
            hndlr.setFormatter(LOG_FORMAT)
            self.logger.info('Formatter updated')

    def __init_api_logger(self):
        class MyApiLogFormatter(logging.Formatter):
            """Custom API Log Formatter"""

            def format(self, record):
                host_name = socket.gethostname()
                api_log = {
                    "timestamp": str(datetime.datetime.now()),
                    "user_name": getpass.getuser(),
                    "host_name": host_name,
                    "host_ip": socket.gethostbyname(host_name),
                    "target_api": super().format(record)
                }

                kwargs = {}
                if record.pretty_print:
                    kwargs['indent'] = 2
                resp = json.dumps(api_log, **kwargs)
                return resp
        log_file_path = "./logs"
        log_file_prefix = "api_call_log"
        try:
            if not os.path.isdir(log_file_path):
                os.makedirs(log_file_path)
        except Exception:
            pass
        timestr = time.strftime("%Y%m%d")
        log_file_name = f"{log_file_path}/{log_file_prefix}_{timestr}.json"
        json_handler = logging.FileHandler(filename=log_file_name)
        json_handler.setFormatter(MyApiLogFormatter())

        self.__api_logger = logging.getLogger('api_call_log')
        self.__api_logger.addHandler(json_handler)
        self.__api_logger.setLevel(logging.INFO)

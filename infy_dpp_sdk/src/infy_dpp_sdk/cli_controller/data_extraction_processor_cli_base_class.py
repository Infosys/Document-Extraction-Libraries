# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import argparse
import base64
import json
from abc import ABC, abstractmethod
import zlib

from ..common.infy_json_encoder import InfyJSONEncoder
from ..data.document_data import DocumentData
from ..interface.i_processor import IProcessor
from ..common.processor_factory import ProcessorFactory

# TODO - Mohan - Verify if this class is required


class ProcessorCliArgs(object):
    def __init__(self, document_data: DocumentData, context_data: dict,
                 config_data: dict, processor_name: str = None, processor_version: str = None):
        self.document_data = DocumentData(**document_data)
        self.context_data = context_data
        self.config_data = config_data
        self.processor_name = processor_name
        self.processor_version = processor_version


class ProcessorData(object):
    processor_module_name: str = None
    processor_package: str = None

    def __init__(self) -> None:
        self.processor_module_name: str = None
        self.processor_package: str = None


class DataExtractionProcessorCliBaseClass(ABC):
    """
    The Abstract Class defines a template method that contains a skeleton of
    some algorithm, composed of calls to (usually) abstract primitive
    operations.

    Concrete subclasses should implement these operations, but leave the
    template method itself intact.
    """

    def execute_main(self) -> None:
        """template method"""
        STATUS_CDE = 1
        args = self.decode_args(self.parse_args())
        processor_data = ProcessorData()
        processor_data.processor_module_name = f"{args.processor_name}_{args.processor_version}"
        self.set_processor_to_execute(processor_data, args)
        self.__validate_processor_to_execute(processor_data)
        processor_obj: IProcessor = self.get_processor_instance(processor_data)
        response_dict = processor_obj.do_execute(
            args.document_data, args.context_data, args.config_data)
        if response_dict:
            STATUS_CDE = 0
        print(self.encode_data_model(response_dict))
        exit(STATUS_CDE)

    # ------------------------abstractmethod---------------------------
    # These operations have to be implemented in subclasses.
    @abstractmethod
    def set_processor_to_execute(self, processor_data: ProcessorData, args: ProcessorCliArgs) -> None:
        """The developer should override this method to set the processor data for the `package` and `module name`(optional) of the
        processor that is to be executed using cli arguments.

        For example:
            processor_data.processor_module_name = f"{args.processor_name}_{args.processor_version}"
            processor_data.processor_package = f"provider.processor.{args.processor_name}"

        Args:
            args (ProcessorCliArgs): cli arguments
            processor_data (ProcessorData): executable processor data

        Raises:
            NotImplementedError
        """

        raise NotImplementedError

    # ------------------------private methods---------------------------
    def __validate_processor_to_execute(self, processor_data: ProcessorData):
        if not processor_data.processor_module_name:
            raise Exception("`processor_module_name` should not be empty")

    # ------------------------public methods---------------------------
    def get_processor_instance(self, processor_data: ProcessorData) -> object:
        processor_class = ProcessorFactory().get_processor_class(
            processor_data.processor_module_name, processor_data.processor_package)
        return processor_class()

    def parse_args(self):
        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers()
        # create the parser for the "command_1" command
        parser_a = subparsers.add_parser('input_file')
        parser_a.add_argument(
            '--json_filepath', help='Filepath of processor input_param data', required=True)
        # create the parser for the "command_2" command
        parser_b = subparsers.add_parser('input_param')
        parser_b.add_argument(
            '--document_data', help='Document Data', required=True)
        parser_b.add_argument(
            '--context_data', help='Context Data', required=True)
        parser_b.add_argument(
            '--config_data', help='Processor Config Data', required=True)
        parser_b.add_argument(
            '--processor_name', help='Processor name', default=None)
        parser_b.add_argument(
            '--processor_version', help='Processor version', default=None)
        args = parser.parse_args()
        return args

    def decode_args(self, args):
        def _read_file(json_filepath):
            data = {}
            with open(json_filepath, 'r', encoding="utf-8") as f:
                data = json.load(f)
            return data

        def _decode(encoded_str):
            try:
                base64_decoded = base64.b64decode(encoded_str)
                decompressed = zlib.decompress(base64_decoded).decode()
                decoded = json.loads(json.loads(decompressed))
                return decoded
            except Exception:
                return encoded_str
        if vars(args).get("json_filepath"):
            arg_dict = _read_file(args.json_filepath)
            args = ProcessorCliArgs(_decode(arg_dict["document_data"]), _decode(arg_dict["context_data"]),
                                    _decode(arg_dict["config_data"]), arg_dict.get("processor_name"), arg_dict.get("processor_version"))
        else:
            args = ProcessorCliArgs(_decode(args.document_data), _decode(args.context_data),
                                    _decode(args.config_data), args.processor_name, args.processor_version)
        return args

    def encode_data_model(self, data):
        json_str = json.dumps(InfyJSONEncoder().encode(data))
        return base64.b64encode(json_str.encode("utf-8")).decode()

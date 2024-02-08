# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import json
import platform
import tempfile

import infy_dpp_sdk

from ...data.config_param_data import ConfigParamData
from ...data.context_data import ContextData
from ...data.document_data import DocumentData
from ...data.processor_response_data import ProcessorResponseData
from ...interface.i_orchestrator_cli import MAX_CLI_LIMIT, IOrchestratorCli
from ..common.extraction_util import ExtractionUtil


class OrchestratorCliBasic(IOrchestratorCli):
    """Orchestrator Cli Implementation class"""

    def __init__(self, config_param_data: ConfigParamData, debug_mode: bool = False):
        self.processor_config_factory = infy_dpp_sdk.common.ConfigDataFactory(
            config_param_data.processor_config_filepath)
        self.processor_src_map_config_factory = infy_dpp_sdk.common.ConfigDataFactory(
            config_param_data.processor_src_mapping_config_filepath)
        self.debug_mode = debug_mode
        super().__init__(config_param_data, debug_mode)

    def execute_processor(self, processor_name: str, processor_version: str,
                          document_data: DocumentData, context_data: ContextData) -> (ProcessorResponseData, str):
        return_value, error = ExtractionUtil.run_command(self.__get_run_command(
            processor_name, processor_version, document_data, context_data))
        if "warning" in error:
            print("[processor] - [warning] - ", error)
        elif error:
            print("[processor] - [error] - ", error)
        if "too Long" in error:
            return None, error
        decorded_return_json = ExtractionUtil.decode_data(return_value)
        if self.debug_mode:
            print("[processor] - [return_value] - ", return_value)
            print("\n")
            print("[processor] - [decorded_return_json] - ",
                  decorded_return_json)

        decoded_return_value = infy_dpp_sdk.data.ProcessorResponseData(
            **decorded_return_json)
        return decoded_return_value, error

    def __get_run_command(self, processor_name, processor_version, document_data, context_data):
        try:
            processor_src_map_data = self.processor_src_map_config_factory.get_config_data(
                processor_name)
            run_command = f'cd {processor_src_map_data["processor_home_dir"]} '
            if processor_src_map_data.get("venv_script_dir"):
                run_command += f'&& cd {processor_src_map_data["venv_script_dir"]} '
                run_command += '&& activate ' if platform.system().lower() == 'windows' else '&& source ./activate '
            run_command += f'&& cd {processor_src_map_data["cli_controller_dir"]} '
            run_command += f'&& python {processor_src_map_data["cli_controller_file"]} '
            # ---- Processor Args
            processor_cli_req_dict = self.__get_processor_request(processor_name, processor_version, document_data,
                                                                  context_data, processor_src_map_data)
            run_command_temp = run_command+'input_param '
            for k, v in processor_cli_req_dict.items():
                run_command_temp += f'--{k} {v} '

            # ---- If `run_command` length is greater than `max_cli_limit` then convert `input_param` as `input_file`
            if len(run_command_temp) > MAX_CLI_LIMIT:
                # TODO: verify in docker run
                temp_request_filepath = f"{tempfile.mkdtemp()}/{processor_name}.json"
                with open(temp_request_filepath, 'w', encoding='utf-8') as f:
                    json.dump(processor_cli_req_dict, f, indent=4)

                run_command += 'input_file '
                run_command += f'--json_filepath  {temp_request_filepath} '
            else:
                run_command = run_command_temp

            if self.debug_mode:
                print(run_command)
        except Exception as e:
            print(e)
        return run_command

    def __get_processor_request(self, processor_name, processor_version, document_data,
                                context_data, processor_src_map_data):
        config_data = self.processor_config_factory.get_config_data(
            processor_src_map_data["config_file_namespace"])
        request_dict = {"processor_name": processor_name,
                        "processor_version": processor_version,
                        "document_data": ExtractionUtil.compress_data(document_data),
                        "context_data": ExtractionUtil.compress_data(context_data),
                        "config_data": ExtractionUtil.compress_data(config_data)}
        return request_dict

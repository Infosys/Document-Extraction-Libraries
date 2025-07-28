# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

from ._internal.b_orchestrator import BOrchestrator
from ._operator.cli_operator import CLIOperator
from ._operator.http_operator import HTTPOperator
from ._operator.native_operator import NativeOperator


class OrchestratorHybrid(BOrchestrator):
    """Orchestrator that invokes processors using CLI or HTTP or both."""
    __INVOCATION_MODE_CLI = "cli"
    __INVOCATION_MODE_HTTP = "http"
    __INVOCATION_MODE_NATIVE = "native"

    def execute_processor(self, processor_input_config_data: dict,
                          processor_deployment_config_data: dict,
                          orchestrator_config_data: dict) -> dict:
        """
        Execute a processor.

        Args:
            processor_input_config_data (dict): Input configuration data for the processor.
            processor_deployment_config_data (dict): Deployment configuration data for the processor.
            orchestrator_config_data (dict): Configuration data for the orchestrator.

        Returns:
            dict: Result of the processor execution.
        """
        result = None
        invocation_mode = self.__get_processor_invocation_mode(
            processor_input_config_data, orchestrator_config_data)
        if invocation_mode == self.__INVOCATION_MODE_CLI:
            result = CLIOperator().execute_processor(processor_deployment_config_data)
        elif invocation_mode == self.__INVOCATION_MODE_HTTP:
            result = HTTPOperator().execute_processor(processor_deployment_config_data)
        elif invocation_mode == self.__INVOCATION_MODE_NATIVE:
            result = NativeOperator().execute_processor(processor_deployment_config_data,
                                                        processor_input_config_data)
        else:
            raise ValueError(
                f"Invalid invocation mode - {invocation_mode} for processor - {processor_input_config_data.get('processor_name')}")
        return result

    def __get_processor_invocation_mode(self, processor_input_config_data: dict,
                                        orchestrator_config_data: dict) -> str:
        """
        Get the invocation mode for the processor.

        Args:
            processor_input_config_data (dict): Input configuration data for the processor.
            orchestrator_config_data (dict): Configuration data for the orchestrator.

        Returns:
            str: Invocation mode for the processor.
        """
        processor_invocation_config_data = orchestrator_config_data.get(
            'processor_invocation', {})
        default_mode = processor_invocation_config_data.get(
            'default_mode', self.__INVOCATION_MODE_NATIVE)
        processor_name_invocation_mode_dict = {}
        for mode_name, mode_value_dict in processor_invocation_config_data.get(
                'custom_mode', {}).items():
            for processor_name in mode_value_dict['processor_names']:
                processor_name_invocation_mode_dict[processor_name] = mode_name

        return processor_name_invocation_mode_dict.get(
            processor_input_config_data.get('processor_name'), default_mode).lower()

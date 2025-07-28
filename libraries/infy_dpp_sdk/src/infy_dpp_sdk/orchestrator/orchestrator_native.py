# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

from ._internal.b_orchestrator import BOrchestrator
from ._operator.native_operator import NativeOperator


class OrchestratorNative(BOrchestrator):
    """Orchestrator that invokes processors natively."""

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
        return NativeOperator().execute_processor(processor_deployment_config_data,
                                                  processor_input_config_data)

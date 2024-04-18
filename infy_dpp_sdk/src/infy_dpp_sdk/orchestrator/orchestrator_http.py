# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#


from .b_orchestrator import BOrchestrator
from .operator.http_operator import HTTPOperator


class OrchestratorHTTP(BOrchestrator):
    """Orchestrator using HTTP"""

    def execute_processor(self, processor_input_config_data: dict,
                          processor_deployment_config_data: dict,
                          orchestrator_config_data: dict):
        """Execute a processor"""
        return HTTPOperator().execute_processor(processor_deployment_config_data)

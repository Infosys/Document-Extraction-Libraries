# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                   #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

from abc import ABC, abstractmethod


class IOrchestratorCli(ABC):
    """Orchestrator Interface for CLI execution"""

    @abstractmethod
    def run_batch(self, context_data: dict = None):
        """Run the pipeline"""
        raise NotImplementedError("run_batch not implemented")

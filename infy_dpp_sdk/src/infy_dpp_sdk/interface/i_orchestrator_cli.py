# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

from abc import ABC, abstractmethod

from ..data.config_param_data import ConfigParamData
from ..data.context_data import ContextData
from ..data.document_data import DocumentData

MAX_CLI_LIMIT: int = 8000


class IOrchestratorCli(ABC):

    def __init__(self, config_param_data: ConfigParamData, debug_mode: bool = False):
        pass

    @abstractmethod
    def execute_processor(self, processor_name: str, processor_version: str,
                          document_data: DocumentData, context_data: ContextData):
        raise NotImplementedError("execute_processor not implemented")

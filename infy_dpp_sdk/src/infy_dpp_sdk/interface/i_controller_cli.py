# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

from abc import ABC, abstractmethod
from ..data import (ControllerRequestData, ControllerResponseData)


class IControllerCLI(ABC):
    """Interface for executing processor(s) when orchestrator makes CLI calls."""

    @abstractmethod
    def receive_request(self) -> ControllerRequestData:
        """Receive the request data from caller."""
        raise NotImplementedError

    @abstractmethod
    def send_response(self, controller_response_data: ControllerResponseData) -> any:
        """Send the response data back to the caller."""
        raise NotImplementedError

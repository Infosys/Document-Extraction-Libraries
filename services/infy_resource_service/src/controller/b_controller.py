# ===============================================================================================================#
# Copyright 2025 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

from abc import ABC
import fastapi


class BController(ABC):
    """Base class for all controllers."""

    def __init__(self, context_root_path: str, controller_path: str):
        """Create instance of controller."""
        print('Controller created')
        self.__router = fastapi.APIRouter(
            prefix=context_root_path + controller_path)

    def get_router(self):
        """Get instance of router."""
        return self.__router

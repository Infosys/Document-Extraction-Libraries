# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

from abc import ABC, abstractmethod


class RuleDataBaseClass(ABC):
    def __init__(self) -> None:
        pass

    @abstractmethod
    def do_process(self, json_match_data: list) -> any:
        pass

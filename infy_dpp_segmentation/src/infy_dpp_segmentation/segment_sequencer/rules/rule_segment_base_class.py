# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                   #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

from abc import ABC, abstractmethod


class RuleSegmentBaseClass(ABC):
    def __init__(self) -> None:
        super().__init__()

    def template_method(self, segment_data_list: list, pages, page):
        updated_segment_data_list = self.generate_sequence_no(
            segment_data_list, pages, page)
        return updated_segment_data_list

    @abstractmethod
    def generate_sequence_no(self, segment_data_list: list, pages, page) -> list:
        raise NotImplementedError

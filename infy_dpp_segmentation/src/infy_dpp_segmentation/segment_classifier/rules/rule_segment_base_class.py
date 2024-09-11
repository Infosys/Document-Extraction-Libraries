# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                   #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

from abc import ABC, abstractmethod


class RuleSegmentBaseClass(ABC):
    def template_method(self, segment_data_list: list, header: object, footer: object, ocr_file_path_list: list):
        updated_segment_data_list = self.classify_segment(
            segment_data_list, header, footer, ocr_file_path_list)
        return updated_segment_data_list

    @abstractmethod
    def classify_segment(self, segment_data_list: list, header: object, footer: object, ocr_file_path_list: list) -> list:
        raise NotImplementedError
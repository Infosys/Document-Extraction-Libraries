# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                   #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

from abc import ABC, abstractmethod


class RuleSegmentBaseClass(ABC):
    def __init__(self) -> None:
        super().__init__()

    def template_method(self, segment_data_list: list, page_list: list, exclude_types_list: list, resources_file_path: str, chunking_method: str, config: object):

        self.pre_hook_page_list(page_list, exclude_types_list)
        output_data_dict = self.group_segment_data(
            segment_data_list, resources_file_path, chunking_method, config)
        return output_data_dict

    @abstractmethod
    def group_segment_data(self, segment_data_list: list, resources_file_path: str, chunking_method: str, config: object) -> dict:
        raise NotImplementedError
    # ------------------------hooks---------------------------
    # These are "hooks." Subclasses may override them.

    def pre_hook_page_list(self, page_list: list, exclude_types_list: list):
        pass
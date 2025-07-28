# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#
from .rule_data_base_class import RuleDataBaseClass


class RuleCus001TransformBboxValue(RuleDataBaseClass):

    def do_process(self, json_match_data: any) -> any:
        x1, y1, x2, y2 = json_match_data
        w, h = x2 - x1, y2 - y1
        return [x1, y1, w, h]

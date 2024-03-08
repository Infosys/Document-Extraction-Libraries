# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                   #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import uuid
from importlib import import_module

class CommonUtil:

    @classmethod
    def get_uuid(cls):
        return str(uuid.uuid4())

    @classmethod
    def get_rule_class_instance(cls, rc_module_name: str, rc_entity_name: str = None):

        # rc_module_name = reduce(lambda x, y: x + ('_' if y.isupper()
        #                                           else '') + y, rc_module_name).lower()
        rc_name = "".join([str(x).title() for x in rc_module_name.split('_')])
        if rc_entity_name:
            rule_mudule = import_module(
                f"infy_dpp_core.document_data_updater.rules.{rc_entity_name}.{rc_module_name}")
        else:
            rule_mudule = import_module(f"infy_dpp_core.document_data_updater.rules.{rc_module_name}")
        rule_class = getattr(rule_mudule, rc_name)

        return rule_class
# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

from importlib import import_module


class ProcessorFactory:
    def get_processor_class(self, module_name: str, package: str = None):
        """It dynamically imports the given `module_name` and returns the class.
        For more information, please refer
            - https://docs.python.org/3/library/importlib.html#importlib.import_module
            - https://packaging.python.org/en/latest/guides/packaging-namespace-packages/


        Args:
            module_name (str): module name. e.g, processor_factory.py
            package (str, optional): Package of module, if any. e.g, infy_dpp_sdk.common
        """

        m_class_name = "".join([str(x).title()
                                for x in module_name.split('_')])
        found_modules = import_module(
            f"{package}.{module_name}" if package else module_name)
        found_class = getattr(found_modules, m_class_name)

        return found_class

# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

class DependencyUtil:
    
    @classmethod
    def is_module_installed(cls, module_name):
        try:
            __import__(module_name)
        except ModuleNotFoundError:
            raise Exception(f"{module_name} is not installed.")

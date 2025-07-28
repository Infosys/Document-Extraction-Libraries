# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

from pydantic import BaseModel


class ConfigParamData(BaseModel):
    """Configuration parameter data class"""
    processor_config_filepath: str | None = None
    processor_src_mapping_config_filepath: str | None = None

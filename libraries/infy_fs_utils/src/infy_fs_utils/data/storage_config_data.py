# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

from pydantic import BaseModel


class StorageConfigData(BaseModel):
    """Storage configuration data"""
    storage_root_uri: str = None
    storage_server_url: str = None
    storage_access_key: str = None
    storage_secret_key: str = None

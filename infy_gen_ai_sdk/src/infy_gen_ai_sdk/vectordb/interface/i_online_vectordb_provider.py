# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

"""Module for Online Vector Db provider interface"""

import abc
from ...schema.vector_db_data import OnlineVectorDbConfigData , BaseVectorDbRecordData, BaseVectorDbQueryParamsData


class IOnlineVectorDbProvider(metaclass=abc.ABCMeta):
    """Interface class for Vector Db provider"""

    def __init__(self, online_vector_config_data: OnlineVectorDbConfigData) -> None:
        pass

    @abc.abstractmethod
    def get_matches(self, query_params_data: BaseVectorDbQueryParamsData):
        """Returns matches for given `query` from vector Db"""
        raise NotImplementedError

    @abc.abstractmethod
    def save_record(self, db_record_data: BaseVectorDbRecordData):
        """Saves a record to vector Db"""
        raise NotImplementedError

    @abc.abstractmethod
    def get_records(self):
        """Get all records from vector dB"""
        raise NotImplementedError

    @abc.abstractmethod
    def delete_records(self):
        """Delete specific records from vector dB"""
        raise NotImplementedError

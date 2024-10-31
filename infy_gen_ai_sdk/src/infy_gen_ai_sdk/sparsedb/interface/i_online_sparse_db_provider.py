# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

"""Module for Online Sparse Db provider interface"""

import abc
from ...schema.sparse_db_data import OnlineSparseDbConfigData, BaseSparseDbSaveRecordData, BaseSparseDbQueryParamsData


class IOnlineSparseDbProvider(metaclass=abc.ABCMeta):
    """Interface class for Online Sparse Db provider"""

    def __init__(self, online_sparse_config_data:OnlineSparseDbConfigData) -> None:
        pass

    @abc.abstractmethod
    def get_matches(self, query_params_data: BaseSparseDbQueryParamsData):
        """Returns matches for given `query` from sparse Db"""
        raise NotImplementedError

    @abc.abstractmethod
    def save_record(self, db_record_data: BaseSparseDbSaveRecordData):
        """Saves a record to sparse Db"""
        raise NotImplementedError

    @abc.abstractmethod
    def get_records(self):
        """Get all records from sparse dB"""
        raise NotImplementedError

    @abc.abstractmethod
    def delete_records(self):
        """Delete specific records from sparse dB"""
        raise NotImplementedError

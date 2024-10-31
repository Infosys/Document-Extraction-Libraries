# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

"""Module for Sparse Db provider interface"""

import abc
from ...schema.sparse_db_data import BaseSparseDbConfigData, BaseSparseDbSaveRecordData, BaseSparseDbQueryParamsData


class ISparseDbProvider(metaclass=abc.ABCMeta):
    """Interface class for Sparse Db provider"""

    def __init__(self, config_data: BaseSparseDbConfigData) -> None:
        """Saves a record to sparse Db"""
        raise NotImplementedError

    @abc.abstractmethod
    def save_record(self, sparse_record_config_dict: BaseSparseDbSaveRecordData):
        """Saves a record to sparse Db"""
        raise NotImplementedError

    @abc.abstractmethod
    def get_records(self):
        """get specific records from sparse dB"""
        raise NotImplementedError
    
    @abc.abstractmethod
    def get_matches(self, query_params_data: BaseSparseDbQueryParamsData):
        """Returns matches for given `query` from sparse Db"""
        raise NotImplementedError

    @abc.abstractmethod
    def delete_records(self):
        """Delete specific records from sparse dB"""
        raise NotImplementedError

# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

"""Module for Vector Db provider interface"""

import abc
from typing import List
from ...embedding.interface.i_embedding_provider import IEmbeddingProvider
from ...schema.vector_db_data import BaseVectorDbQueryParamsData, BaseVectorDbRecordData


class IVectorDbProvider(metaclass=abc.ABCMeta):
    """Interface class for Vector Db provider"""

    def __init__(self, db_type: str, embedding_provider: IEmbeddingProvider) -> None:
        self.__db_type = db_type
        # Set embedding provider at class level for child classes to access
        self._embedding_provider = embedding_provider

    def get_db_type(self):
        """Returns database type `db_type`"""
        return self.__db_type

    @abc.abstractmethod
    def get_matches(self, query_params_data: BaseVectorDbQueryParamsData) -> List[BaseVectorDbRecordData]:
        """Returns matches for given `query` from vector Db"""
        raise NotImplementedError

    @abc.abstractmethod
    def save_record(self, db_record_data: BaseVectorDbRecordData):
        """Saves a record to vector Db"""
        raise NotImplementedError

    @abc.abstractmethod
    def get_records(self, count: int = -1) -> List[BaseVectorDbRecordData]:
        """Get all records from vector dB"""
        raise NotImplementedError

    @abc.abstractmethod
    def delete_records(self):
        """Delete specific records from vector dB"""
        raise NotImplementedError

    @abc.abstractmethod
    def get_custom_metadata(self):
        """Return custom metadata schema"""
        raise NotImplementedError

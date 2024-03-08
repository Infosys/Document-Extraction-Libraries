# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                   #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

"""Module for embedding provider interface class"""

import abc


class IEmbeddingProvider(metaclass=abc.ABCMeta):
    """Interface class for embedding provider"""

    def __init__(self, embeddings) -> None:
        self.__embeddings = embeddings

    def get_embeddings(self):
        """Return embeddings `embeddings`"""
        return self.__embeddings

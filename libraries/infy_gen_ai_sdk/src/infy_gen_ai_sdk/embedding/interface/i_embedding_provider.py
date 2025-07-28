# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

"""Module for embedding provider interface class"""

import abc
import numpy as np
from ...schema.embedding_data import BaseEmbeddingData


class IEmbeddingProvider(metaclass=abc.ABCMeta):
    """Interface class for embedding provider"""

    @abc.abstractmethod
    def generate_embedding(self, text: str) -> BaseEmbeddingData:
        """Generate embedding for given text"""
        raise NotImplementedError

    def convert_to_numpy_array(self, text_embeddings):
        """Convert embeddings to numpy array"""
        # If the embeddings are in list format, convert them to numpy array of shape (1, n)
        if isinstance(text_embeddings, list):
            vector = np.array(text_embeddings, dtype=np.float32).reshape(1, -1)
        else:
            vector = text_embeddings
        return vector

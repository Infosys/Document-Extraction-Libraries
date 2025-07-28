# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

from pydantic import BaseModel


class BaseEmbeddingData(BaseModel):
    """Base class for storing embedding details"""
    vector: list = None
    vector_dimension: int = None
    error_message: str = None
    model_name: str = None

    class Config:
        """Configuration"""
        arbitrary_types_allowed = True

    # @validator('vector')
    # @field_validator('vector')
    # # @classmethod
    # @staticmethod
    # def validate_vector(v):
    #     """Validate vector field"""
    #     if v is not None and not isinstance(v, np.ndarray):
    #         raise TypeError('vector must be a numpy.ndarray')
    #     return v


class EmbeddingData(BaseEmbeddingData):
    """Embedding data class"""

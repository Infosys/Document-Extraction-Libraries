# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#
# from pydantic import BaseModel, validator
import numpy as np
try:
    from pydantic.v1 import BaseModel
except ImportError:
    from pydantic import BaseModel



# Conditional import based on Pydantic version
# if pydantic.VERSION.startswith('1'):
#     from pydantic import validator as field_validator
# else:
#     from pydantic import field_validator


class BaseEmbeddingData(BaseModel):
    """Base class for storing embedding details"""
    vector: np.ndarray = None
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

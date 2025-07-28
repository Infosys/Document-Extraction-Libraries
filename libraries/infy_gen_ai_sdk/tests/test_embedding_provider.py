# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

"""Testing module"""

import os
import infy_gen_ai_sdk


def test_openai_direct():
    """Test method"""
    # Step 1 - Choose embedding provider
    embedding_provider_config_data = infy_gen_ai_sdk.embedding.provider.OpenAIEmbeddingProviderConfigData(
        **{
            "api_type": "azure",
            "api_url": os.environ['AZURE_OPENAI_SERVER_BASE_URL'],
            "api_key": os.environ['AZURE_OPENAI_SECRET_KEY'],
            "model_name": "text-embedding-ada-002",
            "deployment_name": "text-embedding-ada-002",
            "api_version": "2022-12-01",
            "chunk_size": 1000
        })
    embedding_provider = infy_gen_ai_sdk.embedding.provider.OpenAIEmbeddingProvider(
        embedding_provider_config_data)

    # Step 2 - Generate embedding
    embedding = embedding_provider.generate_embedding(
        'This is a test sentence')
    assert embedding.vector_dimension == 1536
    assert embedding.error_message is None


def test_openai_litellm_direct():
    """Test method"""
    # Step 1 - Choose embedding provider
    embedding_provider_config_data = infy_gen_ai_sdk.embedding.provider.OpenAIFormatEmbeddingProviderConfigData(
        **{
            "api_url": os.environ['AZURE_OPENAI_SERVER_BASE_URL'],
            "api_key": os.environ['AZURE_OPENAI_SECRET_KEY'],
            "model_name": "azure/text-embedding-ada-002",
            "api_version": "2022-12-01"
        })
    embedding_provider = infy_gen_ai_sdk.embedding.provider.OpenAIFormatEmbeddingProvider(
        embedding_provider_config_data)

    # Step 2 - Generate embedding
    embedding = embedding_provider.generate_embedding(
        'This is a test sentence')
    assert embedding.vector_dimension == 1536
    assert embedding.error_message is None


def test_openai_litellm_proxy():
    """Test method"""
    # Step 1 - Choose embedding provider
    embedding_provider_config_data = infy_gen_ai_sdk.embedding.provider.OpenAIFormatEmbeddingProviderConfigData(
        **{
            "api_url": os.environ['LITELLM_PROXY_SERVER_BASE_URL'],
            "api_key": os.environ['AZURE_OPENAI_SECRET_KEY'],
            "model_name": "text-embedding-ada-002",
            "api_version": "2022-12-01"
        })
    embedding_provider = infy_gen_ai_sdk.embedding.provider.OpenAIFormatEmbeddingProvider(
        embedding_provider_config_data)

    # Step 2 - Generate embedding
    embedding = embedding_provider.generate_embedding(
        'This is a test sentence')
    assert embedding.vector_dimension == 1536
    assert embedding.error_message is None


def test_st_ray():
    """Test method"""
    # Step 1 - Choose embedding provider
    embedding_provider_config_data = infy_gen_ai_sdk.embedding.provider.StEmbeddingProviderConfigData(
        **{
            "api_url": os.environ['INFY_MODEL_SERVICE_BASE_URL']
        })
    embedding_provider = infy_gen_ai_sdk.embedding.provider.StEmbeddingProvider(
        embedding_provider_config_data)

    # Step 2 - Generate embedding
    embedding = embedding_provider.generate_embedding(
        'This is a test sentence')
    assert embedding.vector_dimension == 384
    assert embedding.error_message in {None, ''}


def test_custom_embedding_1():
    """Test method"""
    # Step 1 - Choose embedding provider
    embedding_provider_config_data = infy_gen_ai_sdk.embedding.provider.CustomEmbeddingProviderConfigData(
        **{
            "api_key": "",
            "endpoint": os.environ['CUSTOM_EMB_MISTRAL_INFERENCE_URL']
        })
    embedding_provider = infy_gen_ai_sdk.embedding.provider.CustomEmbeddingProvider(
        embedding_provider_config_data)

    # Step 2 - Generate embedding
    embedding = embedding_provider.generate_embedding(
        'This is a test sentence')
    assert embedding.vector_dimension == 4096
    assert embedding.error_message is None

# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

"""Testing module"""

import os
from typing import Any, Dict, List, Optional
from datasets import Dataset
from langchain_openai import AzureChatOpenAI
from langchain_openai import AzureOpenAIEmbeddings
from ragas.metrics import faithfulness, answer_correctness, answer_similarity, answer_relevancy, context_recall, context_precision, context_utilization, context_entity_recall
from ragas import evaluate
from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from langchain_core.language_models.llms import LLM
from langchain_core.embeddings import Embeddings

import infy_gen_ai_sdk

class CustomLLM(LLM):
    """A custom LLM class"""
    api_url: str = None
    api_key: str = None
    model_name: str = None
    deployment_name: str = None
    max_tokens: int = None
    temperature: int = None  # 0.7
    top_p: float = None
    frequency_penalty: float = None
    presence_penalty: float = None
    stop: str = None
    timeout: int = None

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """Run the LLM on the given input"""
        if stop is not None:
            raise ValueError("stop kwargs are not permitted.")

        llm_provider_config_data = infy_gen_ai_sdk.llm.provider.OpenAIFormatLlmProviderConfigData(
            **{
                "api_url": self.api_url,
                "api_key": self.api_key,
                "model_name": self.model_name,
                "deployment_name": self.deployment_name,
                "max_tokens": self.max_tokens,
                'temperature': self.temperature,
                "top_p": self.top_p,
                "frequency_penalty": self.frequency_penalty,
                "presence_penalty": self.presence_penalty,
                "stop": None
            })
        llm_provider = infy_gen_ai_sdk.llm.provider.OpenAIFormatLlmProvider(
            llm_provider_config_data)

        llm_request_data = infy_gen_ai_sdk.llm.provider.OpenAIFormatLlmRequestData(
            **{
                "prompt_template": prompt,
                "template_var_to_value_dict": {
                    'context': "",
                    'question': ""
                }
            }
        )
        llm_response_data: infy_gen_ai_sdk.llm.provider.OpenAIFormatLlmResponseData = llm_provider.get_llm_response(
            llm_request_data)

        llm_response_txt = llm_response_data.llm_response_txt

        return llm_response_txt

    @property
    def _identifying_params(self) -> Dict[str, Any]:
        """Return a dictionary of identifying parameters."""
        return {
            "model_name": "Custom LLM Chat Model",
        }

    @property
    def _llm_type(self) -> str:
        """Get the type of language model used by this chat model. Used for logging purposes only."""
        return "custom"


class CustomEmbeddings(Embeddings):
    """A custom Embeddings class"""
    api_url: str = None
    api_key: str = None
    model_name: str = None
    api_version: str = None

    def __init__(self, model_name: str, api_key: str, api_url: str, api_version: str):
        self.api_url = api_url
        self.api_key = api_key
        self.model_name = model_name
        self.api_version = api_version

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed search docs."""
        # embedding = [[0.5, 0.6, 0.7] for _ in texts]
        embeddings = []
        embedding_provider_config_data = infy_gen_ai_sdk.embedding.provider.OpenAIFormatEmbeddingProviderConfigData(
            **{
                "api_url": self.api_url,
                "api_key": self.api_key,
                "model_name": self.model_name,
                "api_version": self.api_version
            })
        embedding_provider = infy_gen_ai_sdk.embedding.provider.OpenAIFormatEmbeddingProvider(
            embedding_provider_config_data)
        embeddings = [
            embedding_provider.generate_embedding(text).vector
            for text in texts
        ]
        return embeddings
        # return embedding.vector

    def embed_query(self, text: str) -> List[float]:
        """Embed query text."""
        return self.embed_documents([text])[0]


# Set Azure generic properties
os.environ["AZURE_OPENAI_API_KEY"] = os.environ["AZURE_OPENAI_SECRET_KEY"]
os.environ["AZURE_OPENAI_ENDPOINT"] = os.environ["AZURE_OPENAI_SERVER_BASE_URL"]

# NOTE:Make sure you have the below environment variable set else uncomment below code and set
# os.environ["TIKTOKEN_CACHE_DIR"] = ''

llm_model = AzureChatOpenAI(
    openai_api_version="2024-02-15-preview",
    azure_deployment="gpt4"
)

embeddings_model = AzureOpenAIEmbeddings(
    openai_api_version="2022-12-01",
    azure_deployment="text-embedding-ada-002",
)


def test_dataset_1():
    """Test dataset 1"""
    dataset = {
        "question": ["What is the capital of France?"],
        "answer": ["Paris is the capital and its in western Europe."],
        "contexts": [["Paris is the capital and most populous city of France."]],
        "ground_truth": ["Paris"]
    }

    dataset = Dataset.from_dict(dataset)
    score = evaluate(dataset,
                     llm=llm_model,
                     embeddings=embeddings_model,
                     metrics=[faithfulness, answer_relevancy])

    print(score.to_pandas())


def test_custom_llm():
    """Test custom LLM"""
    dataset = {
        "question": ["What is the capital of France?"],
        "answer": ["Paris is the capital and its in western Europe."],
        "contexts": [["Paris is the capital and most populous city of France."]],
        "ground_truth": ["Paris"]
    }

    custom_llm = CustomLLM(
        **{
            "api_url": os.environ["LITELLM_PROXY_SERVER_BASE_URL"],
            "api_key": os.environ["AZURE_OPENAI_SECRET_KEY"],
            "model_name": "gpt-4-32k_2",
            "deployment_name": "gpt-4-32k_2",
            "max_tokens": 1000,
            'temperature': 0.5,
            "top_p": 0.95,
            "frequency_penalty": 0,
            "presence_penalty": 0,
            "stop": None
        })
    print("custom_llm::", custom_llm)
    dataset = Dataset.from_dict(dataset)
    score = evaluate(dataset,
                     llm=custom_llm,
                     metrics=[faithfulness, context_recall, context_precision, context_utilization, context_entity_recall])
    print(score.to_pandas())


def test_custom_embedding():
    """Test custom Embedding"""
    dataset = {
        "question": ["What is the capital of France?"],
        "answer": ["Paris is the capital and its in western Europe."],
        "contexts": [["Paris is the capital and most populous city of France."]],
        "ground_truth": ["Paris"]
    }
    custom_llm = CustomLLM(
        **{
            "api_url": os.environ["LITELLM_PROXY_SERVER_BASE_URL"],
            "api_key": os.environ["AZURE_OPENAI_SECRET_KEY"],
            "model_name": "gpt-4-32k_2",
            "deployment_name": "gpt-4-32k_2",
            "max_tokens": 1000,
            'temperature': 0.5,
            "top_p": 0.95,
            "frequency_penalty": 0,
            "presence_penalty": 0,
            "stop": None
        })

    custom_embedding = CustomEmbeddings(
        **{
            "api_url": os.environ["LITELLM_PROXY_SERVER_BASE_URL"],
            "api_key": os.environ["AZURE_OPENAI_SECRET_KEY"],
            "model_name": "text-embedding-ada-002",
            "api_version": "2022-12-01"
        })

    dataset = Dataset.from_dict(dataset)
    score = evaluate(dataset,
                     llm=custom_llm,
                     embeddings=custom_embedding,
                     metrics=[answer_correctness, answer_similarity, answer_relevancy])

    print(score.to_pandas())

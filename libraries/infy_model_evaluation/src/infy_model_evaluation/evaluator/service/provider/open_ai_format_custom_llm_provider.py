# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

"""This module contains the OpenAIFormatCustomLlmProvider class."""

from typing import Any, Dict, List, Optional
from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from langchain_core.language_models.llms import LLM
import infy_gen_ai_sdk


class OpenAIFormatCustomLlmProvider(LLM):
    """A openAI format custom LLM class"""
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
            "model_name": "Custom LLM Model",
        }

    @property
    def _llm_type(self) -> str:
        """Get the type of language model used by this chat model. Used for logging purposes only."""
        return "custom"

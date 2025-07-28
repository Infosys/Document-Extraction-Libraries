# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

"""Testing module"""

import os
import json
import pytest
import infy_gen_ai_sdk

CONTAINER_ROOT_PATH = f"C:/temp/unittest/infy_gen_ai_sdk/{__name__}/CONTAINER"

# Preparing Data
PROMPT_TEMPLATE = """
Use the following pieces of context to answer the question at the end. If you are unsure about the answer, just say that you don't know. Don't try to make up an answer. Provide the shortest and most appropriate relevant answer to the question in proper JSON format with the key as "answer". This JSON format should be followed even when the answer is not found. Ensure all text in the answer is in lowercase.
{context}
Question: {question}
Helpful Answer:
"""

CONTEXT = """
In the depths of an abandoned train tunnel, John and Mark stumbled upon a mysterious machine.
Its sleek, alien design hinted at a technology beyond their comprehension. With cautious excitement,
they pressed buttons and pulled levers, inadvertently activating a time machine.

The tunnel vanished, replaced by a bustling 19th-century street. Wide-eyed, they realized
the power they held. They explored eras, witnessing history's highs and lows. From ancient Rome
to a futuristic metropolis, time unfurled before them.

But the machine's power waned. Panic set in as they realized they were trapped.
They scrambled, trying to reverse their journey, but it was futile. The time machine
blinked out, leaving them marooned in the past.
"""

QUESTION_1 = "What did John and Mark discover?"
QUESTION_2 = "How did John and Mark activate the mysterious machine?"


@pytest.fixture(scope='module', autouse=True)
def pre_test(create_root_folders):
    """Initialization method"""
    create_root_folders([CONTAINER_ROOT_PATH])
    # Configure client properties
    client_config_data = infy_gen_ai_sdk.ClientConfigData(
        **{
            "container_data": {
                "container_root_path": f"{CONTAINER_ROOT_PATH}",
            }
        }
    )
    infy_gen_ai_sdk.ClientConfigManager().load(client_config_data)
    print(infy_gen_ai_sdk.ClientConfigManager().get().dict())


# Direct Calls - Single Request
def test_direct_single_call_openai_gpt_4():
    """Direct call to LLM Endpoint to make single request for model: OpenAI GPT-4"""
    # Step 1 - Choose LLM provider
    llm_provider_config_data = infy_gen_ai_sdk.llm.provider.OpenAIFormatLlmProviderConfigData(
        **{
            "api_url": os.environ['AZURE_OPENAI_SERVER_BASE_URL'],
            "api_key": os.environ['AZURE_OPENAI_SECRET_KEY'],
            "model_name": "azure/gpt-4",
            "deployment_name": "gpt4",
            "max_tokens": 1000,
            'temperature': 0.5,
            "top_p": 0.95,
            "frequency_penalty": 0,
            "presence_penalty": 0,
            "stop": None,
            "timeout": 120
        })
    llm_provider = infy_gen_ai_sdk.llm.provider.OpenAIFormatLlmProvider(
        llm_provider_config_data)

    llm_request_data = infy_gen_ai_sdk.llm.provider.OpenAIFormatLlmRequestData(
        **{
            "prompt_template": PROMPT_TEMPLATE,
            "template_var_to_value_dict": {
                'context': CONTEXT,
                'question': QUESTION_1
            }
        }
    )

    # Step 2 - Fire query to LLM
    llm_response_data: infy_gen_ai_sdk.llm.provider.OpenAIFormatLlmResponseData = llm_provider.get_llm_response(
        llm_request_data)

    llm_response_txt = llm_response_data.llm_response_txt
    try:
        llm_response_json = json.loads(llm_response_txt)
        assert 'answer' in llm_response_json.keys()
    except Exception:
        assert False, "LLM response is not JSON format as per prompt template"

    print(dict(llm_response_data))


def test_direct_single_call_openai_gpt_35_turbo():
    """Direct call to LLM Endpoint to make single request for model: OpenAI GPT-3.5 turbo"""
    # Step 1 - Choose LLM provider
    llm_provider_config_data = infy_gen_ai_sdk.llm.provider.OpenAIFormatLlmProviderConfigData(
        **{
            "api_url": os.environ['AZURE_OPENAI_SERVER_BASE_URL'],
            "api_key": os.environ['AZURE_OPENAI_SECRET_KEY'],
            "model_name": "azure/gpt-35-turbo",
            "deployment_name": "gpt-35-turbo",
            "max_tokens": 1000,
            'temperature': 0.5,
            "top_p": 0.95,
            "frequency_penalty": 0,
            "presence_penalty": 0,
            "stop": None
        })
    llm_provider = infy_gen_ai_sdk.llm.provider.OpenAIFormatLlmProvider(
        llm_provider_config_data)

    llm_request_data = infy_gen_ai_sdk.llm.provider.OpenAIFormatLlmRequestData(
        **{
            "prompt_template": PROMPT_TEMPLATE,
            "template_var_to_value_dict": {
                'context': CONTEXT,
                'question': QUESTION_1
            }
        }
    )

    # Step 2 - Fire query to LLM
    llm_response_data: infy_gen_ai_sdk.llm.provider.OpenAIFormatLlmResponseData = llm_provider.get_llm_response(
        llm_request_data)

    llm_response_txt = llm_response_data.llm_response_txt
    try:
        llm_response_json = json.loads(llm_response_txt)
        assert 'answer' in llm_response_json.keys()
    except Exception:
        assert False, "LLM response is not JSON format as per prompt template"

    print(dict(llm_response_data))

# Direct Calls - Batch Request
def test_direct_batch_call_openai_gpt_4():
    """Test method"""
    # Step 1 - Choose LLM provider
    llm_provider_config_data = infy_gen_ai_sdk.llm.provider.OpenAIFormatLlmProviderConfigData(
        **{
            "api_url": os.environ['AZURE_OPENAI_SERVER_BASE_URL'],
            "api_key": os.environ['AZURE_OPENAI_SECRET_KEY'],
            "model_name": "azure/gpt4",
            "deployment_name": "gpt4",
            "max_tokens": 1000,
            'temperature': 0.5,
            "top_p": 0.95,
            "frequency_penalty": 0,
            "presence_penalty": 0,
            "stop": None
        })
    llm_provider = infy_gen_ai_sdk.llm.provider.OpenAIFormatLlmProvider(
        llm_provider_config_data)
    llm_request_data_list = []

    llm_request_data_1 = infy_gen_ai_sdk.llm.provider.OpenAIFormatLlmRequestData(
        **{
            "prompt_template": PROMPT_TEMPLATE,
            "template_var_to_value_dict": {
                'context': CONTEXT,
                'question': QUESTION_1
            }
        }
    )

    llm_request_data_2 = infy_gen_ai_sdk.llm.provider.OpenAIFormatLlmRequestData(
        **{
            "prompt_template": PROMPT_TEMPLATE,
            "template_var_to_value_dict": {
                'context': CONTEXT,
                'question': QUESTION_2
            }
        }
    )

    llm_request_data_list.append(llm_request_data_1)
    llm_request_data_list.append(llm_request_data_2)

    # Step 2 - Fire query to LLM
    llm_response_data_list: infy_gen_ai_sdk.llm.provider.OpenAIFormatLlmResponseData = llm_provider.get_llm_response_batch(
        llm_request_data_list)

    for llm_response_data in llm_response_data_list:
        llm_response_txt = llm_response_data.llm_response_txt
        try:
            llm_response_json = json.loads(llm_response_txt)
            assert 'answer' in llm_response_json.keys()
        except Exception:
            assert False, "LLM response is not JSON format as per prompt template"

        print(dict(llm_response_json))

    assert len(llm_response_data_list) > 1


def test_direct_batch_call_openai_gpt_35_turbo():
    """Test method"""
    # Step 1 - Choose LLM provider
    llm_provider_config_data = infy_gen_ai_sdk.llm.provider.OpenAIFormatLlmProviderConfigData(
        **{
            "api_url": os.environ['AZURE_OPENAI_SERVER_BASE_URL'],
            "api_key": os.environ['AZURE_OPENAI_SECRET_KEY'],
            "model_name": "azure/gpt-35-turbo",
            "deployment_name": "gpt-35-turbo",
            "max_tokens": 1000,
            'temperature': 0.5,
            "top_p": 0.95,
            "frequency_penalty": 0,
            "presence_penalty": 0,
            "stop": None
        })
    llm_provider = infy_gen_ai_sdk.llm.provider.OpenAIFormatLlmProvider(
        llm_provider_config_data)
    llm_request_data_list = []

    llm_request_data_1 = infy_gen_ai_sdk.llm.provider.OpenAIFormatLlmRequestData(
        **{
            "prompt_template": PROMPT_TEMPLATE,
            "template_var_to_value_dict": {
                'context': CONTEXT,
                'question': QUESTION_1
            }
        }
    )

    llm_request_data_2 = infy_gen_ai_sdk.llm.provider.OpenAIFormatLlmRequestData(
        **{
            "prompt_template": PROMPT_TEMPLATE,
            "template_var_to_value_dict": {
                'context': CONTEXT,
                'question': QUESTION_2
            }
        }
    )

    llm_request_data_list.append(llm_request_data_1)
    llm_request_data_list.append(llm_request_data_2)

    # Step 2 - Fire query to LLM
    llm_response_data_list: infy_gen_ai_sdk.llm.provider.OpenAIFormatLlmResponseData = llm_provider.get_llm_response_batch(
        llm_request_data_list)

    for llm_response_data in llm_response_data_list:
        llm_response_txt = llm_response_data.llm_response_txt
        try:
            llm_response_json = json.loads(llm_response_txt)
            assert 'answer' in llm_response_json.keys()
        except Exception:
            assert False, "LLM response is not JSON format as per prompt template"

        print(dict(llm_response_json))

    assert len(llm_response_data_list) > 1

# Proxy Calls - Single Request
def test_proxy_single_call_openai_gpt_4():
    """Proxy call to make single request for model: OpenAI GPT-4"""
    llm_provider_config_data = infy_gen_ai_sdk.llm.provider.OpenAIFormatLlmProviderConfigData(
        **{
            "api_url": os.environ['LITELLM_PROXY_SERVER_BASE_URL'],
            "api_key": os.environ['AZURE_OPENAI_SECRET_KEY'],    
            "model_name": "gpt-4-32k_2",
            "deployment_name": "gpt-4-32k_2",
            "max_tokens": 1000,
            'temperature': 0.5,
            "top_p": 0.95,
            "frequency_penalty": 0,
            "presence_penalty": 0,
            "stop": None,
            "timeout":20
        })
    llm_provider = infy_gen_ai_sdk.llm.provider.OpenAIFormatLlmProvider(
        llm_provider_config_data)

    llm_request_data = infy_gen_ai_sdk.llm.provider.OpenAIFormatLlmRequestData(
        **{
            "prompt_template": PROMPT_TEMPLATE,
            "template_var_to_value_dict": {
                'context': CONTEXT,
                'question': QUESTION_1
            }
        }
    )

    # Step 2 - Fire query to LLM
    llm_response_data: infy_gen_ai_sdk.llm.provider.OpenAIFormatLlmResponseData = llm_provider.get_llm_response(
        llm_request_data)

    llm_response_txt = llm_response_data.llm_response_txt
    try:
        llm_response_json = json.loads(llm_response_txt)
        assert 'answer' in llm_response_json.keys()
    except Exception:
        assert False, "LLM response is not JSON format as per prompt template"

    print(dict(llm_response_data))


def test_proxy_single_call_llama_3_1_8B():
    """Proxy call to make single request for model: Llama 3.1 8B"""
    # Step 1 - Choose LLM provider
    llm_provider_config_data = infy_gen_ai_sdk.llm.provider.OpenAIFormatLlmProviderConfigData(
        **{
            "api_url": os.environ['LITELLM_PROXY_SERVER_BASE_URL'],
            "api_key": os.environ['LITELLM_PROXY_SECRET_KEY'],  
            "model_name": "Meta-Llama-3.1-8B-Instruct",
            "deployment_name": "Meta-Llama-3.1-8B-Instruct",
            "max_tokens": 1000,
            'temperature': 0.5,
            "top_p": 0.95,
            "frequency_penalty": 0,
            "presence_penalty": 0,
            "stop": None
        })
    llm_provider = infy_gen_ai_sdk.llm.provider.OpenAIFormatLlmProvider(
        llm_provider_config_data)

    llm_request_data = infy_gen_ai_sdk.llm.provider.OpenAIFormatLlmRequestData(
        **{
            "prompt_template": PROMPT_TEMPLATE,
            "template_var_to_value_dict": {
                'context': CONTEXT,
                'question': QUESTION_1
            }
        }
    )

    # Step 2 - Fire query to LLM
    llm_response_data: infy_gen_ai_sdk.llm.provider.OpenAIFormatLlmResponseData = llm_provider.get_llm_response(
        llm_request_data)

    llm_response_txt = llm_response_data.llm_response_txt
    try:
        llm_response_json = json.loads(llm_response_txt)
        assert 'answer' in llm_response_json.keys()
    except Exception:
        assert False, "LLM response is not JSON format as per prompt template"

    print(dict(llm_response_data))


def test_proxy_single_call_llama_3_3_70B():
    """Proxy call to make single request for model: Llama 3.1 70B"""
    # Step 1 - Choose LLM provider
    llm_provider_config_data = infy_gen_ai_sdk.llm.provider.OpenAIFormatLlmProviderConfigData(
        **{
            "api_url": os.environ['LITELLM_PROXY_SERVER_BASE_URL'],
            "api_key": os.environ['LITELLM_PROXY_SECRET_KEY'],
            "model_name": "Meta-Llama-3.3-70B-Instruct",
            "deployment_name": "Meta-Llama-3.3-70B-Instruct",
            "max_tokens": 1000,
            'temperature': 0.5,
            "top_p": 0.95,
            "frequency_penalty": 0,
            "presence_penalty": 0,
            "stop": None
        })
    llm_provider = infy_gen_ai_sdk.llm.provider.OpenAIFormatLlmProvider(
        llm_provider_config_data)

    llm_request_data = infy_gen_ai_sdk.llm.provider.OpenAIFormatLlmRequestData(
        **{
            "prompt_template": PROMPT_TEMPLATE,
            "template_var_to_value_dict": {
                'context': CONTEXT,
                'question': QUESTION_1
            }
        }
    )

    # Step 2 - Fire query to LLM
    llm_response_data: infy_gen_ai_sdk.llm.provider.OpenAIFormatLlmResponseData = llm_provider.get_llm_response(
        llm_request_data)

    llm_response_txt = llm_response_data.llm_response_txt
    try:
        llm_response_json = json.loads(llm_response_txt)
        assert 'answer' in llm_response_json.keys()
    except Exception:
        assert False, "LLM response is not JSON format as per prompt template"

    print(dict(llm_response_data))


def test_proxy_single_call_mixtral_7B():
    """Proxy call to make single request for model: Mixtral 7B"""
    # Step 1 - Choose LLM provider
    llm_provider_config_data = infy_gen_ai_sdk.llm.provider.OpenAIFormatLlmProviderConfigData(
        **{
            "api_url": os.environ['LITELLM_PROXY_SERVER_BASE_URL'],
            "api_key": os.environ['LITELLM_PROXY_SECRET_KEY'],
            "model_name": "mixtral-8x7b-instruct",
            "deployment_name": "mixtral-8x7b-instruct",
            "max_tokens": 1000,
            'temperature': 0.5,
            "top_p": 0.95,
            "frequency_penalty": 0,
            "presence_penalty": 0,
            "stop": None
        })
    llm_provider = infy_gen_ai_sdk.llm.provider.OpenAIFormatLlmProvider(
        llm_provider_config_data)

    llm_request_data = infy_gen_ai_sdk.llm.provider.OpenAIFormatLlmRequestData(
        **{
            "prompt_template": PROMPT_TEMPLATE,
            "template_var_to_value_dict": {
                'context': CONTEXT,
                'question': QUESTION_1
            }
        }
    )

    # Step 2 - Fire query to LLM
    llm_response_data: infy_gen_ai_sdk.llm.provider.OpenAIFormatLlmResponseData = llm_provider.get_llm_response(
        llm_request_data)

    llm_response_txt = llm_response_data.llm_response_txt
    try:
        llm_response_json = json.loads(llm_response_txt)
        assert 'answer' in llm_response_json.keys()
    except Exception:
        assert False, "LLM response is not JSON format as per prompt template"

    print(dict(llm_response_data))


# Proxy Calls - Batch Request
def test_proxy_batch_call_openai_gpt_4():
    """Test method"""
    # Step 1 - Choose LLM provider
    llm_provider_config_data = infy_gen_ai_sdk.llm.provider.OpenAIFormatLlmProviderConfigData(
        **{
            "api_url": os.environ['LITELLM_PROXY_SERVER_BASE_URL'],
            "api_key": os.environ['AZURE_OPENAI_SECRET_KEY'],
            "model_name": "gpt-4-32k_2",
            "deployment_name": "gpt-4-32k_2",
            "max_tokens": 1000,
            'temperature': 0.5,
            "top_p": 0.95,
            "frequency_penalty": 0,
            "presence_penalty": 0,
            "stop": None
        })
    llm_provider = infy_gen_ai_sdk.llm.provider.OpenAIFormatLlmProvider(
        llm_provider_config_data)
    llm_request_data_list = []

    llm_request_data_1 = infy_gen_ai_sdk.llm.provider.OpenAIFormatLlmRequestData(
        **{
            "prompt_template": PROMPT_TEMPLATE,
            "template_var_to_value_dict": {
                'context': CONTEXT,
                'question': QUESTION_1
            }
        }
    )

    llm_request_data_2 = infy_gen_ai_sdk.llm.provider.OpenAIFormatLlmRequestData(
        **{
            "prompt_template": PROMPT_TEMPLATE,
            "template_var_to_value_dict": {
                'context': CONTEXT,
                'question': QUESTION_2
            }
        }
    )

    llm_request_data_list.append(llm_request_data_1)
    llm_request_data_list.append(llm_request_data_2)

    # Step 2 - Fire query to LLM
    llm_response_data_list: infy_gen_ai_sdk.llm.provider.OpenAIFormatLlmResponseData = llm_provider.get_llm_response_batch(
        llm_request_data_list)

    for llm_response_data in llm_response_data_list:
        llm_response_txt = llm_response_data.llm_response_txt
        try:
            llm_response_json = json.loads(llm_response_txt)
            assert 'answer' in llm_response_json.keys()
        except Exception:
            assert False, "LLM response is not JSON format as per prompt template"

        print(dict(llm_response_json))

    assert len(llm_response_data_list) > 1


def test_proxy_batch_call_llama_3_1_8B():
    """Test method"""
    # Step 1 - Choose LLM provider
    llm_provider_config_data = infy_gen_ai_sdk.llm.provider.OpenAIFormatLlmProviderConfigData(
        **{
            "api_url": os.environ['LITELLM_PROXY_SERVER_BASE_URL'],
            "api_key": os.environ['LITELLM_PROXY_SECRET_KEY'],
            "model_name": "Meta-Llama-3.1-8B-Instruct",
            "deployment_name": "Meta-Llama-3.1-8B-Instruct",
            "max_tokens": 1000,
            'temperature': 0.5,
            "top_p": 0.95,
            "frequency_penalty": 0,
            "presence_penalty": 0,
            "stop": None
        })
    llm_provider = infy_gen_ai_sdk.llm.provider.OpenAIFormatLlmProvider(
        llm_provider_config_data)
    llm_request_data_list = []

    llm_request_data_1 = infy_gen_ai_sdk.llm.provider.OpenAIFormatLlmRequestData(
        **{
            "prompt_template": PROMPT_TEMPLATE,
            "template_var_to_value_dict": {
                'context': CONTEXT,
                'question': QUESTION_1
            }
        }
    )

    llm_request_data_2 = infy_gen_ai_sdk.llm.provider.OpenAIFormatLlmRequestData(
        **{
            "prompt_template": PROMPT_TEMPLATE,
            "template_var_to_value_dict": {
                'context': CONTEXT,
                'question': QUESTION_2
            }
        }
    )

    llm_request_data_list.append(llm_request_data_1)
    llm_request_data_list.append(llm_request_data_2)

    # Step 2 - Fire query to LLM
    llm_response_data_list: infy_gen_ai_sdk.llm.provider.OpenAIFormatLlmResponseData = llm_provider.get_llm_response_batch(
        llm_request_data_list)

    for llm_response_data in llm_response_data_list:
        llm_response_txt = llm_response_data.llm_response_txt
        try:
            llm_response_json = json.loads(llm_response_txt)
            assert 'answer' in llm_response_json.keys()
        except Exception:
            assert False, "LLM response is not JSON format as per prompt template"

        print(dict(llm_response_json))

    assert len(llm_response_data_list) > 1


def test_proxy_batch_call_llama_3_3_70B():
    """Test method"""
    # Step 1 - Choose LLM provider
    llm_provider_config_data = infy_gen_ai_sdk.llm.provider.OpenAIFormatLlmProviderConfigData(
        **{
            "api_url": os.environ['LITELLM_PROXY_SERVER_BASE_URL'],
            "api_key": os.environ['LITELLM_PROXY_SECRET_KEY'],
            "model_name": "Meta-Llama-3.3-70B-Instruct",
            "deployment_name": "Meta-Llama-3.3-70B-Instruct",
            "max_tokens": 1000,
            'temperature': 0.5,
            "top_p": 0.95,
            "frequency_penalty": 0,
            "presence_penalty": 0,
            "stop": None
        })
    llm_provider = infy_gen_ai_sdk.llm.provider.OpenAIFormatLlmProvider(
        llm_provider_config_data)

    llm_request_data_list = []

    llm_request_data_1 = infy_gen_ai_sdk.llm.provider.OpenAIFormatLlmRequestData(
        **{
            "prompt_template": PROMPT_TEMPLATE,
            "template_var_to_value_dict": {
                'context': CONTEXT,
                'question': QUESTION_1
            }
        }
    )

    llm_request_data_2 = infy_gen_ai_sdk.llm.provider.OpenAIFormatLlmRequestData(
        **{
            "prompt_template": PROMPT_TEMPLATE,
            "template_var_to_value_dict": {
                'context': CONTEXT,
                'question': QUESTION_2
            }
        }
    )

    llm_request_data_list.append(llm_request_data_1)
    llm_request_data_list.append(llm_request_data_2)

    # Step 2 - Fire query to LLM
    llm_response_data_list: infy_gen_ai_sdk.llm.provider.OpenAIFormatLlmResponseData = llm_provider.get_llm_response_batch(
        llm_request_data_list)

    for llm_response_data in llm_response_data_list:
        llm_response_txt = llm_response_data.llm_response_txt
        try:
            llm_response_json = json.loads(llm_response_txt)
            assert 'answer' in llm_response_json.keys()
        except Exception:
            assert False, "LLM response is not JSON format as per prompt template"

        print(dict(llm_response_json))

    assert len(llm_response_data_list) > 1


def test_proxy_batch_call_mixtral_7B():
    """Test method"""
    # Step 1 - Choose LLM provider
    llm_provider_config_data = infy_gen_ai_sdk.llm.provider.OpenAIFormatLlmProviderConfigData(
        **{
            "api_url": os.environ['LITELLM_PROXY_SERVER_BASE_URL'],
            "api_key": os.environ['LITELLM_PROXY_SECRET_KEY'],
            "model_name": "mixtral-8x7b-instruct",
            "deployment_name": "mixtral-8x7b-instruct",
            "max_tokens": 1000,
            'temperature': 0.5,
            "top_p": 0.95,
            "frequency_penalty": 0,
            "presence_penalty": 0,
            "stop": None
        })
    llm_provider = infy_gen_ai_sdk.llm.provider.OpenAIFormatLlmProvider(
        llm_provider_config_data)
    llm_request_data_list = []

    llm_request_data_1 = infy_gen_ai_sdk.llm.provider.OpenAIFormatLlmRequestData(
        **{
            "prompt_template": PROMPT_TEMPLATE,
            "template_var_to_value_dict": {
                'context': CONTEXT,
                'question': QUESTION_1
            }
        }
    )

    llm_request_data_2 = infy_gen_ai_sdk.llm.provider.OpenAIFormatLlmRequestData(
        **{
            "prompt_template": PROMPT_TEMPLATE,
            "template_var_to_value_dict": {
                'context': CONTEXT,
                'question': QUESTION_2
            }
        }
    )

    llm_request_data_list.append(llm_request_data_1)
    llm_request_data_list.append(llm_request_data_2)

    # Step 2 - Fire query to LLM
    llm_response_data_list: infy_gen_ai_sdk.llm.provider.OpenAIFormatLlmResponseData = llm_provider.get_llm_response_batch(
        llm_request_data_list)

    for llm_response_data in llm_response_data_list:
        llm_response_txt = llm_response_data.llm_response_txt
        try:
            llm_response_json = json.loads(llm_response_txt)
            assert 'answer' in llm_response_json.keys()
        except Exception:
            assert False, "LLM response is not JSON format as per prompt template"

        print(dict(llm_response_json))

    assert len(llm_response_data_list) > 1

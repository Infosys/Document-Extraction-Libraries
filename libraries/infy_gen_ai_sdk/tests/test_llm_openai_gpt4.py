# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

"""Testing module"""

import os
import json
import pytest
import infy_gen_ai_sdk

CONTAINER_ROOT_PATH = f"C:/temp/unittest/infy_gen_ai_sdk/{__name__}/CONTAINER"


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


def test_1():
    """Test method"""
    # Step 1 - Choose LLM provider
    llm_provider_config_data = infy_gen_ai_sdk.llm.provider.OpenAILlmProviderConfigData(
        **{
            "api_type": "azure",
            "api_url": os.environ['AZURE_OPENAI_SERVER_BASE_URL'],
            "api_key": os.environ['AZURE_OPENAI_SECRET_KEY'],
            "api_version": "2024-02-15-preview",
            "model_name": "gpt-4",
            "deployment_name": "gpt4",
            "max_tokens": 1000,
            'temperature': 0.5,
            "is_chat_model": True,
            "top_p": 0.95,
            "frequency_penalty": 0,
            "presence_penalty": 0,
            "stop": None
        })
    llm_provider = infy_gen_ai_sdk.llm.provider.OpenAILlmProvider(
        llm_provider_config_data)

    # Step 2 - Prepare data
    PROMPT_TEMPLATE = """
Use the following pieces of context to answer the question at the end. 
If you don't know the answer or even doubtful a bit, just say that you don't know, 
don't try to make up an answer.Just give the shortest and most appropriate relavant answer 
to the question in proper json format with key as "answer".This json format should be followed even when answer is not found. 
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

    QUESTION = "What did John and Mark discover?"

    llm_request_data = infy_gen_ai_sdk.llm.provider.OpenAILlmRequestData(
        **{
            "prompt_template": PROMPT_TEMPLATE,
            "template_var_to_value_dict": {
                'context': CONTEXT,
                'question': QUESTION
            }
        }
    )

    # Step 3 - Fire query to LLM
    llm_response_data: infy_gen_ai_sdk.llm.provider.OpenAILlmResponseData = llm_provider.get_llm_response(
        llm_request_data)

    llm_response_txt = llm_response_data.llm_response_txt
    try:
        llm_response_json = json.loads(llm_response_txt)
        assert 'answer' in llm_response_json.keys()
    except Exception:
        assert False, "LLM response is not JSON format as per prompt template"

    assert "time machine" in llm_response_json['answer']

    print(dict(llm_response_data))

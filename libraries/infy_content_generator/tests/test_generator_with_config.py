# ===============================================================================================================#
# Copyright 2025 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#
import os
import importlib
import json
import pytest
from jsonpath_ng import parse
import infy_content_generator
import copy


CONTAINER_ROOT_PATH = f"C:/temp/unittest/infy_content_generator/{__name__}/CONTAINER"
STORAGE_ROOT_PATH = f"C:/temp/unittest/infy_content_generator/{__name__}/STORAGE"


@pytest.fixture(scope='module', autouse=True)
def pre_test(create_root_folders, copy_files_to_root_folder):
    """Test pre-run method"""
    # Create data folders
    create_root_folders([STORAGE_ROOT_PATH])
    # Copy files to pick up folder
    SAMPLE_ROOT_PATH = "./tests"
    FILES_TO_COPY = [
        ['question_prompt_test.txt', f"{SAMPLE_ROOT_PATH}",
            f"{STORAGE_ROOT_PATH}/tests"]
    ]
    copy_files_to_root_folder(FILES_TO_COPY)


qna_generator_config = {
    "techniques": [
        {
            "enabled": True,
            "name": "llama_with_two_stage",
            "qna_strategy_name": "$..qna_strategy.strategy_two_stage",
            "llm_providers": {
                "llm_provider_1": "$..llm.custom.meta-llama-3-3-70B-intruct_300_token",
                "llm_provider_2": "$..llm.custom.meta-llama-3-3-70B-intruct_1000_tokens"
            }
        },
        {
            "enabled": False,
            "name": "openai_with_zeroshotpair",
            "qna_strategy_name": "$..qna_strategy.strategy_zeroshotpair",
            "llm_providers": {
                "llm_provider_1": "$..llm.openai"
            }
        },
        {
            "enabled": False,
            "name": "llma_with_zeroshotpair",
            "qna_strategy_name": "$..qna_strategy.strategy_zeroshotpair",
            "llm_providers": {
                "llm_provider_1": "$..llm.custom.meta-llama-3-3-70B-intruct_1000_tokens"
            }
        },
        {
            "enabled": False,
            "name": "llama_with_two_stage_test_usr_provided_que_prompt",
            "qna_strategy_name": "$..qna_strategy.strategy_two_stage_test_provided_que_prompt",
            "llm_providers": {
                "llm_provider_1": "$..llm.custom.meta-llama-3-3-70B-intruct_300_token",
                "llm_provider_2": "$..llm.custom.meta-llama-3-3-70B-intruct_1000_tokens"
            }
        },
    ],
    "question_types": {
        "set_of_9": {
            "Subjective": 3,
            "Procedural": 0,
            "Factual": 0,
            "Hypothetical": 0,
            "Temporal": 0,
            "Cause and Effect": 0,
            "Deductive": 3,
            "Mathematical": 3,
            "Analytical": 3
        }
    },
    "qna_strategy": {
        "strategy_zeroshotpair": {
            "enabled": False,
            "qna_strategy_provider_config_data": {
                "class": "infy_content_generator.generator.provider.ZeroShotPairStrategyConfigData",
                "properties": {
                    "with_sub_context": False,
                    "que_type": "$..question_types.set_of_9"
                }
            },
            "qna_strategy_provider": {
                "class": "infy_content_generator.generator.provider.ZeroShotPairStrategyProvider",
                "properties": {
                    "prompt_files_path": {
                        "with_sub_context": None,
                        "without_sub_context": None
                    }
                }
            }
        },
        "strategy_two_stage": {
            "enabled": True,
            "qna_strategy_provider_config_data": {
                "class": "infy_content_generator.generator.provider.TwoStageStrategyConfigData",
                "properties": {
                    "que_type": "$..question_types.set_of_9"
                }
            },
            "qna_strategy_provider": {
                "class": "infy_content_generator.generator.provider.TwoStageStrategyProvider",
                "properties": {
                    "prompt_files_path": {
                        "question": None,
                        "answer": None
                    }
                }
            }
        },
        "strategy_two_stage_test_provided_que_prompt": {
            "enabled": False,
            "qna_strategy_provider_config_data": {
                "class": "infy_content_generator.generator.provider.TwoStageStrategyConfigData",
                "properties": {
                    "que_type": "$..question_types.set_of_9"
                }
            },
            "qna_strategy_provider": {
                "class": "infy_content_generator.generator.provider.TwoStageStrategyProvider",
                "properties": {
                    "prompt_files_path": {
                        "question": "/tests/question_prompt_test.txt",
                        "answer": None
                    }
                }
            }
        },

    },
    "llm": {
        "custom": {
            "meta-llama-3-3-70B-intruct_300_token": {
                "enabled": True,
                "configuration": {
                    "api_url": os.environ['CUSTOM_LLM_LLAMA_3_1_INFERENCE_URL'],
                    "model_name": 'Meta-Llama-3.3-70B-Instruct',
                    "headers": {"X-Cluster": "H100"},
                    "json_payload": {
                        "model": "/models/Meta-Llama-3.3-70B-Instruct",
                        "max_tokens": 300,
                        "temperature": 0.1,
                        "top_p": 0.9,
                        "presence_penalty": 0,
                        "frequency_penalty": 0
                    }
                },
                "llm_provider_class": "infy_content_generator.llm.provider.ChatLlmProvider",
                "llm_provider_config_data_class": "infy_content_generator.llm.provider.ChatLlmProviderConfigData"
            },
            "meta-llama-3-3-70B-intruct_1000_tokens": {
                "enabled": True,
                "configuration": {
                    "api_url": os.environ['CUSTOM_LLM_LLAMA_3_1_INFERENCE_URL'],
                    "model_name": 'Meta-Llama-3.3-70B-Instruct',
                    "headers": {"X-Cluster": "H100"},
                    "json_payload": {
                        "model": "/models/Meta-Llama-3.3-70B-Instruct",
                        "max_tokens": 1000,
                        "temperature": 0.9,
                        "top_p": 0.9,
                        "presence_penalty": 0,
                        "frequency_penalty": 0
                    },
                },

                "llm_provider_class": "infy_content_generator.llm.provider.ChatLlmProvider",
                "llm_provider_config_data_class": "infy_content_generator.llm.provider.ChatLlmProviderConfigData"
            }
        },
        "openai": {
            "enabled": False,
            "configuration": {
                "api_type": "azure",
                "api_url": os.environ['AZURE_OPENAI_SERVER_URL'],
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
            },
            "llm_provider_class": "infy_content_generator.llm.provider.OpenAILlmProvider",
            "llm_provider_config_data_class": "infy_content_generator.llm.provider.OpenAILlmProviderConfigData"
        }
    }

}


def test_qna_generation():
    """
    Test case to generate QNA data using the configuration
    """
    techniques = qna_generator_config.get("techniques")
    for technique in techniques:
        if technique.get("enabled"):
            qna_strategy_name = technique.get("qna_strategy_name")
            llm_providers = technique.get("llm_providers")
            llm_providers_dict = copy.deepcopy(llm_providers)

            # QNA STRATEGY OBJECT CREATION
            if isinstance(qna_strategy_name, str) and qna_strategy_name.startswith("$"):
                jsonpath_expr = parse(qna_strategy_name)
                qna_strategy_dict = [match.value for match in jsonpath_expr.find(
                    qna_generator_config)][0]
                if qna_strategy_dict.get("enabled"):
                    qna_strategy_provider_config_data = qna_strategy_dict.get(
                        "qna_strategy_provider_config_data")
                    qna_strategy_provider = qna_strategy_dict.get(
                        "qna_strategy_provider")

                    qna_strategy_provider_config_data_cls = qna_strategy_provider_config_data.get(
                        "class")
                    qna_strategy_config_data_cpy = copy.deepcopy(
                        qna_strategy_provider_config_data)
                    que_type = qna_strategy_config_data_cpy.get(
                        "properties").get("que_type")
                    if isinstance(que_type, str) and que_type.startswith("$"):
                        jsonpath_expr = parse(que_type)
                        qna_strategy_config_data_cpy["properties"]["que_type"] = [
                            match.value for match in jsonpath_expr.find(
                                qna_generator_config)][0]
                    # Converting the que_type dictionary to StrategyConfigData dictionary
                    que_type_dict = {}
                    for q_type_key, val in qna_strategy_config_data_cpy["properties"]["que_type"].items():
                        que_type_dict[q_type_key] = {'count': val}
                    qna_strategy_config_data_cpy["properties"]["que_type"] = que_type_dict

                    # Create an object of the Provider Config Data class
                    module_name, provider_config_data_cls_name = qna_strategy_provider_config_data_cls.rsplit(
                        '.', 1)
                    module = importlib.import_module(module_name)
                    qna_strategy_provider_config_data_cls_obj = getattr(
                        module, provider_config_data_cls_name)(**qna_strategy_config_data_cpy.get(
                            "properties"))

                    # Create an object of the Provider class
                    qna_strategy_provider_cls = qna_strategy_provider.get(
                        "class")
                    module_name, qna_strategy_provider_cls_name = qna_strategy_provider_cls.rsplit(
                        '.', 1)
                    module = importlib.import_module(module_name)
                    qna_strategy_provider_cls_obj = getattr(
                        module, qna_strategy_provider_cls_name)(qna_strategy_provider_config_data_cls_obj)
                    # IF PROMPT FILE PATH IS NOT NONE THEN SET PROMPT FILE PATH
                    prompt_files_path = qna_strategy_provider.get(
                        "properties").get("prompt_files_path")
                    if prompt_files_path:
                        PROMPT_TEMPLATE_DICT = qna_strategy_provider_cls_obj.get_prompt_template()
                        for prompt_file_key, prompt_file_value in prompt_files_path.items():
                            if prompt_file_value is not None:
                                prompt_file_abs_path = os.path.join(
                                    STORAGE_ROOT_PATH, prompt_file_value.lstrip('/'))
                                with open(prompt_file_abs_path, 'r', encoding='utf-8') as file:
                                    prompt_template = file.read()
                                PROMPT_TEMPLATE_DICT[prompt_file_key] = prompt_template

                        qna_strategy_provider_cls_obj.set_prompt_template(
                            PROMPT_TEMPLATE_DICT)

            # LLM PROVIDERs OBJECT's DICTONARY CREATION
            for llm_provider_key, llm_provider_value in llm_providers_dict.items():
                if isinstance(llm_provider_value, str) and llm_provider_value.startswith("$"):
                    jsonpath_expr = parse(llm_provider_value)
                    llm_dict = [
                        match.value for match in jsonpath_expr.find(qna_generator_config)][0]
                    if llm_dict.get("enabled"):
                        llm_config_data = llm_dict.get("configuration")
                        llm_provider_config_data_class = llm_dict.get(
                            "llm_provider_config_data_class")
                        llm_provider_class = llm_dict.get(
                            "llm_provider_class")
                        # Split the class name into module name and class name
                        module_name, provider_config_data_class_name = llm_provider_config_data_class.rsplit(
                            '.', 1)
                        # Import the module
                        module = importlib.import_module(module_name)
                        # Create an object of the Provider Config Data class
                        llm_provider_config_data_class_obj = getattr(
                            module, provider_config_data_class_name)(**llm_config_data)

                        # Create an object of the Provider class
                        module_name, provider_class_name = llm_provider_class.rsplit(
                            '.', 1)
                        module = importlib.import_module(module_name)
                        llm_provider_class_obj = getattr(module, provider_class_name)(
                            llm_provider_config_data_class_obj)

                        llm_providers_dict[llm_provider_key] = llm_provider_class_obj

            CONTEXT = """
            The annual financial report for Corporation for the fiscal year 2023 highlights significant growth and strategic advancements. The company reported a total revenue of $5 billion, marking a 10% increase from the previous year. This growth was driven by strong performance in the technology and healthcare sectors, which saw revenue increases of 15% and 12%, respectively.
            
            Operating income for the year was $1.2 billion, up from $1 billion in 2022, reflecting improved operational efficiencies and cost management. Net income stood at $900 million, a 20% increase year-over-year, resulting in earnings per share (EPS) of $3.50. The company's balance sheet remains robust, with total assets of $10 billion and total liabilities of $4 billion, resulting in a shareholder equity of $6 billion. Cash flow from operations was $1.5 billion, providing ample liquidity for future investments and shareholder returns.
            
            XYZ Corporation also announced a strategic acquisition of ABC Technologies, a leading provider of AI solutions, for $500 million. This acquisition is expected to enhance the company's technological capabilities and expand its market reach. Looking ahead, XYZ Corporation is focused on driving innovation, expanding its global footprint, and delivering sustainable growth. The company aims to achieve a revenue target of $6 billion for the fiscal year 2024, with continued emphasis on high-growth sectors and strategic investments.
            """
            metadata = {
                "company_name": "XYZ",
                "year": "2023"
            }
            # SET LLM PROVIDERS
            qna_strategy_provider_cls_obj.set_llm_provider(llm_providers_dict)
            qna_generator = infy_content_generator.generator.QnaGenerator(
                qna_strategy_provider_cls_obj)
            qna_response_data = qna_generator.generate_qna([CONTEXT], metadata)

            json_output = json.dumps(
                qna_response_data, default=lambda o: o.__dict__, indent=4)
            print(json_output)
            file_path = "C:/temp/qna_data_from_config.json"
            with open(file_path, 'w', encoding='utf8') as f:
                f.write(json_output)
            assert os.path.exists(file_path)

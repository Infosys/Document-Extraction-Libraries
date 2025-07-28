# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

"""Testing module"""
import os
import json
import pytest
import infy_content_generator


CONTAINER_ROOT_PATH = f"C:/temp/unittest/infy_content_generator/{__name__}/CONTAINER"
STORAGE_ROOT_PATH = f"C:/temp/unittest/infy_content_generator/{__name__}/STORAGE"


@pytest.fixture(scope='module', autouse=True)
def setup() -> dict:
    """Initialization method"""


def test_generate_qna_2():
    """This is a Test method for ZeroShotPairStrategy and OPEN_AI QnA generation"""

    llm_provider = infy_content_generator.llm.provider.OpenAILlmProvider(
        infy_content_generator.llm.provider.OpenAILlmProviderConfigData(
            **{
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
            })
    )
    strategy_config_data = infy_content_generator.generator.provider.ZeroShotPairStrategyConfigData(
        que_type={
            'procedural': {
                'count': 1
            },
            'factual': {
                'count': 0
            },
            'hypothetical': {
                'count': 0
            },
            'temporal': {
                'count': 0
            },
            'Cause and Effect': {
                'count': 1
            }
        },
        with_sub_context=True)
    qna_strategy_provider = infy_content_generator.generator.provider.ZeroShotPairStrategyProvider(
        strategy_config_data)
    qna_strategy_provider.set_llm_provider({'llm_provider_1': llm_provider})
    qna_generator = infy_content_generator.generator.QnaGenerator(
        qna_strategy_provider)
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

    input_data = [CONTEXT]
    qna_response_data = qna_generator.generate_qna(
        input_data)
    # Convert the list to JSON
    json_output = json.dumps(
        qna_response_data, default=lambda o: o.__dict__, indent=4)
    file_path = "C:/temp/qna_data_open_ai.json"
    with open(file_path, 'w', encoding='utf8') as f:
        f.write(json_output)
    print(json_output)
    assert os.path.exists(file_path)


def test_generate_qna_llm_response_parser_2():
    """This is a Test method for OPEN_AI QnA generation and WithSubContextResParserProvider to parse llm response"""

    llm_provider = infy_content_generator.llm.provider.OpenAILlmProvider(
        infy_content_generator.llm.provider.OpenAILlmProviderConfigData(
            **{
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
            })
    )
    strategy_config_data = infy_content_generator.generator.provider.ZeroShotPairStrategyConfigData(
        que_type={
            'procedural': {
                'count': 1
            },
            'factual': {
                'count': 0
            },
            'hypothetical': {
                'count': 0
            },
            'temporal': {
                'count': 0
            },
            'Cause and Effect': {
                'count': 1
            }
        },
        with_sub_context=True)
    llm_response_parser = infy_content_generator.generator.provider.WithSubContextResParserProvider()

    qna_strategy_provider = infy_content_generator.generator.provider.ZeroShotPairStrategyProvider(
        strategy_config_data, llm_response_parser)
    qna_strategy_provider.set_llm_provider({'llm_provider_1': llm_provider})

    qna_generator = infy_content_generator.generator.QnaGenerator(
        qna_strategy_provider)
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

    context_list = [CONTEXT]
    qna_response_data = qna_generator.generate_qna(
        context_list)
    json_output = json.dumps(
        qna_response_data, default=lambda o: o.__dict__, indent=4)
    print(json_output)
    file_path = "C:/temp/qna_data_custom_model_with_sub_context_llm_response_parser.json"
    with open(file_path, 'w', encoding='utf8') as f:
        f.write(json_output)
    assert os.path.exists(file_path)


def test_generate_qna_llm_response_parser_zero_short_strategy_with_user_prompt():
    """This is a Test method for OPEN_AI QnA generation and WithSubContextResParserProvider to parse llm response with user prompt"""

    llm_provider = infy_content_generator.llm.provider.OpenAILlmProvider(
        infy_content_generator.llm.provider.OpenAILlmProviderConfigData(
            **{
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
            })
    )
    with_sub_context = True
    strategy_config_data = infy_content_generator.generator.provider.ZeroShotPairStrategyConfigData(
        que_type={
            'procedural': {
                'count': 1
            },
            'factual': {
                'count': 0
            },
            'hypothetical': {
                'count': 0
            },
            'temporal': {
                'count': 0
            },
            'Cause and Effect': {
                'count': 1
            }
        },
        with_sub_context=True)
    llm_response_parser = infy_content_generator.generator.provider.WithSubContextResParserProvider()

    qna_strategy_provider = infy_content_generator.generator.provider.ZeroShotPairStrategyProvider(
        strategy_config_data, llm_response_parser)
    qna_strategy_provider.set_llm_provider({'llm_provider_1': llm_provider})
    # Note: if user provides a prompt file, then read the file and update the prompt template
    # user_provided_prompt_str = self.__file_sys_handler.read_file(
    #                     prompt_file_path)
    user_provided_prompt_str = """
    You are a examiner coming up with questions to ask on a quiz. 
    Given the following document, please generate the following type and number of questions and answer based on that document. Also give the source sentences of answer delimited by "XX" when the sentences are not consecutive.

    {que_type_and_count}

    Example Format:
    <Begin Document>
    ...
    <End Document>
    QUESTION: question here
    ANSWER: answer here
    TYPE: question type here
    SOURCE: source here

    These questions should be detailed and be based explicitly on information in the document. Begin!

    <Begin Document>
    {context}
    <End Document>
    """
    PROMPT_TEMPLATE_DICT = qna_strategy_provider.get_prompt_template()
    if with_sub_context:
        PROMPT_TEMPLATE_DICT['with_sub_context'] = user_provided_prompt_str
        qna_strategy_provider.set_prompt_template(
            PROMPT_TEMPLATE_DICT)
    else:
        PROMPT_TEMPLATE_DICT['without_sub_context'] = user_provided_prompt_str
        qna_strategy_provider.set_prompt_template(
            PROMPT_TEMPLATE_DICT)
    qna_generator = infy_content_generator.generator.QnaGenerator(
        qna_strategy_provider)
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

    context_list = [CONTEXT]
    qna_response_data = qna_generator.generate_qna(
        context_list)
    json_output = json.dumps(
        qna_response_data, default=lambda o: o.__dict__, indent=4)
    print(json_output)
    file_path = "C:/temp/qna_data_custom_model_with_sub_context_llm_response_parser_user_prompt.json"
    with open(file_path, 'w', encoding='utf8') as f:
        f.write(json_output)
    assert os.path.exists(file_path)


def test_generate_qna_two_stage_without_parser():
    """This is a Test method for Two Stage QnA generation"""

    def create_llm_provider1(max_tokens, temperature):
        """Helper function to create an LLM provider with specific settings"""
        return infy_content_generator.llm.provider.ChatLlmProvider(
            infy_content_generator.llm.provider.ChatLlmProviderConfigData(
                **{
                    "api_url": os.environ['CUSTOM_LLM_LLAMA_3_1_INFERENCE_URL'],
                    "model_name": 'Meta-Llama-3.3-70B-Instruct',
                    "headers":  {"X-Cluster": "H100"},
                    "json_payload": {
                        "model": "/models/Meta-Llama-3.3-70B-Instruct",
                        "max_tokens": max_tokens,
                        "temperature": temperature,
                        "top_p": 0.9,
                        "stop": None,
                        "presence_penalty": 0,
                        "frequency_penalty": 0,
                    }
                }
            ))

    llm_providers = {
        # For questions
        'llm_provider_1': create_llm_provider1(max_tokens=1000, temperature=0.9),
        # For answers
        'llm_provider_2': create_llm_provider1(max_tokens=300, temperature=0.1)
    }

    strategy_config_data = infy_content_generator.generator.provider.TwoStageStrategyConfigData(
        que_type={
            'subjective': {
                'count': 1
            },
            'analytical': {
                'count': 0
            },
            'deductive': {
                'count': 2
            },
            'objective': {
                'count': 0
            },
            'mathematical': {
                'count': 1
            }
        }
    )

    qna_strategy_provider = infy_content_generator.generator.provider.TwoStageStrategyProvider(
        strategy_config_data)
    qna_strategy_provider.set_llm_provider(llm_providers)

    qna_generator = infy_content_generator.generator.QnaGenerator(
        qna_strategy_provider)
    # Load custom prompt templates if provided by the user
    # PROMPT_TEMPLATE_DICT = qna_strategy_provider.get_prompt_template()
    # For question generation prompt
    # user_provided_question_prompt = self.__file_sys_handler.read_file(question_prompt_file_path)
    # PROMPT_TEMPLATE_DICT['question'] = user_provided_question_prompt
    # For answer generation prompt
    # user_provided_answer_prompt = self.__file_sys_handler.read_file(answer_prompt_file_path)
    # PROMPT_TEMPLATE_DICT['answer'] = user_provided_answer_prompt
    # qna_strategy_provider.set_prompt_template(PROMPT_TEMPLATE_DICT)
    CONTEXT = """
    The annual financial report for XYZ Corporation for the fiscal year 2023 highlights significant growth and strategic advancements. The company reported a total revenue of $5 billion, marking a 10% increase from the previous year. This growth was driven by strong performance in the technology and healthcare sectors, which saw revenue increases of 15% and 12%, respectively.
    
    Operating income for the year was $1.2 billion, up from $1 billion in 2022, reflecting improved operational efficiencies and cost management. Net income stood at $900 million, a 20% increase year-over-year, resulting in earnings per share (EPS) of $3.50. The company's balance sheet remains robust, with total assets of $10 billion and total liabilities of $4 billion, resulting in a shareholder equity of $6 billion. Cash flow from operations was $1.5 billion, providing ample liquidity for future investments and shareholder returns.
    
    XYZ Corporation also announced a strategic acquisition of ABC Technologies, a leading provider of AI solutions, for $500 million. This acquisition is expected to enhance the company's technological capabilities and expand its market reach. Looking ahead, XYZ Corporation is focused on driving innovation, expanding its global footprint, and delivering sustainable growth. The company aims to achieve a revenue target of $6 billion for the fiscal year 2024, with continued emphasis on high-growth sectors and strategic investments.
    """
    qna_response_data = qna_generator.generate_qna(
        [CONTEXT])
    json_output = json.dumps(
        qna_response_data, default=lambda o: o.__dict__, indent=4)
    print(json_output)
    file_path = "C:/temp/qna_data_two_stage_without_parser.json"
    with open(file_path, 'w', encoding='utf8') as f:
        f.write(json_output)
    assert os.path.exists(file_path)


def test_generate_qna_two_stage_with_parser():
    """This is a Test method for Two Stage QnA generation with meta data"""

    def create_llm_provider(max_tokens, temperature):
        """Helper function to create an LLM provider with specific settings"""
        return infy_content_generator.llm.provider.ChatLlmProvider(
            infy_content_generator.llm.provider.ChatLlmProviderConfigData(
                **{
                    "api_url": os.environ['CUSTOM_LLM_LLAMA_3_1_INFERENCE_URL'],
                    "model_name": 'Meta-Llama-3.3-70B-Instruct',
                    "headers":  {"X-Cluster": "H100"},
                    "json_payload": {
                        "model": "/models/Meta-Llama-3.3-70B-Instruct",
                        "max_tokens": max_tokens,
                        "temperature": temperature,
                        "top_p": 0.9,
                        "stop": None,
                        "presence_penalty": 0,
                        "frequency_penalty": 0,
                    }
                }
            ))

    llm_providers = {
        # For questions
        'llm_provider_1': create_llm_provider(max_tokens=1000, temperature=0.9),
        # For answers
        'llm_provider_2': create_llm_provider(max_tokens=300, temperature=0.1)
    }

    strategy_config_data = infy_content_generator.generator.provider.TwoStageStrategyConfigData(
        que_type={
            'subjective': {
                'count': 1
            },
            'analytical': {
                'count': 1
            },
            'deductive': {
                'count': 2
            },
            'objective': {
                'count': 0
            },
            'mathematical': {
                'count': 1
            }
        }

    )

    llm_response_parser = infy_content_generator.generator.provider.TwoStageQuestionResParserProvider()
    qna_strategy_provider = infy_content_generator.generator.provider.TwoStageStrategyProvider(
        strategy_config_data, llm_response_parser)
    qna_strategy_provider.set_llm_provider(llm_providers)
    qna_generator = infy_content_generator.generator.QnaGenerator(
        qna_strategy_provider)

    # Load custom prompt templates if provided by the user
    # PROMPT_TEMPLATE_DICT = qna_strategy_provider.get_prompt_template()
    # For question generation prompt
    # user_provided_question_prompt = self.__file_sys_handler.read_file(question_prompt_file_path)
    # PROMPT_TEMPLATE_DICT['question'] = user_provided_question_prompt
    # For answer generation prompt
    # user_provided_answer_prompt = self.__file_sys_handler.read_file(answer_prompt_file_path)
    # PROMPT_TEMPLATE_DICT['answer'] = user_provided_answer_prompt
    # qna_strategy_provider.set_prompt_template(PROMPT_TEMPLATE_DICT)
    CONTEXT = """
    The annual financial report for XYZ Corporation for the fiscal year 2023 highlights significant growth and strategic advancements. The company reported a total revenue of $5 billion, marking a 10% increase from the previous year. This growth was driven by strong performance in the technology and healthcare sectors, which saw revenue increases of 15% and 12%, respectively.
    
    Operating income for the year was $1.2 billion, up from $1 billion in 2022, reflecting improved operational efficiencies and cost management. Net income stood at $900 million, a 20% increase year-over-year, resulting in earnings per share (EPS) of $3.50. The company's balance sheet remains robust, with total assets of $10 billion and total liabilities of $4 billion, resulting in a shareholder equity of $6 billion. Cash flow from operations was $1.5 billion, providing ample liquidity for future investments and shareholder returns.
    
    XYZ Corporation also announced a strategic acquisition of ABC Technologies, a leading provider of AI solutions, for $500 million. This acquisition is expected to enhance the company's technological capabilities and expand its market reach. Looking ahead, XYZ Corporation is focused on driving innovation, expanding its global footprint, and delivering sustainable growth. The company aims to achieve a revenue target of $6 billion for the fiscal year 2024, with continued emphasis on high-growth sectors and strategic investments.
    """
    metadata = {
        "Document Title": "xyz",
        "Section": "",
        "Sub Section": "",
        "Header": "",
        "Footer": "",
    }

    qna_response_data = qna_generator.generate_qna([CONTEXT], metadata)
    json_output = json.dumps(
        qna_response_data, default=lambda o: o.__dict__, indent=4)
    print(json_output)
    file_path = "C:/temp/qna_data_two_stage_with_parser.json"
    with open(file_path, 'w', encoding='utf8') as f:
        f.write(json_output)
    assert os.path.exists(file_path)


def test_generate_qna_two_stage_with_parser_with_user_prompt():
    """This is a Test method for Two Stage QnA generation with meta data and user prompt"""

    def create_llm_provider(max_tokens, temperature):
        """Helper function to create an LLM provider with specific settings"""
        return infy_content_generator.llm.provider.ChatLlmProvider(
            infy_content_generator.llm.provider.ChatLlmProviderConfigData(
                **{
                    "api_url": os.environ['CUSTOM_LLM_LLAMA_3_1_INFERENCE_URL'],
                    "model_name": 'Meta-Llama-3.3-70B-Instruct',
                    "headers":  {"X-Cluster": "H100"},
                    "json_payload": {
                        "model": "/models/Meta-Llama-3.3-70B-Instruct",
                        "max_tokens": max_tokens,
                        "temperature": temperature,
                        "top_p": 0.9,
                        "stop": None,
                        "presence_penalty": 0,
                        "frequency_penalty": 0,
                    }
                }
            ))

    llm_providers = {
        # For questions
        'llm_provider_1': create_llm_provider(max_tokens=1000, temperature=0.9),
        # For answers
        'llm_provider_2': create_llm_provider(max_tokens=300, temperature=0.1)
    }

    strategy_config_data = infy_content_generator.generator.provider.TwoStageStrategyConfigData(
        que_type={
            'subjective': {
                'count': 1
            },
            'analytical': {
                'count': 1
            },
            'deductive': {
                'count': 2
            },
            'objective': {
                'count': 0
            },
            'mathematical': {
                'count': 1
            }
        }

    )

    llm_response_parser = infy_content_generator.generator.provider.TwoStageQuestionResParserProvider()
    qna_strategy_provider = infy_content_generator.generator.provider.TwoStageStrategyProvider(
        strategy_config_data, llm_response_parser)
    qna_strategy_provider.set_llm_provider(llm_providers)
    qna_generator = infy_content_generator.generator.QnaGenerator(
        qna_strategy_provider)

    # Load custom prompt templates if provided by the user
    PROMPT_TEMPLATE_DICT = qna_strategy_provider.get_prompt_template()
    # For question generation prompt
    # user_provided_question_prompt = self.__file_sys_handler.read_file(question_prompt_file_path)
    user_provided_question_prompt = """
    # Document Analysis and Question Generation

    Metadata: {metadata}

    Given Context: {context}

    ## Phase 1: Context Analysis

    1. Content-First Analysis:
    - Identify key initiatives, actions, and outcomes from the context
    - Extract specific metrics, projects, and results
    - Note concrete examples and evidence presented
    - Identify underlying themes, implications, and connections
    
    2. Stakeholder & Purpose Analysis:
    - Identify primary audience and their information needs
    - Map key themes and decision-relevant information
    - Consider broader industry trends and implications suggested by content

    3. Integration Guidelines:
    If metadata available:
    - Use context as primary source, enhance with metadata
    - If metadata includes entity names (e.g., company, organization, industry), incorporate them meaningfully where they strengthen the question.
    
    If metadata unavailable:
    - Focus on specific initiatives, outcomes, and evidence
    - Frame questions around concrete actions and measurable results
    - Reference particular projects, programs, or strategies mentioned

    ## Phase 2: Question Generation

    Generate {question_count} questions of {question_type} type across these dimensions:

    - Focus on specific actions and measurable outcomes
    - Reference concrete examples from context
    - Explore deeper implications of presented information
    - Connect concepts to broader domain knowledge
    - Encourage reasoned analysis while staying grounded in context

    Examples:
    ✓ "What measurable impacts have resulted from [specific initiative mentioned]?"
    ✓ "How do the [specific projects described] contribute to [stated goals]?"
    ✓ "Given [specific approach mentioned], what potential challenges might arise in [related domain area]?"
    ✓ "How might [described strategy] impact [broader industry aspect] based on the implementation details provided?"

    Question Quality Guidelines:
    - Must be answerable using context as primary evidence
    - Can require domain knowledge for deeper analysis
    - Should encourage connecting multiple concepts

    Avoid:
    ✗ Questions completely detached from context
    ✗ Purely theoretical questions without contextual grounding
    ✗ Generic queries that don't require careful analysis
    ✗ Direct fact-extraction questions

    Output Format:
    Q1: [Question text]
    Type: [Question type]
    Context Support: [Relevant excerpt from context]
    """
    PROMPT_TEMPLATE_DICT['question'] = user_provided_question_prompt
    # For answer generation prompt
    # user_provided_answer_prompt = self.__file_sys_handler.read_file(answer_prompt_file_path)
    user_provided_answer_prompt = """
    Context: {context}

    Question: {question}

    Instructions for answer generation:

    1. Carefully read the provided context and question.
    2. Internally, follow these steps:
    a) Identify all relevant information from the context.
    b) Analyze how this information relates to the question.
    c) Consider any potential inconsistencies or ambiguities.
    d) Use logical reasoning to form connections and draw conclusions.
    e) If needed, make educated inferences based strictly on the given context.
    f) Formulate a clear and concise answer.

    3. Important: Do not output your step-by-step thought process.
    4. Provide only the final, direct answer to the question.
    5. Ensure your answer is based solely on the information given in the context.
    6. Do not repeat words or phrases from the question in your answer. Start your response directly with the relevant information.
    7. If the question cannot be answered based on the given context, state 'The provided information is insufficient to answer this question.'

    Your answer:
    """
    PROMPT_TEMPLATE_DICT['answer'] = user_provided_answer_prompt
    qna_strategy_provider.set_prompt_template(PROMPT_TEMPLATE_DICT)
    CONTEXT = """
    The annual financial report for XYZ Corporation for the fiscal year 2023 highlights significant growth and strategic advancements. The company reported a total revenue of $5 billion, marking a 10% increase from the previous year. This growth was driven by strong performance in the technology and healthcare sectors, which saw revenue increases of 15% and 12%, respectively.
    
    Operating income for the year was $1.2 billion, up from $1 billion in 2022, reflecting improved operational efficiencies and cost management. Net income stood at $900 million, a 20% increase year-over-year, resulting in earnings per share (EPS) of $3.50. The company's balance sheet remains robust, with total assets of $10 billion and total liabilities of $4 billion, resulting in a shareholder equity of $6 billion. Cash flow from operations was $1.5 billion, providing ample liquidity for future investments and shareholder returns.
    
    XYZ Corporation also announced a strategic acquisition of ABC Technologies, a leading provider of AI solutions, for $500 million. This acquisition is expected to enhance the company's technological capabilities and expand its market reach. Looking ahead, XYZ Corporation is focused on driving innovation, expanding its global footprint, and delivering sustainable growth. The company aims to achieve a revenue target of $6 billion for the fiscal year 2024, with continued emphasis on high-growth sectors and strategic investments.
    """
    metadata = {
        "company_name": "infosys",
        "year": "2023",

    }
    qna_response_data = qna_generator.generate_qna([CONTEXT], metadata)
    json_output = json.dumps(
        qna_response_data, default=lambda o: o.__dict__, indent=4)
    print(json_output)
    file_path = "C:/temp/qna_data_two_stage_with_parser_user_prompt.json"
    with open(file_path, 'w', encoding='utf8') as f:
        f.write(json_output)
    assert os.path.exists(file_path)

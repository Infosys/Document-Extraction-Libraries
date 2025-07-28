# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import json
import logging
from typing import Dict, Union
from infy_model_evaluation.llm.interface import ILLMResponseParserProvider


class JSONResponseParser(ILLMResponseParserProvider):
    """
    Parser for extracting scores and reasons from JSON-formatted LLM responses.

    Expected JSON format:
    {
        "score": float,
        "reasons": string
    }

    Returns a dictionary containing the metric score and reason.
    Handles various error cases and ensures scores are within valid range (0-3).
    """

    def __init__(self):
        """Initialize parser with logger"""
        self.__logger = logging.getLogger(__name__)

    def parse_llm_response(self, llm_response_txt: str, metric_name: str) -> Dict:
        """
        Parse JSON-formatted LLM response to extract score and reasons.

        Args:
            llm_response_txt (str): Raw JSON response text from LLM
            metric_name (str): Name of the metric being evaluated

        Returns:
            Dict: Dictionary containing:
                - metric_name: float (score value)
                - metric_name_reason: str (explanation or error message)

        Note:
            - Returns score of 0.0 with error message on parsing failures
            - Clamps scores to range [0.0, 3.0]
        """
        if not llm_response_txt:
            self.__logger.error(f"Empty response received for {metric_name}")
            return self.__create_error_response(metric_name, "Empty response received")

        try:
            # Clean and parse the JSON response
            cleaned_response = llm_response_txt.llm_response_txt.strip()
            response_dict = json.loads(cleaned_response)

            # Extract and validate score
            score = self.__extract_and_validate_score(response_dict)

            # Extract reasons or use default
            reasons = response_dict.get('reasons', '') or 'No reason provided'

            return {
                f"{metric_name}": score,
                f"{metric_name}_reason": reasons
            }

        except json.JSONDecodeError as e:
            error_msg = f"Failed to parse JSON response: {str(e)}"
            self.__logger.error(f"{error_msg} for {metric_name}")
            return self.__create_error_response(metric_name, error_msg)

        except Exception as e:
            error_msg = f"Error processing response: {str(e)}"
            self.__logger.error(f"{error_msg} for {metric_name}")
            return self.__create_error_response(metric_name, error_msg)

    def __extract_and_validate_score(self, response_dict: Dict) -> float:
        """
        Extract score from response dictionary and ensure it's within valid range.

        Args:
            response_dict (Dict): Parsed JSON response dictionary

        Returns:
            float: Validated score in range [0.0, 3.0]

        Raises:
            ValueError: If score is missing or invalid
        """
        try:
            score = float(response_dict.get('score', 0))
            # Clamp score to valid range
            return max(0.0, min(3.0, score))
        except (TypeError, ValueError) as e:
            raise ValueError(f"Invalid score format: {str(e)}")

    def __create_error_response(self, metric_name: str, error_message: str) -> Dict:
        """
        Create standardized error response dictionary.

        Args:
            metric_name (str): Name of the metric
            error_message (str): Description of the error

        Returns:
            Dict: Error response with 0.0 score and error message
        """
        return {
            f"{metric_name}": -1.0,
            f"{metric_name}_reason": error_message
        }

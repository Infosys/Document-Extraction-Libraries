# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import re
from typing import Union
from infy_model_evaluation.llm.interface import ILLMResponseParserProvider


class ScoreExtractorResParserProvider(ILLMResponseParserProvider):
    """
    Parser for extracting numerical scores from LLM responses.
    Handles various response formats like:
    - Plain number ("3")
    - Score with label ("Score: 3")
    - Sentence with score ("The score is 3")
    - Extra text before/after score

    Returns the extracted score as a string, maintaining original precision.
    Raises ValueError if no valid score is found or score is out of range.
    """

    def parse_llm_response(self, llm_response_txt: str) -> str:
        """
        Parse LLM response to extract numerical score.

        Args:
            llm_response_txt (str): Raw response text from LLM

        Returns:
            str: Extracted score as string

        Raises:
            ValueError: If no valid score found or score out of valid range
        """
        if not llm_response_txt:
            raise ValueError("Empty response received from LLM")

        # Clean and normalize the response
        cleaned_response = llm_response_txt.lower().strip()

        # Try different parsing strategies in order of preference
        score = (
            self._try_parse_direct_number(cleaned_response) or
            self._try_parse_score_label(cleaned_response) or
            self._try_parse_number_in_text(cleaned_response)
        )

        if score is None:
            raise ValueError(
                f"No valid score found in response: '{llm_response_txt}'"
            )

        return str(score)

    def _try_parse_direct_number(self, text: str) -> Union[float, None]:
        """
        Try to parse response as a direct number.
        Example: "3" or "2.5"

        Args:
            text (str): Normalized response text

        Returns:
            float or None: Parsed score if valid, None otherwise
        """
        try:
            # Match standalone number (including decimals)
            if re.match(r'^\d+\.?\d*$', text):
                return float(text)
        except ValueError:
            return None
        return None

    def _try_parse_score_label(self, text: str) -> Union[float, None]:
        """
        Try to parse response with explicit score label.
        Examples: "score: 3", "rating: 2.5"

        Args:
            text (str): Normalized response text

        Returns:
            float or None: Parsed score if valid, None otherwise
        """
        score_patterns = [
            r'score:\s*(\d+\.?\d*)',
            r'rating:\s*(\d+\.?\d*)',
            r'value:\s*(\d+\.?\d*)'
        ]

        for pattern in score_patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    return float(match.group(1))
                except ValueError:
                    continue
        return None

    def _try_parse_number_in_text(self, text: str) -> Union[float, None]:
        """
        Try to extract any number from text as last resort.
        Example: "The score for this response is 3"

        Args:
            text (str): Normalized response text

        Returns:
            float or None: Parsed score if valid, None otherwise
        """
        # Find all numbers in text
        numbers = re.findall(r'\d+\.?\d*', text)

        # If exactly one number found, assume it's the score
        if len(numbers) == 1:
            try:
                return float(numbers[0])
            except ValueError:
                return None
        return None

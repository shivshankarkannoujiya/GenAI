from typing import Dict, Any
from app.utils.logger import get_logger

logger = get_logger(__name__)


class TestCaseValidator:
    """Validator for generated test cases"""

    @staticmethod
    def validate_json_structure(data: Dict[str, Any]) -> bool:
        """
        Validate that the JSON response has the correct structure
        Args:
            data: Parsed JSON data from OpenAI
        Returns:
            True if valid, False otherwise
        """
        try:
            if "test_cases" not in data:
                logger.error("Missing 'test_cases' key in response")
                return False

            if "problem_summary" not in data:
                logger.error("Missing 'problem_summary' key in response")
                return False

            if not isinstance(data["test_cases"], list):
                logger.error("'test_cases' is not a list")
                return False

            for idx, test_case in enumerate(data["test_cases"]):
                if not isinstance(test_case, dict):
                    logger.error(f"Test case {idx} is not a dictionary")
                    return False

                required_fields = ["input", "expected_output"]
                for field in required_fields:
                    if field not in test_case:
                        logger.error(f"Test case {idx} missing '{field}' field")
                        return False

            return True

        except Exception as e:
            logger.error(f"Validation error: {str(e)}")
            return False

    @staticmethod
    def validate_test_case_content(test_case: Dict[str, Any]) -> bool:
        """
        Validate individual test case content
        Args:
            test_case: Individual test case dictionary
        Returns:
            True if valid, False otherwise
        """
        try:
            if not test_case.get("input", "").strip():
                logger.warning("Test case has empty input")
                return False

            if not test_case.get("expected_output", "").strip():
                logger.warning("Test case has empty expected_output")
                return False

            return True

        except Exception as e:
            logger.error(f"Test case content validation error: {str(e)}")
            return False

    @staticmethod
    def clean_json_response(response: str) -> str:
        """
        Clean OpenAI response to extract pure JSON
        Args:
            response: Raw response from OpenAI
        Returns:
            Cleaned JSON string
        """
        response = response.strip()

        # Remove ```json ... ```
        if response.startswith("```"):
            # Find the first newline after ```
            first_newline = response.find("\n")
            if first_newline != -1:
                response = response[first_newline + 1 :]

            # Remove trailing ```
            if response.endswith("```"):
                response = response[:-3]

        # Remove any leading/trailing whitespace
        response = response.strip()

        return response


validator = TestCaseValidator()

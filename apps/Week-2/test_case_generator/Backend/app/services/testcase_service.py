import json
from datetime import datetime
from typing import Dict, Any

from app.core.openai_client import openai_client
from app.core.prompts import get_testcase_generation_prompt, get_system_prompt
from app.models.schemas import TestCaseRequest, TestCaseResponse, TestCase
from app.services.validator import validator
from app.utils.logger import get_logger

logger = get_logger(__name__)


class TestCaseService:
    """Service for handling test case generation logic"""

    async def generate_test_cases(self, request: TestCaseRequest) -> TestCaseResponse:
        """
        Generate test cases using OpenAI
        Args:
            request: TestCaseRequest with problem details
        Returns:
            TestCaseResponse with generated test cases
        Raises:
            ValueError: If response parsing fails or validation fails
            Exception: If OpenAI API call fails
        """
        try:
            logger.info(
                f"Generating {request.num_test_cases} test cases for {request.problem_type} problem"
            )

            # Build the prompt
            user_prompt = get_testcase_generation_prompt(
                problem_description=request.problem_description,
                difficulty=request.difficulty.value,
                problem_type=request.problem_type.value,
                num_cases=request.num_test_cases,
                constraints=request.constraints,
                include_edge_cases=request.include_edge_cases,
            )

            # Prepare messages for OpenAI
            messages = [
                {"role": "system", "content": get_system_prompt()},
                {"role": "user", "content": user_prompt},
            ]

            logger.debug(f"Prompt length: {len(user_prompt)} characters")

            # Call OpenAI
            response = await openai_client.generate_completion(messages)

            logger.debug(f"Received response of length: {len(response)} characters")

            # Parse and validate response
            parsed_data = self._parse_openai_response(response)

            # Validate structure
            if not validator.validate_json_structure(parsed_data):
                raise ValueError("Invalid JSON structure in OpenAI response")

            # Validate individual test cases
            valid_test_cases = []
            for test_case in parsed_data["test_cases"]:
                if validator.validate_test_case_content(test_case):
                    valid_test_cases.append(test_case)
                else:
                    logger.warning(f"Skipping invalid test case: {test_case}")

            if not valid_test_cases:
                raise ValueError("No valid test cases generated")

            # Create response object
            response_data = TestCaseResponse(
                test_cases=[TestCase(**tc) for tc in valid_test_cases],
                problem_summary=parsed_data["problem_summary"],
                generated_at=datetime.utcnow().isoformat(),
            )

            logger.info(f"Successfully generated {len(valid_test_cases)} test cases")

            return response_data

        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {str(e)}")
            raise ValueError(f"Failed to parse OpenAI response as JSON: {str(e)}")
        except ValueError as e:
            logger.error(f"Validation error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in generate_test_cases: {str(e)}")
            raise Exception(f"Failed to generate test cases: {str(e)}")

    def _parse_openai_response(self, response: str) -> Dict[str, Any]:
        """
        Parse and clean OpenAI response
        Args:
            response: Raw response string from OpenAI
        Returns:
            Parsed JSON data as dictionary
        Raises:
            json.JSONDecodeError: If parsing fails
        """
        # Clean the response
        clean_response = validator.clean_json_response(response)

        logger.debug(f"Cleaned response: {clean_response[:200]}...")

        # Parse JSON
        try:
            data = json.loads(clean_response)
            return data
        except json.JSONDecodeError:
            # Try to extract JSON from response if it's wrapped in text
            # Look for { ... } pattern
            import re

            json_match = re.search(r"\{.*\}", clean_response, re.DOTALL)
            if json_match:
                try:
                    data = json.loads(json_match.group(0))
                    logger.warning("Extracted JSON from wrapped response")
                    return data
                except json.JSONDecodeError:
                    pass

            # If all else fails, raise the original error
            raise


testcase_service = TestCaseService()

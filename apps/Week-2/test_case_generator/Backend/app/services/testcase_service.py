import json
from datetime import datetime
from app.core.openai_client import openai_client
from app.core.prompts import get_testcase_generation_prompt
from app.models.schemas import TestCaseRequest, TestCaseResponse


class TestCaseService:
    async def generate_test_cases(self, request: TestCaseRequest) -> TestCaseResponse:

        prompt = get_testcase_generation_prompt(
            problem_description=request.problem_description,
            difficulty=request.difficulty.value,
            problem_type=request.problem_type.value,
            num_cases=request.num_test_cases,
            constraints=request.constraints,
            include_edge_cases=request.include_edge_cases,
        )

        messages = [
            {
                "role": "system",
                "content": "You are an expert coding problem test case generator. Always return valid JSON.",
            },
            {"role": "user", "content": prompt},
        ]

        response = await openai_client.generate_completion(messages)

        # Parse JSON response
        # Clean response if it has markdown

        try:
            clean_response = response.strip()
            if clean_response.startswith("```"):
                clean_response = clean_response.split("```")[1]
                if clean_response.startswith("json"):
                    clean_response = clean_response[4:]
                clean_response = clean_response.strip()
            data = json.loads(clean_response)

            return TestCaseResponse(
                test_cases=data["test_cases"],
                problem_summary=data["problem_summary"],
                generated_at=datetime.utcnow().isoformat(),
            )
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse OpenAI response: {str(e)}")


testcase_service = TestCaseService()

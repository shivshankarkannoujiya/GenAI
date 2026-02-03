def get_testcase_generation_prompt(
    problem_description: str,
    difficulty: str,
    problem_type: str,
    num_cases: int,
    constraints: str = None,
    include_edge_cases: bool = True,
) -> str:
    edge_case_instruction = (
    """
    - Include edge cases like empty inputs, maximum values, minimum values
    - Include corner cases specific to the problem type
    """
        if include_edge_cases
        else ""
    )

    constraint_section = f"\n\nConstraints:\n{constraints}" if constraints else ""

    return f"""You are an expert test case generator for coding problems.

Problem Description:
{problem_description}

Difficulty: {difficulty}
Problem Type: {problem_type}{constraint_section}

Generate {num_cases} diverse test cases for this problem.

Requirements:
- Include simple cases to verify basic functionality
- Include complex cases to test algorithm correctness{edge_case_instruction}
- Ensure test cases cover different scenarios
- Format each test case clearly with input and expected output

Return ONLY a valid JSON object with this exact structure:
{{
    "test_cases": [
        {{
            "input": "describe input here",
            "expected_output": "describe expected output here",
            "explanation": "brief explanation of what this tests"
        }}
    ],
    "problem_summary": "one sentence summary of the problem"
}}

Do not include any markdown formatting, code blocks, or extra text. Return only the raw JSON.
"""

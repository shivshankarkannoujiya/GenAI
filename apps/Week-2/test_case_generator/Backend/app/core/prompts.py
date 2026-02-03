from typing import Optional


def get_testcase_generation_prompt(
    problem_description: str,
    difficulty: str,
    problem_type: str,
    num_cases: int,
    constraints: Optional[str] = None,
    include_edge_cases: bool = True,
) -> str:
    """
    Generate a detailed prompt for OpenAI to create test cases

    Args:
        problem_description: Description of the coding problem
        difficulty: Problem difficulty (easy/medium/hard)
        problem_type: Type of problem (array, string, tree, etc.)
        num_cases: Number of test cases to generate
        constraints: Optional constraints for the problem
        include_edge_cases: Whether to include edge cases

    Returns:
        Formatted prompt string
    """

    # Build edge case instruction
    edge_case_instruction = ""
    if include_edge_cases:
        edge_case_instruction = """
- Include edge cases such as:
  * Empty inputs (when applicable)
  * Single element inputs
  * Maximum constraint values
  * Minimum constraint values
  * Negative numbers (if applicable)
  * Duplicate values
  * All same values
- Include corner cases specific to the problem type"""

    # Build constraints section
    constraint_section = ""
    if constraints:
        constraint_section = f"""

**Constraints:**
{constraints}"""

    # Difficulty-specific guidance
    difficulty_guidance = {
        "easy": "Focus on straightforward test cases that verify basic functionality. Include simple happy paths.",
        "medium": "Include a mix of basic and complex scenarios. Test multiple edge cases and algorithmic correctness.",
        "hard": "Create challenging test cases that stress-test the algorithm. Include maximum constraints and tricky edge cases.",
    }

    difficulty_note = difficulty_guidance.get(difficulty.lower(), "")

    prompt = f"""You are an expert test case generator for coding interview problems, similar to LeetCode.

**Problem Description:**
{problem_description}

**Problem Details:**
- Difficulty Level: {difficulty.upper()}
- Problem Type: {problem_type.replace('_', ' ').title()}{constraint_section}

**Your Task:**
Generate exactly {num_cases} diverse and comprehensive test cases for this problem.

**Requirements:**
1. **Diversity**: Each test case should test different aspects of the problem
2. **Coverage**: Include simple cases, complex cases, and boundary conditions{edge_case_instruction}
3. **Clarity**: Provide clear inputs and expected outputs
4. **Explanation**: Explain what each test case validates

**Difficulty Guidance:**
{difficulty_note}

**Output Format:**
You MUST return ONLY a valid JSON object with this EXACT structure (no markdown, no code blocks, no extra text):

{{
    "test_cases": [
        {{
            "input": "Clear description of input (e.g., 'nums = [2,7,11,15], target = 9')",
            "expected_output": "Expected output (e.g., '[0,1]' or '2')",
            "explanation": "Brief explanation of what this test case validates"
        }}
    ],
    "problem_summary": "One concise sentence summarizing the problem"
}}

**Important:**
- Return ONLY the JSON object
- Do NOT include ```json or ``` markers
- Do NOT include any additional text before or after the JSON
- Ensure all JSON is properly formatted and valid
- Generate exactly {num_cases} test cases"""

    return prompt


def get_system_prompt() -> str:
    """
    Get the system prompt for OpenAI

    Returns:
        System prompt string
    """
    return """You are an expert coding interview test case generator. You specialize in creating comprehensive, diverse, and well-explained test cases for algorithmic problems similar to those found on LeetCode, HackerRank, and other competitive programming platforms.

Your test cases should:
- Be clear and unambiguous
- Cover various scenarios (basic, complex, edge cases)
- Include helpful explanations
- Follow proper formatting conventions
- Always return valid JSON without any markdown formatting

You have deep knowledge of:
- Data structures (arrays, trees, graphs, linked lists, etc.)
- Algorithms (sorting, searching, dynamic programming, etc.)
- Edge cases and boundary conditions
- Time and space complexity considerations"""

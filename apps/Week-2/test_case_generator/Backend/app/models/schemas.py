from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import datetime
from enum import Enum


class DifficultyLevel(str, Enum):
    """Difficulty levels for coding problems"""

    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class ProblemType(str, Enum):
    """Types of coding problems"""

    ARRAY = "array"
    STRING = "string"
    TREE = "tree"
    GRAPH = "graph"
    DYNAMIC_PROGRAMMING = "dynamic_programming"
    GREEDY = "greedy"
    BACKTRACKING = "backtracking"
    LINKED_LIST = "linked_list"
    HASH_TABLE = "hash_table"
    STACK = "stack"
    QUEUE = "queue"
    HEAP = "heap"
    BINARY_SEARCH = "binary_search"
    SLIDING_WINDOW = "sliding_window"
    TWO_POINTERS = "two_pointers"
    RECURSION = "recursion"
    SORTING = "sorting"
    BIT_MANIPULATION = "bit_manipulation"


class TestCaseRequest(BaseModel):
    """Request model for test case generation"""

    problem_description: str = Field(
        ...,
        min_length=10,
        max_length=5000,
        description="Description of the coding problem",
    )
    difficulty: DifficultyLevel = Field(
        ..., description="Difficulty level of the problem"
    )
    problem_type: ProblemType = Field(..., description="Type/category of the problem")
    num_test_cases: int = Field(
        default=5, ge=1, le=20, description="Number of test cases to generate"
    )
    constraints: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Optional constraints for the problem",
    )
    include_edge_cases: bool = Field(
        default=True, description="Whether to include edge cases in test generation"
    )

    @field_validator("problem_description")
    @classmethod
    def validate_problem_description(cls, v: str) -> str:
        """Validate that problem description is not just whitespace"""
        if not v.strip():
            raise ValueError("Problem description cannot be empty or just whitespace")
        return v.strip()

    @field_validator("constraints")
    @classmethod
    def validate_constraints(cls, v: Optional[str]) -> Optional[str]:
        """Validate and clean constraints"""
        if v is not None:
            v = v.strip()
            if not v:
                return None
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "problem_description": "Given an array of integers nums and an integer target, return indices of the two numbers that add up to target.",
                "difficulty": "easy",
                "problem_type": "array",
                "num_test_cases": 5,
                "constraints": "2 <= nums.length <= 10^4\n-10^9 <= nums[i] <= 10^9\n-10^9 <= target <= 10^9",
                "include_edge_cases": True,
            }
        }


class TestCase(BaseModel):
    """Individual test case model"""

    input: str = Field(..., min_length=1, description="Input for the test case")
    expected_output: str = Field(
        ..., min_length=1, description="Expected output for the test case"
    )
    explanation: Optional[str] = Field(
        default=None, description="Explanation of what this test case validates"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "input": "nums = [2,7,11,15], target = 9",
                "expected_output": "[0,1]",
                "explanation": "Because nums[0] + nums[1] == 9, we return [0, 1]",
            }
        }


class TestCaseResponse(BaseModel):
    """Response model for test case generation"""

    test_cases: List[TestCase] = Field(
        ..., min_length=1, description="Generated test cases"
    )
    problem_summary: str = Field(
        ..., min_length=1, description="Brief summary of the problem"
    )
    generated_at: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="Timestamp when test cases were generated",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "test_cases": [
                    {
                        "input": "nums = [2,7,11,15], target = 9",
                        "expected_output": "[0,1]",
                        "explanation": "Basic case with solution at the beginning",
                    },
                    {
                        "input": "nums = [3,2,4], target = 6",
                        "expected_output": "[1,2]",
                        "explanation": "Solution not at the start",
                    },
                ],
                "problem_summary": "Two Sum Problem - Find indices of two numbers that add to target",
                "generated_at": "2026-02-04T10:30:00.000000",
            }
        }


class ErrorResponse(BaseModel):
    """Error response model"""

    detail: str = Field(..., description="Error message")
    error_type: Optional[str] = Field(default=None, description="Type of error")

    class Config:
        json_schema_extra = {
            "example": {
                "detail": "Failed to generate test cases",
                "error_type": "OpenAIError",
            }
        }


class HealthResponse(BaseModel):
    """Health check response model"""

    status: str = Field(..., description="Service status")
    service: str = Field(..., description="Service name")
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="Current timestamp",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "service": "testcase-generator",
                "timestamp": "2026-02-04T10:30:00.000000",
            }
        }

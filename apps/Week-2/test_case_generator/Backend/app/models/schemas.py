from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


class DifficultyLevel(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class ProblemType(str, Enum):
    DP = "dynamic_programming"
    TREE = "tree"
    ARRAY = "array"
    GRAPH = "graph"
    GREEDY = "greedy"
    STRING = "string"
    BACKTRACKING = "backtracking"


class TestCaseRequest(BaseModel):
    problem_description: str = Field(..., min_length=10)
    difficulty: DifficultyLevel
    problem_type: ProblemType
    num_test_cases: int = Field(default=5, ge=1, le=20)
    constraints: Optional[str] = None
    include_edge_cases: bool = True


class TestCase(BaseModel):
    input: str
    expected_output: str
    explanation: Optional[str] = None


class TestCaseResponse(BaseModel):
    test_cases: List[TestCase]
    problem_summary: str
    generated_at: str

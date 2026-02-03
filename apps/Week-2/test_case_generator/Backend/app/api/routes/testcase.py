from fastapi import APIRouter, HTTPException, status
from typing import Dict

from app.models.schemas import (
    TestCaseRequest,
    TestCaseResponse,
    ErrorResponse,
    HealthResponse,
)
from app.services.testcase_service import testcase_service
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/testcases", tags=["testcases"])


@router.post(
    "/generate",
    response_model=TestCaseResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {
            "description": "Test cases generated successfully",
            "model": TestCaseResponse,
        },
        422: {
            "description": "Validation error or invalid response format",
            "model": ErrorResponse,
        },
        500: {"description": "Internal server error", "model": ErrorResponse},
    },
    summary="Generate Test Cases",
    description="Generate test cases for a coding problem using AI",
)
async def generate_test_cases(request: TestCaseRequest) -> TestCaseResponse:
    try:
        logger.info(
            f"Received request to generate test cases for {request.problem_type} problem"
        )

        result = await testcase_service.generate_test_cases(request)

        logger.info(f"Successfully generated {len(result.test_cases)} test cases")
        return result

    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)
        )
    except Exception as e:
        logger.error(f"Internal error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Health Check",
    description="Check if the test case generation service is healthy",
)
async def health_check() -> HealthResponse:
    logger.debug("Health check requested")
    return HealthResponse(status="healthy", service="testcase-generator")


@router.get(
    "/supported-types",
    response_model=Dict[str, list],
    status_code=status.HTTP_200_OK,
    summary="Get Supported Problem Types",
    description="Get list of supported problem types and difficulties",
)
async def get_supported_types() -> Dict[str, list]:
    from app.models.schemas import DifficultyLevel, ProblemType

    return {
        "difficulties": [d.value for d in DifficultyLevel],
        "problem_types": [
            {"value": p.value, "label": p.value.replace("_", " ").title()}
            for p in ProblemType
        ],
    }

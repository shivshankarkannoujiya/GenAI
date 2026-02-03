from fastapi import APIRouter, HTTPException
from app.models.schemas import TestCaseRequest, TestCaseResponse
from app.services.testcase_service import testcase_service


router = APIRouter(prefix="/testcases", tags=["testcases"])


@router.post("/generate", response_model=TestCaseResponse)
async def generate_test_cases(request: TestCaseRequest):
    try:
        result = await testcase_service.generate_test_cases(request)
        return result
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "testcase-generator"}

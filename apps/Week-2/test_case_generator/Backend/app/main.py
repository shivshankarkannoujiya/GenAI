from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.api.routes import testcase


settings = get_settings()

app = FastAPI(
    title="AlgoNex Test Case Generator",
    description="AI-powered test case generation for coding problems",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(testcase.router, prefix=settings.api_v1_prefix)


@app.get("/")
async def root():
    return {"message": "AlgoNex Test Case Generator API", "version": "1.0.0"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

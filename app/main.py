"""
DSAMaster Code Execution API - FastAPI Backend

Sandboxed code execution for Python, Java, C++
"""

import json
import logging
import os
from typing import Any, Dict, List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .executor import execute_in_sandbox, sanitize_code

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("dsamaster-api")

# FastAPI app
app = FastAPI(
    title="DSAMaster Code Execution API",
    description="Docker-sandboxed execution for coding challenges",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------

class TestCase(BaseModel):
    input: Any
    expected: Any


class RunRequest(BaseModel):
    language: str  # python, java, cpp
    code: str
    test_cases: List[TestCase]
    function_name: str


class TestResult(BaseModel):
    input: Any
    expected: Any
    actual: Any
    passed: bool
    execution_time_ms: int
    error: str | None


class RunResponse(BaseModel):
    results: List[TestResult]
    all_passed: bool
    language: str
    function_name: str


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "ok",
        "timestamp": __import__("datetime").datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }


@app.post("/api/run", response_model=RunResponse)
async def run_code(request: RunRequest):
    """
    Execute code against test cases in a Docker sandbox.
    """
    supported = ["python", "java", "cpp"]
    if request.language not in supported:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported language: {request.language}. Supported: {supported}"
        )

    try:
        sanitize_code(request.code, request.language)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    results = []
    all_passed = True

    for test_case in request.test_cases:
        execution = await execute_in_sandbox(
            request.code,
            request.language,
            request.function_name,
            test_case.input
        )

        passed = (
            not execution["timed_out"]
            and not execution["error"]
            and not execution["parse_error"]
            and json.dumps(execution["result"]) == json.dumps(test_case.expected)
        )

        if not passed:
            all_passed = False

        results.append(TestResult(
            input=test_case.input,
            expected=test_case.expected,
            actual=execution["result"],
            passed=passed,
            execution_time_ms=execution["execution_time_ms"],
            error=execution["error"] or execution["parse_error"] or None
        ))

    return RunResponse(
        results=results,
        all_passed=all_passed,
        language=request.language,
        function_name=request.function_name
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "3001"))
    )

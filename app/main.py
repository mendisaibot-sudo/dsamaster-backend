"""
DSAMaster Code Execution API - FastAPI Backend

Sandboxed code execution for Python, Java, C++
Plus Blog Admin API
"""

import json
import logging
import os
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from pydantic import BaseModel

from .executor import execute_in_sandbox, sanitize_code

# Import routers
from .routers import auth as auth_router
from .routers import blog
from .routers import progress
from .routers import admin
from .routers import content as content_router

# Import models for DB init
from .db import engine
from .models.user import Base as UserBase
from .models.content import Base as ContentBase

# Import progress updater
from .routers.progress import update_progress_after_submission
from .db import get_db

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("dsamaster-api")

# Initialize database tables on startup
UserBase.metadata.create_all(bind=engine)
ContentBase.metadata.create_all(bind=engine)

# FastAPI app
app = FastAPI(
    title="DSAMaster Code Execution API",
    description="Docker-sandboxed execution for coding challenges + Blog + Auth API",
    version="2.0.0"
)

# CORS
app.add_middleware(
    SessionMiddleware, 
    secret_key=os.getenv("JWT_SECRET_KEY", "dev-secret-key"),
    max_age=3600
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "https://dsamaster.de,http://localhost:5173").split(","),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Include routers
app.include_router(auth_router.router)
app.include_router(blog.router)
app.include_router(progress.router)
app.include_router(admin.router)
app.include_router(content_router.router)

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
        "version": "2.0.0"
    }


@app.post("/api/run", response_model=RunResponse)
async def run_code(request: RunRequest):
    """Execute code against test cases in a Docker sandbox."""
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
    total_runtime = 0

    for test_case in request.test_cases:
        execution = await execute_in_sandbox(
            request.code,
            request.language,
            test_case.input,
            request.function_name
        )

        passed = (
            not execution["timed_out"]
            and not execution["error"]
            and not execution["parse_error"]
            and json.dumps(execution["result"]) == json.dumps(test_case.expected)
        )

        if not passed:
            all_passed = False

        total_runtime += execution["execution_time_ms"]

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

"""Progress tracking endpoints."""

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db import get_db
from app.models.user import User, UserProgress, UserStats, Submission, Problem
from app.utils.auth import verify_token

router = APIRouter(prefix="/api/progress", tags=["progress"])

def get_current_user(request, db: Session = Depends(get_db)):
    from fastapi import Request
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Bearer token required")
    
    payload = verify_token(auth_header[7:])
    user_id = payload["sub"]
    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

@router.get("/stats")
async def get_user_stats(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get current user's overall statistics."""
    stats = db.query(UserStats).filter(UserStats.user_id == current_user.id).first()
    if not stats:
        stats = UserStats(user_id=current_user.id)
        db.add(stats)
        db.commit()
    
    return {
        "success": True,
        "data": stats.to_dict()
    }

@router.get("/problems")
async def get_user_progress(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get user's progress on all problems."""
    progress = db.query(UserProgress).filter(
        UserProgress.user_id == current_user.id
    ).all()
    
    return {
        "success": True,
        "data": [p.to_dict() for p in progress]
    }

@router.get("/problem/{problem_id}")
async def get_problem_progress(
    problem_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's progress on a specific problem."""
    progress = db.query(UserProgress).filter(
        UserProgress.user_id == current_user.id,
        UserProgress.problem_id == problem_id
    ).first()
    
    if not progress:
        return {
            "success": True,
            "data": {
                "user_id": str(current_user.id),
                "problem_id": problem_id,
                "status": "not_started",
                "attempts_count": 0
            }
        }
    
    return {
        "success": True,
        "data": progress.to_dict()
    }

@router.get("/submissions")
async def get_submissions(
    problem_id: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's submission history."""
    query = db.query(Submission).filter(Submission.user_id == current_user.id)
    if problem_id:
        query = query.filter(Submission.problem_id == problem_id)
    
    submissions = query.order_by(Submission.created_at.desc()).all()
    return {
        "success": True,
        "data": [s.to_dict() for s in submissions]
    }

# Internal helper to update progress (called from /api/run endpoint)
def update_progress_after_submission(
    user_id: str,
    problem_id: str,
    language: str,
    code: str,
    status: str,
    runtime_ms: int,
    passed_tests: int,
    total_tests: int,
    error_message: str = None,
    db: Session = None
):
    """Update user progress after a code submission."""
    if db is None:
        from app.db import get_db_context
        with get_db_context() as db:
            return _do_update(db, user_id, problem_id, language, code, status, runtime_ms, passed_tests, total_tests, error_message)
    return _do_update(db, user_id, problem_id, language, code, status, runtime_ms, passed_tests, total_tests, error_message)

def _do_update(db, user_id, problem_id, language, code, status, runtime_ms, passed_tests, total_tests, error_message):
    # Create submission record
    submission = Submission(
        user_id=user_id,
        problem_id=problem_id,
        language=language,
        code=code,
        status=status,
        runtime_ms=runtime_ms,
        passed_tests=passed_tests,
        total_tests=total_tests,
        error_message=error_message
    )
    db.add(submission)
    
    # Update or create progress
    progress = db.query(UserProgress).filter(
        UserProgress.user_id == user_id,
        UserProgress.problem_id == problem_id
    ).first()
    
    if not progress:
        progress = UserProgress(
            user_id=user_id,
            problem_id=problem_id,
            status="attempted",
            attempts_count=1
        )
        db.add(progress)
    else:
        progress.attempts_count += 1
        progress.last_attempt_at = datetime.utcnow()
    
    # If accepted, update to solved
    if status == "accepted":
        progress.status = "solved"
        if not progress.solved_at:
            progress.solved_at = datetime.utcnow()
        if progress.best_runtime_ms is None or runtime_ms < progress.best_runtime_ms:
            progress.best_runtime_ms = runtime_ms
    
    # Update user stats
    stats = db.query(UserStats).filter(UserStats.user_id == user_id).first()
    if not stats:
        stats = UserStats(user_id=user_id)
        db.add(stats)
    
    stats.total_attempts += 1
    
    if status == "accepted" and progress.attempts_count == 1:
        # First time solving this problem
        stats.total_solved += 1
        
        # Get problem difficulty
        problem = db.query(Problem).filter(Problem.id == problem_id).first()
        if problem:
            if problem.difficulty == "easy":
                stats.easy_solved += 1
            elif problem.difficulty == "medium":
                stats.medium_solved += 1
            elif problem.difficulty == "hard":
                stats.hard_solved += 1
        
        # Update streak
        stats.last_solved_at = datetime.utcnow()
        _update_streak(stats)
        if stats.current_streak > stats.longest_streak:
            stats.longest_streak = stats.current_streak
    
    db.commit()
    return submission

def _update_streak(stats):
    """Update current streak based on last solve date."""
    from datetime import date
    today = date.today()
    
    if stats.last_solved_at:
        last_solve = stats.last_solved_at.date()
        if last_solve == today:
            pass  # Already solved today, no streak change
        elif (today - last_solve).days == 1:
            stats.current_streak += 1
        else:
            stats.current_streak = 1
    else:
        stats.current_streak = 1

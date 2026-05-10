from datetime import datetime

from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.content import Lesson, UserExerciseProgress, UserLessonProgress
from app.models.user import User
from app.routers.auth import get_current_user

router = APIRouter(prefix="/api/progress", tags=["progress"])


@router.get("/me")
async def get_my_progress(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return all progress for the current user."""
    lesson_progress = (
        db.query(UserLessonProgress)
        .filter(UserLessonProgress.user_id == current_user.id)
        .all()
    )
    exercise_progress = (
        db.query(UserExerciseProgress)
        .filter(UserExerciseProgress.user_id == current_user.id)
        .all()
    )
    return {
        "user_id": str(current_user.id),
        "lesson_progress": [lp.to_dict() for lp in lesson_progress],
        "exercise_progress": [ep.to_dict() for ep in exercise_progress],
    }


@router.post("/lesson/{slug}")
async def track_lesson_progress(
    slug: str,
    body: dict = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update or create lesson progress entry."""
    lesson = db.query(Lesson).filter(Lesson.slug == slug).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    progress = (
        db.query(UserLessonProgress)
        .filter(
            UserLessonProgress.user_id == current_user.id,
            UserLessonProgress.lesson_id == lesson.id,
        )
        .first()
    )

    if not progress:
        progress = UserLessonProgress(
            user_id=current_user.id,
            lesson_id=lesson.id,
            status="in_progress",
            started_at=datetime.utcnow(),
        )
        db.add(progress)

    new_status = body.get("status")
    if new_status in ("in_progress", "completed"):
        progress.status = new_status
        if new_status == "completed" and not progress.completed_at:
            progress.completed_at = datetime.utcnow()

    last_position = body.get("last_position")
    if last_position is not None:
        progress.last_position = str(last_position)

    db.commit()
    db.refresh(progress)
    return progress.to_dict()


@router.post("/lesson/{slug}/exercises")
async def track_exercise_progress(
    slug: str,
    body: dict = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Track exercise completion and auto-mark lesson complete if all exercises done."""
    lesson = db.query(Lesson).filter(Lesson.slug == slug).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    exercise_id = body.get("exercise_id")
    answer = body.get("answer")
    is_correct = body.get("correct", False)

    if not exercise_id:
        raise HTTPException(status_code=400, detail="exercise_id is required")

    # Upsert exercise progress
    ep = (
        db.query(UserExerciseProgress)
        .filter(
            UserExerciseProgress.user_id == current_user.id,
            UserExerciseProgress.exercise_id == exercise_id,
        )
        .first()
    )

    if not ep:
        ep = UserExerciseProgress(
            user_id=current_user.id,
            lesson_id=lesson.id,
            exercise_id=exercise_id,
        )
        db.add(ep)

    ep.attempts += 1
    ep.last_answer = str(answer) if answer is not None else None
    if is_correct:
        ep.correct = True
        if not ep.completed_at:
            ep.completed_at = datetime.utcnow()

    db.commit()
    db.refresh(ep)

    # Auto-mark lesson as completed if all exercises are correct
    all_exercises = lesson.exercises
    if all_exercises:
        completed_exercise_ids = {
            str(row.exercise_id)
            for row in db.query(UserExerciseProgress)
            .filter(
                UserExerciseProgress.user_id == current_user.id,
                UserExerciseProgress.lesson_id == lesson.id,
                UserExerciseProgress.correct == True,
            )
            .all()
        }
        all_exercise_ids = {str(ex.id) for ex in all_exercises}

        if completed_exercise_ids == all_exercise_ids:
            lp = (
                db.query(UserLessonProgress)
                .filter(
                    UserLessonProgress.user_id == current_user.id,
                    UserLessonProgress.lesson_id == lesson.id,
                )
                .first()
            )
            if not lp:
                lp = UserLessonProgress(
                    user_id=current_user.id,
                    lesson_id=lesson.id,
                    status="in_progress",
                    started_at=datetime.utcnow(),
                )
                db.add(lp)
            lp.status = "completed"
            if not lp.completed_at:
                lp.completed_at = datetime.utcnow()
            db.commit()
            db.refresh(lp)

    return ep.to_dict()

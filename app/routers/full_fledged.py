"""Full-fledged DSAMaster content API endpoints."""
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.content import Category, Exercise, Lesson, Topic, UserLessonProgress
from app.models.user import User
from app.routers.auth import get_current_user

router = APIRouter(prefix="/api", tags=["full-fledged"])


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def _get_lesson_by_slug(db: Session, slug: str) -> Optional[Lesson]:
    return db.query(Lesson).filter(Lesson.slug == slug).first()


# ---------------------------------------------------------------------------
# Categories
# ---------------------------------------------------------------------------

@router.get("/categories")
async def list_categories(db: Session = Depends(get_db)):
    """List all categories with topic counts and total lesson counts."""
    cats = db.query(Category).order_by(Category.order_index).all()
    return [
        {
            **cat.to_dict(),
            "topic_count": len(cat.topics),
            "lesson_count": sum(len(t.lessons) for t in cat.topics),
        }
        for cat in cats
    ]


@router.get("/categories/{slug}")
async def get_category(slug: str, db: Session = Depends(get_db)):
    """Get a single category with all topics."""
    cat = db.query(Category).filter(Category.slug == slug).first()
    if not cat:
        return JSONResponse(status_code=404, content={"detail": "Category not found"})
    return {
        **cat.to_dict(),
        "topics": [
            {
                **t.to_dict(),
                "lesson_count": len(t.lessons),
            }
            for t in cat.topics
        ],
    }


# ---------------------------------------------------------------------------
# Topics
# ---------------------------------------------------------------------------

@router.get("/topics/{slug}")
async def get_topic(slug: str, db: Session = Depends(get_db)):
    """Get a topic with all lessons."""
    topic = db.query(Topic).filter(Topic.slug == slug).first()
    if not topic:
        return JSONResponse(status_code=404, content={"detail": "Topic not found"})
    return {
        **topic.to_dict(),
        "category": topic.category.to_dict(),
        "lessons": [l.to_dict() for l in topic.lessons],
    }


# ---------------------------------------------------------------------------
# Lessons
# ---------------------------------------------------------------------------

@router.get("/lessons/{slug}")
async def get_lesson(slug: str, db: Session = Depends(get_db)):
    """Get full lesson detail with content blocks, code examples, and exercises."""
    lesson = db.query(Lesson).filter(Lesson.slug == slug).first()
    if not lesson:
        return JSONResponse(status_code=404, content={"detail": "Lesson not found"})
    return lesson.to_detail_dict()


@router.get("/lessons/search")
async def search_lessons(
    q: Optional[str] = Query(None, description="Search query (title or content)"),
    category: Optional[str] = Query(None, description="Filter by category slug"),
    difficulty: Optional[str] = Query(None, description="Filter by difficulty: beginner/intermediate/advanced"),
    db: Session = Depends(get_db),
):
    """Search lessons with text query and optional filters."""
    query = db.query(Lesson).outerjoin(Topic).outerjoin(Category)

    if q:
        q_lower = f"%{q.lower()}%"
        query = query.filter(
            (func.lower(Lesson.title).ilike(q_lower))
            | (func.lower(Lesson.content_json.cast(str)).ilike(q_lower))
        )

    if difficulty:
        query = query.filter(Lesson.difficulty == difficulty.lower())

    if category:
        query = query.filter(Category.slug == category)

    lessons = query.order_by(Lesson.order_index).all()

    results = []
    for lesson in lessons:
        item = lesson.to_dict()
        item["topic"] = lesson.topic.to_dict() if lesson.topic else None
        item["category"] = lesson.topic.category.to_dict() if lesson.topic else None
        results.append(item)

    return {
        "query": q,
        "category": category,
        "difficulty": difficulty,
        "count": len(results),
        "results": results,
    }


# ---------------------------------------------------------------------------
# Progress
# ---------------------------------------------------------------------------

@router.post("/progress/{lesson_slug}")
async def mark_lesson_complete(
    lesson_slug: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark a lesson as completed for the current user."""
    lesson = _get_lesson_by_slug(db, lesson_slug)
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
            status="completed",
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
        )
        db.add(progress)
    else:
        if progress.status != "completed":
            progress.status = "completed"
        if not progress.completed_at:
            progress.completed_at = datetime.utcnow()

    db.commit()
    db.refresh(progress)
    return progress.to_dict()


@router.get("/progress/stats")
async def get_progress_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get user progress statistics."""
    total_lessons = db.query(Lesson).count()

    lesson_progress = (
        db.query(UserLessonProgress)
        .filter(UserLessonProgress.user_id == current_user.id)
        .all()
    )

    completed = sum(1 for lp in lesson_progress if lp.status == "completed")
    in_progress = sum(1 for lp in lesson_progress if lp.status == "in_progress")
    not_started = max(0, total_lessons - completed - in_progress)

    # Category breakdown
    category_stats = {}
    cats = db.query(Category).all()
    for cat in cats:
        cat_lessons = [l for t in cat.topics for l in t.lessons]
        cat_slugs = {l.id for l in cat_lessons}
        cat_completed = sum(
            1 for lp in lesson_progress
            if lp.status == "completed" and lp.lesson_id in cat_slugs
        )
        category_stats[cat.slug] = {
            "name": cat.name,
            "total": len(cat_lessons),
            "completed": cat_completed,
            "percentage": round(cat_completed / max(len(cat_slugs), 1) * 100, 1),
        }

    # Difficulty breakdown
    difficulty_stats = {}
    for diff in ("beginner", "intermediate", "advanced"):
        diff_count = db.query(Lesson).filter(Lesson.difficulty == diff).count()
        diff_completed = (
            db.query(UserLessonProgress)
            .join(Lesson)
            .filter(
                UserLessonProgress.user_id == current_user.id,
                UserLessonProgress.status == "completed",
                Lesson.difficulty == diff,
            )
            .count()
        )
        difficulty_stats[diff] = {
            "total": diff_count,
            "completed": diff_completed,
            "percentage": round(diff_completed / max(diff_count, 1) * 100, 1),
        }

    # Recent completed
    recent = (
        db.query(UserLessonProgress)
        .filter(
            UserLessonProgress.user_id == current_user.id,
            UserLessonProgress.status == "completed",
        )
        .order_by(desc(UserLessonProgress.completed_at))
        .limit(5)
        .all()
    )

    return {
        "user": {
            "id": str(current_user.id),
            "name": current_user.display_name,
        },
        "overall": {
            "total_lessons": total_lessons,
            "completed": completed,
            "in_progress": in_progress,
            "not_started": not_started,
            "percentage": round(completed / max(total_lessons, 1) * 100, 1),
        },
        "by_category": category_stats,
        "by_difficulty": difficulty_stats,
        "recent_completed": [lp.to_dict() for lp in recent],
    }


@router.get("/progress/leaderboard")
async def get_leaderboard(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    """Get top learners by completed lessons count."""
    subq = (
        db.query(
            UserLessonProgress.user_id.label("uid"),
            func.count(UserLessonProgress.id).label("completed_count"),
        )
        .filter(UserLessonProgress.status == "completed")
        .group_by(UserLessonProgress.user_id)
        .subquery()
    )

    leaders = (
        db.query(User, subq.c.completed_count)
        .join(subq, User.id == subq.c.uid)
        .order_by(desc(subq.c.completed_count))
        .limit(limit)
        .all()
    )

    return {
        "limit": limit,
        "leaderboard": [
            {
                "rank": i + 1,
                "user_id": str(user.id),
                "display_name": user.display_name,
                "completed_lessons": count,
                "avatar_url": user.avatar_url,
            }
            for i, (user, count) in enumerate(leaders)
        ],
    }

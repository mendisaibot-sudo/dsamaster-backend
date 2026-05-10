from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.content import Category, CodeExample, Exercise, Lesson, Topic

router = APIRouter(prefix="/api/content", tags=["content"])


@router.get("/categories")
async def get_categories(db: Session = Depends(get_db)):
    cats = db.query(Category).order_by(Category.order_index).all()
    return [
        {
            **cat.to_dict(),
            "topic_count": len(cat.topics),
            "lesson_count": sum(len(t.lessons) for t in cat.topics),
        }
        for cat in cats
    ]


@router.get("/categories/{slug}/topics")
async def get_category_topics(slug: str, db: Session = Depends(get_db)):
    cat = db.query(Category).filter(Category.slug == slug).first()
    if not cat:
        return JSONResponse(status_code=404, content={"detail": "Category not found"})
    return [t.to_dict() for t in cat.topics]


@router.get("/topics/{slug}/lessons")
async def get_topic_lessons(slug: str, db: Session = Depends(get_db)):
    topic = db.query(Topic).filter(Topic.slug == slug).first()
    if not topic:
        return JSONResponse(status_code=404, content={"detail": "Topic not found"})
    return [l.to_dict() for l in topic.lessons]


@router.get("/lessons")
async def get_all_lessons(db: Session = Depends(get_db)):
    lessons = db.query(Lesson).order_by(Lesson.order_index).all()
    return [l.to_dict() for l in lessons]


@router.get("/lessons/{slug}")
async def get_lesson(slug: str, db: Session = Depends(get_db)):
    lesson = db.query(Lesson).filter(Lesson.slug == slug).first()
    if not lesson:
        return JSONResponse(status_code=404, content={"detail": "Lesson not found"})
    return lesson.to_detail_dict()


@router.get("/lessons/{slug}/exercises")
async def get_lesson_exercises(slug: str, db: Session = Depends(get_db)):
    lesson = db.query(Lesson).filter(Lesson.slug == slug).first()
    if not lesson:
        return JSONResponse(status_code=404, content={"detail": "Lesson not found"})
    return [ex.to_dict() for ex in lesson.exercises]


@router.post("/lessons/{slug}/exercises/{exercise_id}/submit")
async def submit_exercise_answer(
    slug: str,
    exercise_id: str,
    payload: dict,
    db: Session = Depends(get_db),
):
    lesson = db.query(Lesson).filter(Lesson.slug == slug).first()
    if not lesson:
        return JSONResponse(status_code=404, content={"detail": "Lesson not found"})

    exercise = db.query(Exercise).filter(
        Exercise.id == exercise_id,
        Exercise.lesson_id == lesson.id,
    ).first()
    if not exercise:
        return JSONResponse(status_code=404, content={"detail": "Exercise not found for this lesson"})

    answer = str(payload.get("answer", "")).strip()
    correct = answer == str(exercise.correct_answer).strip()

    return {
        "exercise_id": str(exercise.id),
        "correct": correct,
        "correct_answer": str(exercise.correct_answer),
        "explanation": exercise.explanation,
        "hint": exercise.hint,
    }

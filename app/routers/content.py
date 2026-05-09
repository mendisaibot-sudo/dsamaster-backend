from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.content import Category, Topic, Lesson, CodeExample, Exercise

router = APIRouter(prefix="/api/content", tags=["content"])

@router.get("/categories")
def list_categories(db: Session = Depends(get_db)):
    cats = db.query(Category).order_by(Category.order_index).all()
    return [{"id": str(c.id), "name": c.name, "slug": c.slug, "description": c.description, "icon": c.icon, "color": c.color, "order_index": c.order_index, "topic_count": len(c.topics) if c.topics else 0} for c in cats]

@router.get("/categories/{slug}")
def get_category(slug: str, db: Session = Depends(get_db)):
    cat = db.query(Category).filter(Category.slug == slug).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    return {"id": str(cat.id), "name": cat.name, "slug": cat.slug, "description": cat.description, "icon": cat.icon, "color": cat.color, "order_index": cat.order_index, "topic_count": len(cat.topics) if cat.topics else 0}

@router.get("/categories/{slug}/topics")
def get_category_topics(slug: str, db: Session = Depends(get_db)):
    cat = db.query(Category).filter(Category.slug == slug).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    topics = db.query(Topic).filter(Topic.category_id == cat.id).order_by(Topic.order_index).all()
    return [{"id": str(t.id), "category_id": str(t.category_id), "name": t.name, "slug": t.slug, "description": t.description, "difficulty": t.difficulty, "estimated_hours": t.estimated_hours, "order_index": t.order_index, "lesson_count": len(t.lessons) if t.lessons else 0} for t in topics]

@router.get("/topics")
def list_topics(category_id: Optional[str] = None, db: Session = Depends(get_db)):
    q = db.query(Topic).order_by(Topic.order_index)
    if category_id:
        q = q.filter(Topic.category_id == category_id)
    topics = q.all()
    return [{"id": str(t.id), "category_id": str(t.category_id), "name": t.name, "slug": t.slug, "description": t.description, "difficulty": t.difficulty, "estimated_hours": t.estimated_hours, "order_index": t.order_index, "lesson_count": len(t.lessons) if t.lessons else 0} for t in topics]

@router.get("/topics/{slug}")
def get_topic(slug: str, db: Session = Depends(get_db)):
    topic = db.query(Topic).filter(Topic.slug == slug).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    return {"id": str(topic.id), "category_id": str(topic.category_id), "name": topic.name, "slug": topic.slug, "description": topic.description, "difficulty": topic.difficulty, "estimated_hours": topic.estimated_hours, "order_index": topic.order_index, "lesson_count": len(topic.lessons) if topic.lessons else 0}

@router.get("/topics/{slug}/lessons")
def get_topic_lessons(slug: str, db: Session = Depends(get_db)):
    topic = db.query(Topic).filter(Topic.slug == slug).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    lessons = db.query(Lesson).filter(Lesson.topic_id == topic.id).order_by(Lesson.order_index).all()
    return [{"id": str(l.id), "topic_id": str(l.topic_id), "title": l.title, "slug": l.slug, "difficulty": l.difficulty, "estimated_minutes": l.estimated_minutes, "order_index": l.order_index} for l in lessons]

@router.get("/lessons")
def list_lessons(topic_id: Optional[str] = None, db: Session = Depends(get_db)):
    q = db.query(Lesson).order_by(Lesson.order_index)
    if topic_id:
        q = q.filter(Lesson.topic_id == topic_id)
    lessons = q.all()
    return [{"id": str(l.id), "topic_id": str(l.topic_id), "title": l.title, "slug": l.slug, "difficulty": l.difficulty, "estimated_minutes": l.estimated_minutes, "order_index": l.order_index} for l in lessons]

@router.get("/lessons/{slug}")
def get_lesson(slug: str, db: Session = Depends(get_db)):
    lesson = db.query(Lesson).filter(Lesson.slug == slug).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    code_examples = db.query(CodeExample).filter(CodeExample.lesson_id == lesson.id).order_by(CodeExample.order_index).all()
    return {
        "id": str(lesson.id),
        "topic_id": str(lesson.topic_id),
        "title": lesson.title,
        "slug": lesson.slug,
        "difficulty": lesson.difficulty,
        "estimated_minutes": lesson.estimated_minutes,
        "order_index": lesson.order_index,
        "content": lesson.content_json,
        "code_examples": [{"id": str(ce.id), "language": ce.language, "code": ce.code, "explanation": ce.explanation, "output": ce.output} for ce in code_examples]
    }

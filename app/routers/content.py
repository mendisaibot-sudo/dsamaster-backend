from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.content import Category, Topic, Lesson, CodeExample
from app.models.user import UserLessonProgress
from app.utils.auth import verify_token
from datetime import datetime

router = APIRouter(prefix="/api/content", tags=["content"])

def get_current_user_optional(request: Request, db: Session = Depends(get_db)):
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None
    try:
        payload = verify_token(auth_header[7:])
        user_id = payload.get("sub")
        if not user_id:
            return None
        from app.models.user import User
        user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
        return user
    except Exception:
        return None

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
def get_category_topics(slug: str, db: Session = Depends(get_db), current_user = Depends(get_current_user_optional)):
    cat = db.query(Category).filter(Category.slug == slug).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    topics = db.query(Topic).filter(Topic.category_id == cat.id).order_by(Topic.order_index).all()
    result = []
    for t in topics:
        topic_data = {"id": str(t.id), "category_id": str(t.category_id), "name": t.name, "slug": t.slug, "description": t.description, "difficulty": t.difficulty, "estimated_hours": t.estimated_hours, "order_index": t.order_index, "lesson_count": len(t.lessons) if t.lessons else 0}
        if current_user:
            lesson_ids = [l.id for l in t.lessons]
            completed = db.query(UserLessonProgress).filter(
                UserLessonProgress.user_id == current_user.id,
                UserLessonProgress.lesson_id.in_(lesson_ids),
                UserLessonProgress.status == "completed"
            ).count()
            topic_data["completed_count"] = completed
        result.append(topic_data)
    return result

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
def get_topic_lessons(slug: str, db: Session = Depends(get_db), current_user = Depends(get_current_user_optional)):
    topic = db.query(Topic).filter(Topic.slug == slug).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    lessons = db.query(Lesson).filter(Lesson.topic_id == topic.id).order_by(Lesson.order_index).all()
    result = []
    for l in lessons:
        lesson_data = {"id": str(l.id), "topic_id": str(l.topic_id), "title": l.title, "slug": l.slug, "difficulty": l.difficulty, "estimated_minutes": l.estimated_minutes, "order_index": l.order_index}
        if current_user:
            prog = db.query(UserLessonProgress).filter(
                UserLessonProgress.user_id == current_user.id,
                UserLessonProgress.lesson_id == l.id
            ).first()
            lesson_data["status"] = prog.status if prog else "not_started"
            lesson_data["percent_complete"] = prog.percent_complete if prog else 0
        else:
            lesson_data["status"] = "not_started"
            lesson_data["percent_complete"] = 0
        result.append(lesson_data)
    return result

@router.get("/lessons")
def list_lessons(topic_id: Optional[str] = None, db: Session = Depends(get_db)):
    q = db.query(Lesson).order_by(Lesson.order_index)
    if topic_id:
        q = q.filter(Lesson.topic_id == topic_id)
    lessons = q.all()
    return [{"id": str(l.id), "topic_id": str(l.topic_id), "title": l.title, "slug": l.slug, "difficulty": l.difficulty, "estimated_minutes": l.estimated_minutes, "order_index": l.order_index} for l in lessons]

@router.get("/lessons/{slug}")
def get_lesson(slug: str, db: Session = Depends(get_db), current_user = Depends(get_current_user_optional)):
    lesson = db.query(Lesson).filter(Lesson.slug == slug).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    code_examples = db.query(CodeExample).filter(CodeExample.lesson_id == lesson.id).order_by(CodeExample.order_index).all()
    result = {
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
    if current_user:
        prog = db.query(UserLessonProgress).filter(
            UserLessonProgress.user_id == current_user.id,
            UserLessonProgress.lesson_id == lesson.id
        ).first()
        result["user_progress"] = {
            "status": prog.status if prog else "not_started",
            "percent_complete": prog.percent_complete if prog else 0,
            "time_spent_seconds": prog.time_spent_seconds if prog else 0
        }
    return result

@router.post("/lessons/{slug}/progress")
def update_lesson_progress(slug: str, data: dict, db: Session = Depends(get_db), current_user = Depends(get_current_user_optional)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Login required")
    lesson = db.query(Lesson).filter(Lesson.slug == slug).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    prog = db.query(UserLessonProgress).filter(
        UserLessonProgress.user_id == current_user.id,
        UserLessonProgress.lesson_id == lesson.id
    ).first()
    
    status = data.get("status", "in_progress")
    percent = data.get("percent_complete", 0)
    time_spent = data.get("time_spent_seconds", 0)
    
    if not prog:
        prog = UserLessonProgress(
            user_id=current_user.id,
            lesson_id=lesson.id,
            status=status,
            percent_complete=percent,
            time_spent_seconds=time_spent,
            started_at=datetime.utcnow() if status != "completed" else None,
            completed_at=datetime.utcnow() if status == "completed" else None,
            last_accessed_at=datetime.utcnow()
        )
        db.add(prog)
    else:
        prog.status = status
        prog.percent_complete = max(prog.percent_complete, percent)
        prog.time_spent_seconds += time_spent
        prog.last_accessed_at = datetime.utcnow()
        if status == "completed" and not prog.completed_at:
            prog.completed_at = datetime.utcnow()
        if status in ("in_progress", "completed") and not prog.started_at:
            prog.started_at = datetime.utcnow()
    
    db.commit()
    return {"success": True, "data": prog.to_dict()}

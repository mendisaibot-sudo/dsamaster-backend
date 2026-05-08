"""Content platform models for DSAMaster."""

import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, DateTime, Integer, Text, ForeignKey, CheckConstraint, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Category(Base):
    __tablename__ = "categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    icon = Column(String(100), nullable=True)
    color = Column(String(20), nullable=True)
    order_index = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    topics = relationship("Topic", back_populates="category", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "slug": self.slug,
            "description": self.description,
            "icon": self.icon,
            "color": self.color,
            "order_index": self.order_index,
            "topic_count": len(self.topics) if self.topics else 0,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Topic(Base):
    __tablename__ = "topics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    difficulty = Column(String(10), nullable=False)
    estimated_hours = Column(Integer, default=0)
    order_index = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (
        CheckConstraint("difficulty IN ('beginner','intermediate','advanced')", name="check_topic_difficulty"),
    )

    category = relationship("Category", back_populates="topics")
    lessons = relationship("Lesson", back_populates="topic", cascade="all, delete-orphan", order_by="Lesson.order_index")
    exercises = relationship("Exercise", back_populates="topic", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": str(self.id),
            "category_id": str(self.category_id),
            "name": self.name,
            "slug": self.slug,
            "description": self.description,
            "difficulty": self.difficulty,
            "estimated_hours": self.estimated_hours,
            "order_index": self.order_index,
            "lesson_count": len(self.lessons) if self.lessons else 0,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Lesson(Base):
    __tablename__ = "lessons"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    topic_id = Column(UUID(as_uuid=True), ForeignKey("topics.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(200), nullable=False)
    slug = Column(String(200), unique=True, nullable=False)
    content_json = Column(JSONB, nullable=False)
    difficulty = Column(String(10), nullable=False)
    estimated_minutes = Column(Integer, default=0)
    order_index = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        CheckConstraint("difficulty IN ('beginner','intermediate','advanced')", name="check_lesson_difficulty"),
    )

    topic = relationship("Topic", back_populates="lessons")
    code_examples = relationship("CodeExample", back_populates="lesson", cascade="all, delete-orphan", order_by="CodeExample.id")

    def to_dict(self):
        return {
            "id": str(self.id),
            "topic_id": str(self.topic_id),
            "title": self.title,
            "slug": self.slug,
            "difficulty": self.difficulty,
            "estimated_minutes": self.estimated_minutes,
            "order_index": self.order_index,
            "code_example_count": len(self.code_examples) if self.code_examples else 0,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def to_detail_dict(self):
        d = self.to_dict()
        d["content"] = self.content_json
        d["code_examples"] = [ex.to_dict() for ex in self.code_examples]
        return d


class CodeExample(Base):
    __tablename__ = "code_examples"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lesson_id = Column(UUID(as_uuid=True), ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False)
    language = Column(String(20), nullable=False)
    code = Column(Text, nullable=False)
    explanation = Column(Text, nullable=True)
    output = Column(Text, nullable=True)
    order_index = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    lesson = relationship("Lesson", back_populates="code_examples")

    def to_dict(self):
        return {
            "id": str(self.id),
            "lesson_id": str(self.lesson_id),
            "language": self.language,
            "code": self.code,
            "explanation": self.explanation,
            "output": self.output,
            "order_index": self.order_index,
        }


class Exercise(Base):
    __tablename__ = "exercises"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    topic_id = Column(UUID(as_uuid=True), ForeignKey("topics.id", ondelete="CASCADE"), nullable=False)
    type = Column(String(10), nullable=False)
    question = Column(Text, nullable=False)
    options_json = Column(JSONB, nullable=True)
    correct_answer = Column(Text, nullable=False)
    hint = Column(Text, nullable=True)
    difficulty = Column(String(10), default="beginner")
    order_index = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (
        CheckConstraint("type IN ('mcq','coding')", name="check_exercise_type"),
        CheckConstraint("difficulty IN ('beginner','intermediate','advanced')", name="check_exercise_difficulty"),
    )

    topic = relationship("Topic", back_populates="exercises")

    def to_dict(self):
        return {
            "id": str(self.id),
            "topic_id": str(self.topic_id),
            "type": self.type,
            "question": self.question,
            "options": self.options_json,
            "hint": self.hint,
            "difficulty": self.difficulty,
            "order_index": self.order_index,
        }


class UserLessonProgress(Base):
    __tablename__ = "user_lesson_progress"
    __table_args__ = (
        UniqueConstraint("user_id", "lesson_id", name="uix_user_lesson"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    lesson_id = Column(UUID(as_uuid=True), ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    time_spent_seconds = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "lesson_id": str(self.lesson_id),
            "completed": self.completed_at is not None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "time_spent_seconds": self.time_spent_seconds,
        }


class UserExerciseSubmission(Base):
    __tablename__ = "user_exercise_submissions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    exercise_id = Column(UUID(as_uuid=True), ForeignKey("exercises.id", ondelete="CASCADE"), nullable=False)
    answer = Column(Text, nullable=False)
    is_correct = Column(Integer, default=0)
    submitted_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "exercise_id": str(self.exercise_id),
            "is_correct": bool(self.is_correct),
            "submitted_at": self.submitted_at.isoformat() if self.submitted_at else None,
        }

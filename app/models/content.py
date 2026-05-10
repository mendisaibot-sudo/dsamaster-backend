import uuid
from datetime import datetime

from sqlalchemy import (
    UUID,
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.models.user import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    icon = Column(String(50), nullable=True)
    color = Column(String(20), nullable=True)
    order_index = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    topics = relationship("Topic", back_populates="category", cascade="all, delete-orphan", order_by="Topic.order_index")

    def to_dict(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "slug": self.slug,
            "description": self.description,
            "icon": self.icon,
            "color": self.color,
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
    order_index = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        CheckConstraint("difficulty IN ('beginner','intermediate','advanced')", name="check_topic_difficulty"),
    )

    category = relationship("Category", back_populates="topics")
    lessons = relationship("Lesson", back_populates="topic", cascade="all, delete-orphan", order_by="Lesson.order_index")
    exercises = relationship("Exercise", back_populates="topic", cascade="all, delete-orphan", order_by="Exercise.order_index")

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
    exercises = relationship("Exercise", back_populates="lesson", cascade="all, delete-orphan", order_by="Exercise.order_index")

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
        d["exercises"] = [ex.to_dict() for ex in self.exercises] if self.exercises else []
        return d


class CodeExample(Base):
    __tablename__ = "code_examples"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lesson_id = Column(UUID(as_uuid=True), ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False)
    language = Column(String(20), nullable=False)
    code = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    output = Column(Text, nullable=True)

    lesson = relationship("Lesson", back_populates="code_examples")

    def to_dict(self):
        return {
            "id": str(self.id),
            "lesson_id": str(self.lesson_id),
            "language": self.language,
            "code": self.code,
            "description": self.description,
            "output": self.output,
        }


class Exercise(Base):
    __tablename__ = "exercises"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    topic_id = Column(UUID(as_uuid=True), ForeignKey("topics.id", ondelete="CASCADE"), nullable=True)
    lesson_id = Column(UUID(as_uuid=True), ForeignKey("lessons.id", ondelete="CASCADE"), nullable=True)
    type = Column(String(10), nullable=False)
    question = Column(Text, nullable=False)
    options_json = Column(JSONB, nullable=True)
    correct_answer = Column(Text, nullable=False)
    hint = Column(Text, nullable=True)
    explanation = Column(Text, nullable=True)
    difficulty = Column(String(10), default="beginner")
    order_index = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (
        CheckConstraint("type IN ('mcq','coding')", name="check_exercise_type"),
        CheckConstraint("difficulty IN ('beginner','intermediate','advanced')", name="check_exercise_difficulty"),
    )

    topic = relationship("Topic", back_populates="exercises")
    lesson = relationship("Lesson", back_populates="exercises")

    def to_dict(self):
        return {
            "id": str(self.id),
            "topic_id": str(self.topic_id) if self.topic_id else None,
            "lesson_id": str(self.lesson_id) if self.lesson_id else None,
            "type": self.type,
            "question": self.question,
            "options": self.options_json,
            "hint": self.hint,
            "explanation": self.explanation,
            "difficulty": self.difficulty,
            "order_index": self.order_index,
        }


class UserLessonProgress(Base):
    __tablename__ = "user_lesson_progress"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    lesson_id = Column(UUID(as_uuid=True), ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(20), default="not_started")
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    last_position = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        CheckConstraint("status IN ('not_started','in_progress','completed')", name="check_lesson_status"),
        UniqueConstraint("user_id", "lesson_id", name="uix_user_lesson"),
    )

    user = relationship("User", back_populates="lesson_progress")

    def to_dict(self):
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "lesson_id": str(self.lesson_id),
            "status": self.status,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "last_position": self.last_position,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class UserExerciseProgress(Base):
    __tablename__ = "user_exercise_progress"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    lesson_id = Column(UUID(as_uuid=True), ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False)
    exercise_id = Column(UUID(as_uuid=True), ForeignKey("exercises.id", ondelete="CASCADE"), nullable=False)
    correct = Column(Boolean, default=False)
    attempts = Column(Integer, default=0)
    last_answer = Column(Text, nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("user_id", "exercise_id", name="uix_user_exercise"),
    )

    user = relationship("User", back_populates="exercise_progress")
    lesson = relationship("Lesson")
    exercise = relationship("Exercise")

    def to_dict(self):
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "lesson_id": str(self.lesson_id),
            "exercise_id": str(self.exercise_id),
            "correct": self.correct,
            "attempts": self.attempts,
            "last_answer": self.last_answer,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

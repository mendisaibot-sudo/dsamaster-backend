"""User model definitions."""

import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, DateTime, Boolean, Integer, Text, ForeignKey, UniqueConstraint, CheckConstraint
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    display_name = Column(String(100), nullable=False)
    role = Column(String(20), default='user', nullable=False)
    captcha_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=False)
    email_verified = Column(Boolean, default=False)
    oauth_provider = Column(String(20), nullable=True)
    oauth_id = Column(String(255), nullable=True, unique=True)
    avatar_url = Column(String(500), nullable=True)
    verification_token = Column(String(255), nullable=True)
    verification_token_expires_at = Column(DateTime(timezone=True), nullable=True)
    reset_token = Column(String(255), nullable=True)
    reset_token_expires_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    auth_tokens = relationship("AuthToken", back_populates="user", cascade="all, delete-orphan")
    progress = relationship("UserProgress", back_populates="user", cascade="all, delete-orphan")
    submissions = relationship("Submission", back_populates="user", cascade="all, delete-orphan")
    stats = relationship("UserStats", back_populates="user", uselist=False, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": str(self.id),
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "display_name": self.display_name,
            "role": self.role,
            "captcha_verified": self.captcha_verified,
            "is_active": self.is_active,
            "email_verified": self.email_verified,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login_at": self.last_login_at.isoformat() if self.last_login_at else None,
        }


class AuthToken(Base):
    __tablename__ = "auth_tokens"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token_hash = Column(String(255), unique=True, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    revoked_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="auth_tokens")


class Problem(Base):
    __tablename__ = "problems"

    id = Column(String(20), primary_key=True)
    title = Column(String(200), nullable=False)
    difficulty = Column(String(10), nullable=True)
    category = Column(String(50), nullable=False)
    function_name = Column(String(50), nullable=False)
    description = Column(Text, nullable=False)
    starter_code_js = Column(Text, nullable=True)
    starter_code_py = Column(Text, nullable=True)
    starter_code_java = Column(Text, nullable=True)
    starter_code_cpp = Column(Text, nullable=True)
    constraints = Column(JSONB, nullable=True)
    examples = Column(JSONB, nullable=True)
    test_cases = Column(JSONB, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        CheckConstraint("difficulty IN ('easy', 'medium', 'hard')", name="check_difficulty"),
    )


class UserProgress(Base):
    __tablename__ = "user_progress"
    __table_args__ = (
        UniqueConstraint("user_id", "problem_id", name="uix_user_problem"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    problem_id = Column(String(20), ForeignKey("problems.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(20), default='not_started', nullable=False)
    best_runtime_ms = Column(Integer, nullable=True)
    attempts_count = Column(Integer, default=0)
    solved_at = Column(DateTime(timezone=True), nullable=True)
    last_attempt_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="progress")

    def to_dict(self):
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "problem_id": self.problem_id,
            "status": self.status,
            "best_runtime_ms": self.best_runtime_ms,
            "attempts_count": self.attempts_count,
            "solved_at": self.solved_at.isoformat() if self.solved_at else None,
            "last_attempt_at": self.last_attempt_at.isoformat() if self.last_attempt_at else None,
        }


class Submission(Base):
    __tablename__ = "submissions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    problem_id = Column(String(20), ForeignKey("problems.id", ondelete="CASCADE"), nullable=False)
    language = Column(String(20), nullable=False)
    code = Column(Text, nullable=False)
    status = Column(String(20), nullable=False)
    runtime_ms = Column(Integer, nullable=True)
    passed_tests = Column(Integer, default=0)
    total_tests = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    user = relationship("User", back_populates="submissions")

    def to_dict(self):
        return {
            "id": str(self.id),
            "problem_id": self.problem_id,
            "language": self.language,
            "status": self.status,
            "runtime_ms": self.runtime_ms,
            "passed_tests": self.passed_tests,
            "total_tests": self.total_tests,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class UserStats(Base):
    __tablename__ = "user_stats"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    total_solved = Column(Integer, default=0)
    total_attempts = Column(Integer, default=0)
    easy_solved = Column(Integer, default=0)
    medium_solved = Column(Integer, default=0)
    hard_solved = Column(Integer, default=0)
    current_streak = Column(Integer, default=0)
    longest_streak = Column(Integer, default=0)
    last_solved_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="stats")

    def to_dict(self):
        return {
            "user_id": str(self.user_id),
            "total_solved": self.total_solved,
            "total_attempts": self.total_attempts,
            "easy_solved": self.easy_solved,
            "medium_solved": self.medium_solved,
            "hard_solved": self.hard_solved,
            "current_streak": self.current_streak,
            "longest_streak": self.longest_streak,
            "last_solved_at": self.last_solved_at.isoformat() if self.last_solved_at else None,
        }

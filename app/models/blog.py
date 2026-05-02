"""Pydantic models for blog posts."""

from typing import List
from pydantic import BaseModel, Field
from datetime import datetime


class BlogPost(BaseModel):
    """Blog post data model."""
    slug: str = Field(..., description="Unique URL-friendly identifier")
    title: str
    content: str = Field(..., description="Markdown or HTML content")
    excerpt: str = Field(..., description="Short description")
    date: str = Field(..., description="ISO format date (e.g. 2024-01-15)")
    readTime: int = Field(..., description="Estimated reading time in minutes")
    tags: List[str] = Field(default_factory=list)
    difficulty: str = Field(default="Medium", pattern="^(Easy|Medium|Hard)$")
    author: str = Field(default="Admin")
    published: bool = Field(default=True)
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

    class Config:
        json_schema_extra = {
            "example": {
                "slug": "arrays-101",
                "title": "Arrays 101",
                "content": "# Arrays 101\n\nArrays are...",
                "excerpt": "A beginner's guide to arrays",
                "date": "2024-01-15",
                "readTime": 5,
                "tags": ["arrays", "data-structures"],
                "difficulty": "Easy",
                "author": "Admin",
                "published": True,
                "created_at": "2024-01-15T10:00:00",
                "updated_at": "2024-01-15T10:00:00"
            }
        }


class BlogPostCreate(BaseModel):
    """Model for creating a new blog post."""
    slug: str = Field(..., min_length=1, max_length=100)
    title: str = Field(..., min_length=1, max_length=200)
    content: str
    excerpt: str = Field(..., max_length=500)
    date: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    readTime: int = Field(default=5, ge=1)
    tags: List[str] = Field(default_factory=list)
    difficulty: str = Field(default="Medium", pattern="^(Easy|Medium|Hard)$")
    author: str = Field(default="Admin")
    published: bool = Field(default=True)


class BlogPostUpdate(BaseModel):
    """Model for updating an existing blog post."""
    title: str | None = Field(default=None, min_length=1, max_length=200)
    content: str | None = None
    excerpt: str | None = Field(default=None, max_length=500)
    date: str | None = None
    readTime: int | None = Field(default=None, ge=1)
    tags: List[str] | None = None
    difficulty: str | None = Field(default=None, pattern="^(Easy|Medium|Hard)$")
    author: str | None = None
    published: bool | None = None


class BlogPostListResponse(BaseModel):
    """Response model for listing blog posts."""
    posts: List[BlogPost]
    total: int


class AuthResponse(BaseModel):
    """Response model for authentication."""
    success: bool
    data: dict | None = None
    error: str | None = None


class BlogResponse(BaseModel):
    """Generic response wrapper for blog operations."""
    success: bool
    data: dict | list | None = None
    error: str | None = None

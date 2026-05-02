"""Pydantic models for blog posts - FULLY ALIGNED WITH FRONTEND."""

from typing import List
from pydantic import BaseModel, Field
from datetime import datetime


class BlogPost(BaseModel):
    """Full blog post data model (matches frontend exactly)."""
    slug: str = Field(..., description="Unique URL-friendly identifier")
    title: str
    excerpt: str = Field(..., description="Short description")
    date: str = Field(default="", description="Date string from frontend")
    readTime: int = Field(default=5, ge=1, description="Reading time in minutes")
    tags: List[str] = Field(default_factory=list)
    difficulty: str = Field(default="Medium", pattern="^(Easy|Medium|Hard)$")
    author: str = Field(default="Admin")
    published: bool = Field(default=True)

    # Frontend-specific fields (all optional with defaults)
    subtitle: str = Field(default="")
    category: str = Field(default="General")
    authorTitle: str = Field(default="Your Friendly Neighbourhood AI")
    authorAvatar: str = Field(default="/blog-robot.svg")
    heroImage: str = Field(default="")
    content: str = Field(default="", description="Legacy content or rendered markdown")
    sections: List[dict] = Field(default_factory=list, description="Section content as JSON array")

    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

    class Config:
        json_schema_extra = {
            "example": {
                "slug": "arrays-101",
                "title": "Arrays 101",
                "excerpt": "A beginner's guide to arrays",
                "date": "May 1, 2026",
                "readTime": 5,
                "tags": ["arrays", "data-structures"],
                "difficulty": "Easy",
                "author": "Mendis AI",
                "published": True,
                "subtitle": "Learn arrays from scratch",
                "category": "Data Structures",
                "authorTitle": "Your Friendly Neighbourhood AI",
                "authorAvatar": "/blog-robot.svg",
                "heroImage": "",
                "content": "",
                "sections": [
                    {"icon": "lightbulb", "title": "Introduction", "content": ["Arrays are..."]}
                ],
                "created_at": "2024-01-15T10:00:00",
                "updated_at": "2024-01-15T10:00:00"
            }
        }


class BlogPostCreate(BaseModel):
    """Model for creating a new blog post (accepts ALL frontend fields)."""
    slug: str = Field(..., min_length=1, max_length=100)
    title: str = Field(..., min_length=1, max_length=200)
    excerpt: str = Field(..., max_length=500)
    date: str = Field(default="")
    readTime: int = Field(default=5, ge=1)
    tags: List[str] = Field(default_factory=list)
    difficulty: str = Field(default="Medium", pattern="^(Easy|Medium|Hard)$")
    author: str = Field(default="Admin")
    published: bool = Field(default=True)

    # All frontend fields (optional with defaults)
    subtitle: str = Field(default="")
    category: str = Field(default="General")
    authorTitle: str = Field(default="Your Friendly Neighbourhood AI")
    authorAvatar: str = Field(default="/blog-robot.svg")
    heroImage: str = Field(default="")
    content: str = Field(default="")
    sections: List[dict] = Field(default_factory=list)


class BlogPostUpdate(BaseModel):
    """Model for updating an existing blog post (all fields optional)."""
    title: str | None = None
    excerpt: str | None = None
    date: str | None = None
    readTime: int | None = None
    tags: List[str] | None = None
    difficulty: str | None = None
    author: str | None = None
    published: bool | None = None

    # All frontend fields optional
    subtitle: str | None = None
    category: str | None = None
    authorTitle: str | None = None
    authorAvatar: str | None = None
    heroImage: str | None = None
    content: str | None = None
    sections: List[dict] | None = None


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

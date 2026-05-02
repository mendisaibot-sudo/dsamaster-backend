"""Thread-safe JSON file storage for blog posts."""

import json
import os
import threading
from typing import List, Optional

from app.models.blog import BlogPost, BlogPostUpdate

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
BLOGS_FILE = os.path.join(DATA_DIR, "blogs.json")

# Thread lock for file operations
_file_lock = threading.Lock()


def _ensure_data_dir():
    """Create data directory and empty blogs.json if they don't exist."""
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(BLOGS_FILE):
        with open(BLOGS_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)


def _load_posts() -> List[dict]:
    """Load all blog posts from the JSON file."""
    _ensure_data_dir()
    with open(BLOGS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_posts(posts: list):
    """Save all blog posts to the JSON file."""
    with open(BLOGS_FILE, "w", encoding="utf-8") as f:
        json.dump(posts, f, indent=2, ensure_ascii=False)


def get_all_posts(include_unpublished: bool = False) -> List[BlogPost]:
    """Get all blog posts, optionally including unpublished ones."""
    with _file_lock:
        raw_posts = _load_posts()
    if not include_unpublished:
        raw_posts = [p for p in raw_posts if p.get("published", True)]
    posts = []
    for p in raw_posts:
        try:
            posts.append(BlogPost(**p))
        except Exception:
            continue
    return posts


def get_post_by_slug(slug: str, include_unpublished: bool = False) -> Optional[BlogPost]:
    """Get a single blog post by its slug."""
    posts = get_all_posts(include_unpublished)
    for post in posts:
        if post.slug == slug:
            return post
    return None


def create_post(post: BlogPost) -> BlogPost:
    """Create a new blog post. Raises ValueError if slug already exists."""
    with _file_lock:
        posts = _load_posts()
        # Check for duplicate slug
        for existing in posts:
            if existing.get("slug") == post.slug:
                raise ValueError(f"Blog post with slug '{post.slug}' already exists")
        posts.append(post.model_dump())
        _save_posts(posts)
    return post


def update_post(slug: str, update: BlogPostUpdate) -> Optional[BlogPost]:
    """Update an existing blog post by slug."""
    from datetime import datetime

    with _file_lock:
        posts = _load_posts()
        for i, existing in enumerate(posts):
            if existing.get("slug") == slug:
                update_data = update.model_dump(exclude_none=True)
                for key, value in update_data.items():
                    existing[key] = value
                existing["updated_at"] = datetime.utcnow().isoformat()
                posts[i] = existing
                _save_posts(posts)
                return BlogPost(**existing)
        return None


def delete_post(slug: str) -> bool:
    """Delete a blog post by slug. Returns True if deleted, False if not found."""
    with _file_lock:
        posts = _load_posts()
        for i, existing in enumerate(posts):
            if existing.get("slug") == slug:
                posts.pop(i)
                _save_posts(posts)
                return True
        return False


def slug_exists(slug: str) -> bool:
    """Check if a blog post with the given slug already exists."""
    with _file_lock:
        posts = _load_posts()
        return any(p.get("slug") == slug for p in posts)

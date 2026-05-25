#!/usr/bin/env python3
"""
DSAMaster Full Content Loader
Loads content_data/all_content.json into PostgreSQL database.
Idempotent - skips existing entries by slug.

Usage:
    python scripts/load_full_content.py

Requires DATABASE_URL env var or uses default.
"""
import json
import os
import sys
import uuid
from pathlib import Path

# Add app path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.content import Category, CodeExample, Exercise, Lesson, Topic
from app.models.user import Base

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/dsamaster")
CONTENT_FILE = Path(__file__).parent.parent / "content_data" / "all_content.json"

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
Session = sessionmaker(bind=engine)


def generate_slug(name: str, existing_slugs: set, prefix: str = "") -> str:
    """Generate a unique slug from a name."""
    base = "-".join(name.lower().split())
    if prefix:
        base = f"{prefix}-{base}"
    slug = base[:120]
    if slug not in existing_slugs:
        return slug
    for i in range(1, 1000):
        candidate = f"{slug}-{i}"
        if candidate not in existing_slugs:
            return candidate
    raise ValueError(f"Could not generate unique slug for '{name}'")


def load_all_content(filepath: Path) -> dict:
    """Load and normalize all_content.json."""
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Expected format: { category_slug: { category: {}, topics: [], lessons: [] } }
    return data


def ensure_content_json(lesson_raw: dict) -> dict:
    """Ensure lesson has content_json dict."""
    lesson = dict(lesson_raw)
    if "content_json" not in lesson and "content" in lesson:
        content = lesson.pop("content")
        if isinstance(content, str):
            lesson["content_json"] = {"blocks": [{"type": "text", "text": content}]}
        elif isinstance(content, dict):
            lesson["content_json"] = content
        else:
            lesson["content_json"] = {"blocks": []}
    if not lesson.get("content_json"):
        lesson["content_json"] = {"blocks": []}
    return lesson


def import_content(session, data: dict) -> dict:
    """Import all content into the database. Returns stats."""
    stats = {"categories": 0, "topics": 0, "lessons": 0, "code_examples": 0, "exercises": 0}

    existing_cat_slugs = {c[0] for c in session.query(Category.slug).all()}
    existing_topic_slugs = {t[0] for t in session.query(Topic.slug).all()}
    existing_lesson_slugs = {l[0] for l in session.query(Lesson.slug).all()}

    category_map = {}  # slug_or_name -> Category object
    topic_map = {}     # slug -> Topic object

    for cat_slug, cat_data in data.items():
        cat_info = cat_data.get("category", {})
        if not cat_info:
            cat_info = {"name": cat_slug.title(), "slug": cat_slug}

        # --- Create or get Category ---
        if cat_info["slug"] in existing_cat_slugs:
            category = session.query(Category).filter(Category.slug == cat_info["slug"]).first()
            print(f"  [ SKIP ] Category '{cat_info['slug']}' already exists")
        else:
            category = Category(
                id=uuid.uuid4(),
                name=cat_info.get("name", cat_slug.title()),
                slug=cat_info["slug"],
                description=cat_info.get("description"),
                icon=cat_info.get("icon"),
                color=cat_info.get("color"),
                order_index=cat_info.get("order_index", 0),
            )
            session.add(category)
            session.flush()
            existing_cat_slugs.add(category.slug)
            stats["categories"] += 1
            print(f"  [CREATE] Category '{category.slug}' ({category.name})")

        category_map[cat_slug] = category

        # --- Create or get Topics ---
        topics = cat_data.get("topics", [])
        for idx, topic_info in enumerate(topics):
            t_slug = topic_info["slug"]
            if t_slug in existing_topic_slugs:
                topic = session.query(Topic).filter(Topic.slug == t_slug).first()
                print(f"    [ SKIP ] Topic '{t_slug}' already exists")
            else:
                topic = Topic(
                    id=uuid.uuid4(),
                    category_id=category.id,
                    name=topic_info["name"],
                    slug=t_slug,
                    description=topic_info.get("description"),
                    difficulty=topic_info.get("difficulty", "beginner"),
                    estimated_hours=topic_info.get("estimated_hours", 0),
                    order_index=topic_info.get("order_index", idx),
                )
                session.add(topic)
                session.flush()
                existing_topic_slugs.add(topic.slug)
                stats["topics"] += 1
                print(f"    [CREATE] Topic '{topic.slug}' ({topic.name})")

            topic_map[t_slug] = topic

        # --- Create or get Lessons ---
        lessons = cat_data.get("lessons", [])
        for lesson_raw in lessons:
            lesson_data = ensure_content_json(lesson_raw)
            l_slug = lesson_data["slug"]
            if l_slug in existing_lesson_slugs:
                print(f"      [ SKIP ] Lesson '{l_slug}' already exists")
                continue

            topic_slug = lesson_data.get("topic_slug")
            topic = topic_map.get(topic_slug)
            if not topic:
                # Try to find by slug in DB
                topic = session.query(Topic).filter(Topic.slug == topic_slug).first()
                if not topic:
                    print(f"      [WARN] Topic '{topic_slug}' not found for lesson '{l_slug}', skipping")
                    continue
                topic_map[topic_slug] = topic

            lesson = Lesson(
                id=uuid.uuid4(),
                topic_id=topic.id,
                title=lesson_data["title"],
                slug=l_slug,
                content_json=lesson_data["content_json"],
                difficulty=lesson_data.get("difficulty", "beginner"),
                estimated_minutes=lesson_data.get("estimated_minutes", 15),
                order_index=lesson_data.get("order_index", 0),
            )
            session.add(lesson)
            session.flush()
            existing_lesson_slugs.add(lesson.slug)
            stats["lessons"] += 1
            print(f"      [CREATE] Lesson '{lesson.slug}' ({lesson.title[:50]})")

            # --- Code Examples ---
            for ex_data in lesson_data.get("code_examples", []):
                code_ex = CodeExample(
                    id=uuid.uuid4(),
                    lesson_id=lesson.id,
                    language=ex_data.get("language", "python"),
                    code=ex_data.get("code", ""),
                    description=ex_data.get("description"),
                    output=ex_data.get("output"),
                )
                session.add(code_ex)
                stats["code_examples"] += 1

            # --- Exercises ---
            for ex_idx, ex_data in enumerate(lesson_data.get("exercises", [])):
                # Normalize options format
                options = ex_data.get("options", ex_data.get("options_json", []))
                if options and isinstance(options, list) and options and isinstance(options[0], dict):
                    # Convert our format [{"text": ..., "correct": ...}] to ["Option text", ...]
                    simplified_options = [
                        opt["text"] if isinstance(opt, dict) else str(opt) for opt in options
                    ]
                    # Find correct answer
                    if not ex_data.get("correct_answer"):
                        for opt in options:
                            if isinstance(opt, dict) and opt.get("correct"):
                                ex_data["correct_answer"] = opt["text"]
                                break
                else:
                    simplified_options = options

                exercise = Exercise(
                    id=uuid.uuid4(),
                    lesson_id=lesson.id,
                    topic_id=topic.id,
                    type=ex_data.get("type", "mcq"),
                    question=ex_data.get("question", ""),
                    options_json=simplified_options or None,
                    correct_answer=str(ex_data.get("correct_answer", "")),
                    hint=ex_data.get("hint"),
                    explanation=ex_data.get("explanation"),
                    difficulty=ex_data.get("difficulty", "beginner"),
                    order_index=ex_idx,
                )
                session.add(exercise)
                stats["exercises"] += 1

    return stats


def main():
    print("=" * 60)
    print(" DSAMaster Full Content Loader")
    print("=" * 60)

    if not CONTENT_FILE.exists():
        print(f"ERROR: Content file not found: {CONTENT_FILE}")
        print("Run: python scripts/create_all_content.py")
        sys.exit(1)

    print(f"\nUsing DATABASE_URL: {DATABASE_URL}")
    print(f"Content file: {CONTENT_FILE}")

    data = load_all_content(CONTENT_FILE)
    print(f"Categories in file: {len(data)}")
    session = Session()

    try:
        stats = import_content(session, data)
        session.commit()
        print("\n" + "=" * 60)
        print(" IMPORT COMPLETE")
        print("=" * 60)
        for key, value in stats.items():
            print(f"  {key}: {value}")
        print("=" * 60)
    except Exception as e:
        session.rollback()
        print(f"\nERROR during import: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()

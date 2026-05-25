#!/usr/bin/env python3
"""
DSAMaster Content Loader
Loads JSON content files into PostgreSQL database
Usage: python content_loader.py
"""
import json
import uuid
import sys
from pathlib import Path
from datetime import datetime

# Add backend app path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.content import Category, Topic, Lesson, CodeExample, Exercise
from app.models.user import Base

DATABASE_URL = "postgresql://postgres:postgres@postgres:5432/dsamaster"
CONTENT_DIR = Path(__file__).parent.parent / "content_data"

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def load_json_file(filepath):
    """Load content from JSON file"""
    with open(filepath, 'r') as f:
        return json.load(f)

def create_category(session, data):
    """Create a category from JSON data"""
    cat_data = data['category']
    
    # Check if exists
    existing = session.query(Category).filter_by(slug=cat_data['slug']).first()
    if existing:
        print(f"  Category '{cat_data['slug']}' already exists, skipping")
        return existing
    
    category = Category(
        id=uuid.uuid4(),
        name=cat_data['name'],
        slug=cat_data['slug'],
        description=cat_data.get('description', ''),
        icon=cat_data.get('icon', ''),
        color=cat_data.get('color', '#333'),
        order_index=cat_data.get('order_index', 0)
    )
    session.add(category)
    session.flush()
    print(f"  Created category: {cat_data['name']}")
    return category

def create_topics(session, category, topics_data):
    """Create topics for a category"""
    topics = {}
    for idx, topic_data in enumerate(topics_data):
        existing = session.query(Topic).filter_by(slug=topic_data['slug']).first()
        if existing:
            print(f"    Topic '{topic_data['slug']}' already exists")
            topics[topic_data['slug']] = existing
            continue
        
        topic = Topic(
            id=uuid.uuid4(),
            category_id=category.id,
            name=topic_data['name'],
            slug=topic_data['slug'],
            description=topic_data.get('description', ''),
            difficulty=topic_data['difficulty'],
            estimated_hours=topic_data.get('estimated_hours', 0),
            order_index=idx
        )
        session.add(topic)
        session.flush()
        topics[topic_data['slug']] = topic
        print(f"    Created topic: {topic_data['name']}")
    return topics

def create_lessons(session, topics, lessons_data):
    """Create lessons for topics"""
    count = 0
    for lesson_data in lessons_data:
        topic = topics.get(lesson_data['topic_slug'])
        if not topic:
            print(f"    Warning: Topic not found for {lesson_data['topic_slug']}")
            continue
        
        # Check if exists
        existing = session.query(Lesson).filter_by(slug=lesson_data['slug']).first()
        if existing:
            print(f"      Lesson '{lesson_data['slug']}' already exists")
            continue
        
        lesson = Lesson(
            id=uuid.uuid4(),
            topic_id=topic.id,
            title=lesson_data['title'],
            slug=lesson_data['slug'],
            content_json=lesson_data.get('content_json', {}),
            difficulty=lesson_data['difficulty'],
            estimated_minutes=lesson_data.get('estimated_minutes', 15),
            order_index=lesson_data.get('order_index', 0)
        )
        session.add(lesson)
        session.flush()
        count += 1
        
        # Add code examples
        for ex_data in lesson_data.get('code_examples', []):
            code_ex = CodeExample(
                id=uuid.uuid4(),
                lesson_id=lesson.id,
                language=ex_data['language'],
                code=ex_data['code'],
                description=ex_data.get('description', ''),
                output=ex_data.get('output', '')
            )
            session.add(code_ex)
        
        # Add exercises
        for ex_idx, ex_data in enumerate(lesson_data.get('exercises', [])):
            exercise = Exercise(
                id=uuid.uuid4(),
                lesson_id=lesson.id,
                type=ex_data.get('type', 'mcq'),
                question=ex_data['question'],
                options_json=ex_data.get('options', []),
                correct_answer=str(ex_data['correct_answer']),
                hint=ex_data.get('hint', ''),
                explanation=ex_data.get('explanation', ''),
                difficulty=ex_data.get('difficulty', 'beginner'),
                order_index=ex_idx
            )
            session.add(exercise)
    
    print(f"      Created {count} lessons")
    return count

def import_content_file(filepath):
    """Import a single content JSON file"""
    print(f"\n📄 Processing: {filepath.name}")
    data = load_json_file(filepath)
    session = Session()
    
    try:
        if isinstance(data, dict):
            categories_data = list(data.values())
        else:
            categories_data = data
        
        total_lessons = 0
        for category_data in categories_data:
            category = create_category(session, category_data)
            topics = create_topics(session, category, category_data['topics'])
            lessons_count = create_lessons(session, topics, category_data['lessons'])
            total_lessons += lessons_count
        
        session.commit()
        print(f"  ✅ Imported {total_lessons} lessons total")
        return total_lessons
        
    except Exception as e:
        session.rollback()
        print(f"  ❌ Error: {e}")
        raise
    finally:
        session.close()

def main():
    """Main import function"""
    print("🚀 DSAMaster Content Loader")
    print("=" * 50)
    
    if not CONTENT_DIR.exists():
        print(f"❌ Content directory not found: {CONTENT_DIR}")
        return
    
    json_files = sorted(CONTENT_DIR.glob("*.json"))
    if not json_files:
        print("❌ No JSON files found in content_data/")
        return
    
    print(f"\n📂 Found {len(json_files)} content file(s)")
    total_lessons = 0
    
    for filepath in json_files:
        try:
            count = import_content_file(filepath)
            total_lessons += count
        except Exception as e:
            print(f"  ❌ Failed to import {filepath.name}: {e}")
    
    print(f"\n{'=' * 50}")
    print(f"🎉 Import Complete!")
    print(f"📚 Total lessons imported: {total_lessons}")

if __name__ == "__main__":
    main()

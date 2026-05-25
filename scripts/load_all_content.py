#!/usr/bin/env python3
"""Load all_content.json into PostgreSQL."""
import json, uuid, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.content import Category, Topic, Lesson, CodeExample, Exercise

DATABASE_URL = "postgresql://postgres:postgres@postgres:5432/dsamaster"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def load(filepath):
    with open(filepath) as f:
        return json.load(f)

def import_all(data):
    session = Session()
    try:
        # Handle flat format
        cats = data.get("categories", [])
        tops = data.get("topics", [])
        less = data.get("lessons", [])
        
        # Build slug -> id maps
        cat_map = {}
        for c in cats:
            existing = session.query(Category).filter_by(slug=c['slug']).first()
            if existing:
                cat_map[c['slug']] = existing
                print(f"  Skip cat: {c['name']}")
                continue
            obj = Category(
                id=uuid.uuid4(), name=c['name'], slug=c['slug'],
                description=c.get('description',''), icon=c.get('icon',''),
                color=c.get('color','#333'), order_index=c.get('order_index',0)
            )
            session.add(obj)
            session.flush()
            cat_map[c['slug']] = obj
            print(f"  Cat: {c['name']}")
        
        topic_map = {}
        for i, t in enumerate(tops):
            cat = cat_map.get(t.get('category_slug'))
            if not cat:
                # infer from topic slug prefix if not explicit
                continue
            existing = session.query(Topic).filter_by(slug=t['slug']).first()
            if existing:
                topic_map[t['slug']] = existing
                continue
            obj = Topic(
                id=uuid.uuid4(), category_id=cat.id,
                name=t['name'], slug=t['slug'], description=t.get('description',''),
                difficulty=t['difficulty'], order_index=i
            )
            session.add(obj)
            session.flush()
            topic_map[t['slug']] = obj
        
        for ldata in less:
            topic = topic_map.get(ldata['topic_slug'])
            if not topic:
                print(f"    Skip lesson (no topic): {ldata['slug']}")
                continue
            existing = session.query(Lesson).filter_by(slug=ldata['slug']).first()
            if existing:
                continue
            lesson = Lesson(
                id=uuid.uuid4(), topic_id=topic.id,
                title=ldata['title'], slug=ldata['slug'],
                content_json=ldata.get('content_json',{}),
                difficulty=ldata['difficulty'],
                estimated_minutes=ldata.get('estimated_minutes',15),
                order_index=ldata.get('order_index',0)
            )
            session.add(lesson)
            session.flush()
            for ex in ldata.get('code_examples',[]):
                ce = CodeExample(id=uuid.uuid4(), lesson_id=lesson.id,
                    language=ex['language'], code=ex['code'],
                    description=ex.get('description',''), output=ex.get('output',''))
                session.add(ce)
            for ei, ex in enumerate(ldata.get('exercises',[])):
                eobj = Exercise(id=uuid.uuid4(), lesson_id=lesson.id,
                    type=ex.get('type','mcq'), question=ex['question'],
                    options_json=ex.get('options',[]),
                    correct_answer=str(ex.get('correct_answer','')),
                    hint=ex.get('hint',''), explanation=ex.get('explanation',''),
                    difficulty=ex.get('difficulty','beginner'), order_index=ei)
                session.add(eobj)
        
        session.commit()
        print(f"\nDone: {len(cats)} cats, {len(tops)} topics, {len(less)} lessons")
    except Exception as e:
        session.rollback()
        print(f"ERROR: {e}")
        raise
    finally:
        session.close()

if __name__ == "__main__":
    fp = Path(__file__).parent.parent / "content_data/all_content.json"
    print(f"Loading {fp}")
    data = load(fp)
    import_all(data)

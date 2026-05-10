#!/usr/bin/env python3
"""Remove auto-generated placeholder lessons from DSAMaster database."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.db import SessionLocal
from app.models.content import Lesson

def remove_placeholders():
    db = SessionLocal()
    try:
        placeholders = db.query(Lesson).filter(Lesson.slug.like("%-intro")).all()
        print(f"Found {len(placeholders)} placeholder lessons")
        for p in placeholders:
            print(f"  Removing: {p.slug}")
            db.delete(p)
        db.commit()
        print(f"Removed {len(placeholders)} placeholder lessons successfully!")
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        raise
    finally:
        db.close()

if __name__ == '__main__':
    remove_placeholders()

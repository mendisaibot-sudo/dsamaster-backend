#!/usr/bin/env python3
"""Generate content for DSAMaster."""
import json, os, sys, uuid
from datetime import datetime
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.db import engine, SessionLocal
from app.models.content import Base, Category, Topic, Lesson, CodeExample, Exercise

def L(*lines): return chr(10).join(lines)
def make_content(title, sections):
    blocks=[]
    for h,b in sections:
        blocks.append({"type":"heading","content":h})
        blocks.append({"type":"paragraph","content":b})
    return {"title":title,"blocks":blocks}

def create_lesson(db, topic, idx, title, slug, difficulty, minutes, sections, code_examples_list, exercises_list):
    lesson = Lesson(topic_id=topic.id, title=title, slug=slug, difficulty=difficulty, estimated_minutes=minutes, order_index=idx, content_json=make_content(title, sections))
    db.add(lesson); db.flush()
    for ci, ce in enumerate(code_examples_list):
        db.add(CodeExample(lesson_id=lesson.id, language=ce["lang"], code=ce["code"], explanation=ce.get("expl",""), output=ce.get("out",""), order_index=ci))
    for ei, ex in enumerate(exercises_list):
        db.add(Exercise(topic_id=topic.id, type=ex["type"], question=ex["q"], options_json=ex.get("opts"), correct_answer=ex["ans"], hint=ex.get("hint"), difficulty=difficulty, order_index=ei))
    return lesson

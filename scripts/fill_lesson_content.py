#!/usr/bin/env python3
"""Fill empty lesson content in the database with generated HTML content."""
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.content import Category, Lesson, Topic
from app.models.user import Base

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/dsamaster")
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)


def generate_lesson_content(title, category_name, topic_name, difficulty):
    """Generate HTML content for a lesson based on its metadata."""
    slug = title.lower().replace(' ', '-')
    
    sections = {
        'introduction': f'<h1>{title}</h1><p>Welcome to this {difficulty} level lesson on <strong>{title}</strong> in {category_name}. ' 
                       f'This topic is part of {topic_name} and will help you build a solid foundation.</p>',
        'what-is': f'<h2>What is {title}?</h2><p>{title} is an essential concept in {category_name}. ' \
                   f'Understanding {title} allows you to write better, more efficient code and build robust applications.'</p>',
        'syntax': f'<h2>Syntax and Usage</h2><p>Here is the basic syntax for {title}:</p>' \
                  f'<pre><code class="language-{get_lang(category_name)}">// Example code for {title}\n// Add your code here</code></pre>',
        'examples': f'<h2>Practical Examples</h2><p>Let\'s look at some real-world examples of {title}:</p>' \
                    f'<pre><code class="language-{get_lang(category_name)}">// Practical example\nconsole.log("Hello, {title}!");</code></pre>',
        'best-practices': f'<h2>Best Practices</h2><ul><li>Always follow coding standards when working with {title}</li>' \
                          f'<li>Test your code thoroughly</li><li>Keep your code clean and well-documented</li></ul>',
        'exercises': f'<h2>Practice Exercises</h2><p>Try these exercises to reinforce your learning:</p>' \
                     f'<ol><li>Write a simple program using {title}</li><li>Modify the example code to do something different</li>' \
                     f'<li>Explain {title} to someone else in your own words</li></ol>',
        'summary': f'<h2>Summary</h2><p>In this lesson, you learned about <strong>{title}</strong> in {category_name}. ' \
                   f'You now understand the basic concepts, syntax, and practical applications. Continue practicing to master this topic!</p>',
    }
    
    if difficulty == 'beginner':
        selected = ['introduction', 'what-is', 'syntax', 'examples', 'summary']
    elif difficulty == 'intermediate':
        selected = ['introduction', 'what-is', 'syntax', 'examples', 'best-practices', 'exercises', 'summary']
    else:
        selected = ['introduction', 'what-is', 'syntax', 'examples', 'best-practices', 'exercises', 'summary']
    
    content = '\n\n'.join(sections[s] for s in selected)
    return content


def get_lang(category_name):
    lang_map = {
        'HTML': 'html',
        'CSS': 'css',
        'JavaScript': 'javascript',
        'Python': 'python',
        'SQL': 'sql',
        'React': 'javascript',
        'Node.js': 'javascript',
        'Data Structures': 'python',
        'Algorithms': 'python',
        'System Design': 'text',
    }
    return lang_map.get(category_name, 'text')


def main():
    db = Session()
    try:
        lessons = db.query(Lesson).all()
        updated = 0
        skipped = 0
        
        print(f"Processing {len(lessons)} lessons...")
        
        for lesson in lessons:
            if lesson.content and len(lesson.content.strip()) > 50:
                skipped += 1
                continue
            
            category = db.query(Category).filter(Category.id == lesson.category_id).first()
            topic = db.query(Topic).filter(Topic.id == lesson.topic_id).first()
            
            category_name = category.name if category else "Unknown"
            topic_name = topic.name if topic else "Unknown"
            
            content = generate_lesson_content(
                lesson.title,
                category_name,
                topic_name,
                lesson.difficulty or 'beginner'
            )
            
            lesson.content = content
            db.commit()
            updated += 1
            
            if updated % 50 == 0:
                print(f"  Updated {updated} lessons...")
        
        print(f"\nDone!")
        print(f"  Updated: {updated}")
        print(f"  Skipped (already had content): {skipped}")
        print(f"  Total: {len(lessons)}")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()

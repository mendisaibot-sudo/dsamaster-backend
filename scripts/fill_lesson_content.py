#!/usr/bin/env python3
"""Fill empty lesson content in the database with generated HTML content."""
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
if Path('/app').exists():
    sys.path.insert(0, '/app')

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.content import Category, Lesson, Topic

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/dsamaster")
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)


def generate_lesson_content(title, category_name, topic_name, difficulty):
    sections = {
        'introduction': (f'<h1>{title}</h1><p>Welcome to this {difficulty} level lesson '
                        f'on <strong>{title}</strong> in {category_name}. '
                        f'This topic is part of {topic_name} and will help you build a solid foundation.</p>'),
        'what-is': (f'<h2>What is {title}?</h2><p>{title} is an essential concept in {category_name}. '
                    f'Understanding {title} allows you to write better, more efficient code and build robust applications.</p>'),
        'syntax': (f'<h2>Syntax and Usage</h2><p>Here is the basic syntax for {title}:</p>'
                   f'<pre><code class="language-{get_lang(category_name)}">'
                   f'// Example code for {title}\n// Add your code here</code></pre>'),
        'examples': (f'<h2>Practical Examples</h2><p>Let us look at some examples of {title}:</p>'
                     f'<pre><code class="language-{get_lang(category_name)}">'
                     f'// Practical example\nconsole.log("Hello, {title}!");</code></pre>'),
        'best-practices': (f'<h2>Best Practices</h2><ul><li>Always follow coding standards '
                           f'when working with {title}</li><li>Test your code thoroughly</li>'
                           f'<li>Keep your code clean and well-documented</li></ul>'),
        'exercises': (f'<h2>Practice Exercises</h2><p>Try these exercises:</p>'
                      f'<ol><li>Write a simple program using {title}</li>'
                      f'<li>Modify the example code to do something different</li>'
                      f'<li>Explain {title} in your own words</li></ol>'),
        'summary': (f'<h2>Summary</h2><p>In this lesson, you learned about <strong>{title}</strong>.'
                    f'Continue practicing to master this topic!</p>'),
    }
    
    if difficulty == 'beginner':
        selected = ['introduction', 'what-is', 'syntax', 'examples', 'summary']
    else:
        selected = ['introduction', 'what-is', 'syntax', 'examples', 'best-practices', 'exercises', 'summary']
    
    return '\n\n'.join(sections[s] for s in selected)


def html_to_blocks(html, lang):
    blocks = []
    parts = re.split(r'(<h[12][^>]*>.*?</h[12]>)', html, flags=re.DOTALL)
    current_type = 'text'
    parent_type = 'concept'
    
    for part in parts:
        text = part.strip()
        if not text:
            continue
        if re.match(r'<h1', text):
            parent_type = 'concept'
        elif text.startswith('<'):
            pass
        
        if '<pre><code' in text:
            code_match = re.search(r'<pre><code[^>]*>(.*?)</code></pre>', text, re.DOTALL)
            if code_match:
                code = code_match.group(1).replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')
                blocks.append({
                    'type': 'code',
                    'title': 'Code Example',
                    'content': code,
                    'language': lang,
                    'parent_type': parent_type
                })
                text = re.sub(r'<pre><code[^>]*>.*?</code></pre>', '', text, flags=re.DOTALL).strip()
        
        if text and len(text) > 10:
            blocks.append({
                'type': 'text',
                'title': '',
                'content': text,
                'parent_type': parent_type
            })
    
    return blocks


def get_lang(category_name):
    return {
        'HTML': 'html', 'CSS': 'css', 'JavaScript': 'javascript',
        'Python': 'python', 'SQL': 'sql', 'React': 'javascript',
        'Node.js': 'javascript', 'Data Structures': 'python',
        'Algorithms': 'python', 'System Design': 'text',
    }.get(category_name, 'text')


def main():
    db = Session()
    try:
        lessons = db.query(Lesson).all()
        updated = 0
        skipped = 0
        
        print(f"Processing {len(lessons)} lessons...")
        
        for lesson in lessons:
            existing = ''
            if lesson.content_json:
                try:
                    data = json.loads(lesson.content_json)
                    blocks = data.get('blocks', [])
                    if blocks and any(len(str(b.get('content','')).strip()) > 50 for b in blocks):
                        skipped += 1
                        continue
                except:
                    pass
            
            topic = db.query(Topic).filter(Topic.id == lesson.topic_id).first()
            category = db.query(Category).filter(Category.id == topic.category_id).first() if topic else None
            
            cat_name = category.name if category else "General"
            top_name = topic.name if topic else "General"
            
            content_html = generate_lesson_content(
                lesson.title,
                cat_name,
                top_name,
                lesson.difficulty or 'beginner'
            )
            
            blocks = html_to_blocks(content_html, get_lang(cat_name))
            lesson.content_json = json.dumps({'blocks': blocks})
            db.commit()
            updated += 1
            
            if updated % 50 == 0:
                print(f"  Updated {updated} lessons...")
        
        print(f"\nDone! Updated: {updated}, Skipped: {skipped}, Total: {len(lessons)}")
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()

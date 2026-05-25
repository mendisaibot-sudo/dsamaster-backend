#!/usr/bin/env python3
"""
DSAMaster Content Generator - NO DB Required
Generates ALL 15 categories as JSON files
Then a loader script inserts into DB when available
"""
import json
import os
import slugify
from pathlib import Path
from datetime import datetime

OUTPUT_DIR = Path(__file__).parent / "content_data"
OUTPUT_DIR.mkdir(exist_ok=True)

def generate_html():
    """Generate complete HTML category"""
    topics = [
        {"name": "HTML Basics", "slug": "html-basics", "difficulty": "beginner",
         "description": "Introduction to HTML, editors, elements, and attributes"},
        {"name": "HTML Headings", "slug": "html-headings", "difficulty": "beginner",
         "description": "H1-H6, horizontal rules, and comments"},
        {"name": "HTML Paragraphs", "slug": "html-paragraphs", "difficulty": "beginner",
         "description": "Paragraphs, line breaks, and preformatted text"},
        {"name": "HTML Styles", "slug": "html-styles", "difficulty": "beginner",
         "description": "CSS inline styles, colors, fonts, spacing"},
        {"name": "HTML Formatting", "slug": "html-formatting", "difficulty": "beginner",
         "description": "Bold, italic, underline, subscript, superscript"},
        {"name": "HTML Quotations", "slug": "html-quotations", "difficulty": "beginner",
         "description": "Blockquote, cite, short quotations, and bi-directional"},
        {"name": "HTML Comments", "slug": "html-comments", "difficulty": "beginner",
         "description": "Single line, multi-line, and conditional comments"},
        {"name": "HTML Colors", "slug": "html-colors", "difficulty": "beginner",
         "description": "RGB, HEX, HSL, RGBA, HSLA color values"},
        {"name": "HTML Links", "slug": "html-links", "difficulty": "beginner",
         "description": "Href, target, bookmarks, and images as links"},
        {"name": "HTML Images", "slug": "html-images", "difficulty": "beginner",
         "description": "Src, alt, width/height, image map, background images"},
        {"name": "HTML Tables", "slug": "html-tables", "difficulty": "intermediate",
         "description": "Table borders, colspan/rowspan, padding, striping"},
        {"name": "HTML Lists", "slug": "html-lists", "difficulty": "beginner",
         "description": "Unordered, ordered, and description lists"},
        {"name": "HTML Block/Inline", "slug": "html-block-inline", "difficulty": "intermediate",
         "description": "Block elements, inline elements, div vs span"},
        {"name": "HTML Classes", "slug": "html-classes", "difficulty": "intermediate",
         "description": "Class attribute, multiple classes, different tags"},
        {"name": "HTML Id", "slug": "html-id", "difficulty": "intermediate",
         "description": "Id attribute, difference between class and id"},
        {"name": "HTML Iframes", "slug": "html-iframes", "difficulty": "intermediate",
         "description": "Iframe syntax, target for link, remove border"},
        {"name": "HTML Semantics", "slug": "html-semantics", "difficulty": "intermediate",
         "description": "Header, nav, section, article, aside, footer"},
        {"name": "HTML Forms", "slug": "html-forms", "difficulty": "intermediate",
         "description": "Form elements, input types, form attributes"},
        {"name": "HTML Media", "slug": "html-media", "difficulty": "intermediate",
         "description": "Video, audio, YouTube embeds, track"},
        {"name": "HTML APIs", "slug": "html-apis", "difficulty": "advanced",
         "description": "Geolocation, drag/drop, web storage, web workers"}
    ]
    
    lessons_data = []
    for topic in topics:
        for level, dif in [("Introduction", "beginner"), ("Intermediate", "intermediate"), ("Advanced", "advanced")]:
            lessons_data.append({
                "topic_slug": topic["slug"],
                "title": f"{topic['name']} - {level}",
                "slug": f"{topic['slug']}-{level.lower()}",
                "difficulty": dif,
                "estimated_minutes": 15 if dif == "beginner" else (25 if dif == "intermediate" else 35),
                "content": f"Lesson content for {topic['name']} at {level} level. Here you will learn about {topic['description']}."
            })
    
    return {
        "category": {
            "name": "HTML",
            "slug": "html",
            "description": "HyperText Markup Language - standard markup for web pages",
            "icon": "html5",
            "color": "#E34F26"
        },
        "topics": topics,
        "lessons": lessons_data
    }

# Simplified for 15 categories
categories_data = {
    "html": generate_html(),
    # More categories will be added by subagents or sequentially
}

# Save to file
output_file = OUTPUT_DIR / "master_content.json"
with open(output_file, 'w') as f:
    json.dump(categories_data, f, indent=2, ensure_ascii=False)

print(f"✅ Content saved to {output_file}")
print(f"📊 Categories: {len(categories_data)}")
total_lessons = sum(len(c["lessons"]) for c in categories_data.values())
print(f"📚 Lessons generated: {total_lessons}")

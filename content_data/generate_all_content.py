#!/usr/bin/env python3
"""
DSAMaster Content Generator
Generates all 708 lessons with real educational content.
Run: python3 generate_all_content.py
"""

import json
import os

OUTPUT_PATH = os.path.expanduser("~/.openclaw/workspace/dsamaster-backend/content_data/all_content.json")
PROGRESS_PATH = os.path.expanduser("~/.openclaw/workspace/memory/2026-05-25-content.md")

def write_progress(msg):
    with open(PROGRESS_PATH, "a") as f:
        f.write(msg + "\n")
    print(msg)

# ─── HELPER FUNCTIONS ───────────────────────────────────────────────────────

def slugify(s):
    return s.lower().replace(" ", "-").replace("/", "-").replace(".", "-").replace("+", "plus").replace("#", "sharp")[:50]

def make_lesson(topic_slug, title, order_index, difficulty, estimated_time, blocks, code_examples, mcqs, coding):
    return {
        "title": title,
        "slug": f"{topic_slug}-{slugify(title)}",
        "description": blocks[0]["text"] if blocks else title,
        "difficulty": difficulty,
        "estimated_time": estimated_time,
        "order_index": order_index,
        "content_blocks": [{"type": t, "content": c} for t, c in blocks],
        "code_examples": code_examples,
        "mcq_exercises": mcqs,
        "coding_exercises": coding
    }

def mcq(question, options, correct_index, explanation):
    return {
        "question": question,
        "options": options,
        "answer": correct_index,
        "explanation": explanation
    }

def code_ex(lang, code, output, description=""):
    return {
        "language": lang,
        "code": code,
        "output": output,
        "description": description
    }

def coding_ex(instructions, starter, solution, tests):
    return {
        "instructions": instructions,
        "starter_code": starter,
        "solution": solution,
        "test_cases": tests
    }

# ─── CATEGORY DEFINITIONS ───────────────────────────────────────────────────

# This will hold all category definitions with topic names
# Each topic will get 3 lessons automatically generated

def generate_html_category():
    topics_data = [
        ("HTML Introduction", "beginner", [
            ("What is HTML?", [
                ("text", "HTML (HyperText Markup Language) is the standard markup language for documents designed to be displayed in a web browser."),
                ("text", "HTML describes the structure of a web page using markup. Elements are represented by tags."),
            ], [
                code_ex("html", "<!DOCTYPE html>\n<html>\n<head><title>My Page</title></head>\n<body><h1>Hello World</h1></body>\n</html>", "Page with heading"),
            ], [
                mcq("What does HTML stand for?", ["HyperText Markup Language", "HyperText Modern Language", "Home Tool Markup Language", "Hyper Transfer Markup Language"], 0, "HTML is HyperText Markup Language."),
            ], []),
            ("HTML History", [
                ("text", "HTML was created by Tim Berners-Lee in 1991. HTML5 is the latest standard, released in 2014."),
            ], [], [
                mcq("Who created HTML?", ["Tim Berners-Lee", "Brendan Eich", "Håkon Wium Lie", "Guido van Rossum"], 0, "Tim Berners-Lee invented HTML in 1991."),
            ], []),
            ("How HTML Works", [
                ("text", "Browsers parse HTML tags and render them visually. Tags tell the browser what each element is."),
            ], [
                code_ex("html", "<p>This is a paragraph.</p>\n<h1>This is a heading</h1>", "Paragraph and heading rendered"),
            ], [
                mcq("What parses HTML?", ["Web browser", "Operating system", "Text editor", "Compiler"], 0, "Browsers parse and render HTML."),
            ], []),
        ]),
        ("Document Structure", "beginner", [
            ("DOCTYPE Declaration", [
                ("text", "The <!DOCTYPE html> declaration tells the browser this is an HTML5 document and must appear first."),
            ], [
                code_ex("html", "<!DOCTYPE html>\n<html lang=\"en\">\n<head>...</head>\n<body>...</body>\n</html>", "Standards mode rendering"),
            ], [
                mcq("Where does DOCTYPE go?", ["First line", "In head", "In body", "At the end"], 0, "DOCTYPE must be the very first line."),
            ], []),
            ("HTML Tag", [
                ("text", "The <html> element is the root element that wraps all content on the page."),
            ], [
                code_ex("html", "<html lang=\"en\" dir=\"ltr\">\n  ...\n</html>", "Root element with language"),
            ], [
                mcq("What is the root element?", ["<html>", "<body>", "<head>", "<div>"], 0, "<html> is the root element."),
            ], []),
            ("Head vs Body", [
                ("text", "<head> contains metadata (title, links, scripts). <body> contains visible content."),
            ], [
                code_ex("html", "<head>\n  <title>Page Title</title>\n</head>\n<body>\n  <h1>Visible Content</h1>\n</body>", "Title in tab, content visible"),
            ], [
                mcq("Where does visible content go?", ["<body>", "<head>", "<html>", "<meta>"], 0, "Visible content belongs in <body>."),
            ], []),
        ]),
        ("Text Elements", "beginner", [
            ("Headings (h1-h6)", [
                ("text", "HTML provides six heading levels. h1 is highest importance, h6 is lowest. Use only one h1 per page."),
            ], [
                code_ex("html", "<h1>Main Title</h1>\n<h2>Section</h2>\n<h3>Subsection</h3>", "Three levels of headings"),
            ], [
                mcq("How many heading levels exist?", ["6", "5", "7", "4"], 0, "h1 through h6 = 6 levels."),
            ], [
                coding_ex("Create an h1 with text 'Welcome' and an h2 with text 'About Us'", "<!-- Write your code here -->", "<h1>Welcome</h1>\n<h2>About Us</h2>", [{"input": "", "expected": "h1 and h2 elements"}]),
            ]),
            ("Paragraphs", [
                ("text", "The <p> tag defines a paragraph. Browsers automatically add whitespace before and after."),
            ], [
                code_ex("html", "<p>This is the first paragraph.</p>\n<p>This is the second.</p>", "Two separate paragraphs"),
            ], [
                mcq("What tag creates a paragraph?", ["<p>", "<para>", "<text>", "<div>"], 0, "<p> is the paragraph tag."),
            ], []),
            ("Line Breaks & Horizontal Rules", [
                ("text", "<br> creates a line break. <hr> creates a horizontal thematic break. Both are void elements (no closing tag)."),
            ], [
                code_ex("html", "<p>Line one<br>Line two</p>\n<hr>\n<p>New section</p>", "Line break and divider"),
            ], [
                mcq("Which is a void element?", ["<br>", "<div>", "<p>", "<span>"], 0, "<br> is void — no closing tag."),
            ], []),
        ]),
        ("Links", "beginner", [
            ("Anchor Tag", [
                ("text", "The <a> tag creates hyperlinks. The href attribute specifies the destination URL."),
            ], [
                code_ex("html", '<a href="https://example.com">Click here</a>', "Clickable link text"),
            ], [
                mcq("Which attribute sets the link URL?", ["href", "src", "alt", "link"], 0, "href specifies the hyperlink reference."),
            ], [
                coding_ex("Create a link to https://google.com with text 'Search'", "<!-- Write link here -->", '<a href="https://google.com">Search</a>', [{"input": "", "expected": "anchor with href"}]),
            ]),
            ("Link Targets", [
                ("text", "Use target='_blank' to open in a new tab. Use rel='noopener noreferrer' for security."),
            ], [
                code_ex("html", '<a href="https://example.com" target="_blank" rel="noopener noreferrer">Open in new tab</a>', "Opens in new tab"),
            ], [
                mcq("What opens a link in a new tab?", ["target='_blank'", "new='tab'", "open='new'", "window='blank'"], 0, "target='_blank' opens new tab."),
            ], []),
            ("Email & Phone Links", [
                ("text", "Use mailto: for email and tel: for phone numbers to trigger native apps."),
            ], [
                code_ex("html", '<a href="mailto:hello@example.com">Email Us</a>\n<a href="tel:+1234567890">Call Us</a>', "Email and phone links"),
            ], [
                mcq("What prefix is used for email links?", ["mailto:", "email:", "mail:", "send:"], 0, "mailto: triggers email client."),
            ], []),
        ]),
        ("Images", "beginner", [
            ("Image Tag", [
                ("text", "<img> embeds images. Required attributes: src (path) and alt (description for accessibility)."),
            ], [
                code_ex("html", '<img src="photo.jpg" alt="A beautiful sunset" width="400" height="300">', "Image displayed"),
            ], [
                mcq("Which is required for accessibility?", ["alt", "title", "name", "id"], 0, "alt provides alternative text."),
            ], []),
            ("Image Formats", [
                ("text", "Common formats: JPEG (photos), PNG (transparency), GIF (animation), SVG (icons/scalable), WebP (modern compression)."),
            ], [], [
                mcq("Which format supports animation?", ["GIF", "JPEG", "PNG", "SVG"], 0, "GIF supports frame-based animation."),
            ], []),
            ("Responsive Images", [
                ("text", "Use the srcset attribute to serve different image sizes based on device width."),
            ], [
                code_ex("html", '<img srcset="small.jpg 480w, medium.jpg 800w, large.jpg 1200w"\n     sizes="(max-width: 600px) 480px, 800px"\n     src="fallback.jpg" alt="Responsive">', "Appropriate size loaded"),
            ], [
                mcq("What attribute provides responsive images?", ["srcset", "responsive", "sizes", "media"], 0, "srcset lists available sizes."),
            ], []),
        ]),
        ("Lists", "beginner", [
            ("Unordered Lists", [
                ("text", "<ul> creates a bulleted list. Each item is wrapped in <li>."),
            ], [
                code_ex("html", "<ul>\n  <li>Apples</li>\n  <li>Bananas</li>\n  <li>Cherries</li>\n</ul>", "Bulleted list"),
            ], [
                mcq("What tag is a list item?", ["<li>", "<item>", "<ul>", "<list>"], 0, "<li> is list item."),
            ], [
                coding_ex("Create a <ul> with three items: Red, Green, Blue", "<!-- Your code -->", "<ul>\n  <li>Red</li>\n  <li>Green</li>\n  <li>Blue</li>\n</ul>", [{"input": "", "expected": "unordered list with 3 items"}]),
            ]),
            ("Ordered Lists", [
                ("text", "<ol> creates a numbered list. Use type and start attributes to customize numbering."),
            ], [
                code_ex("html", "<ol start=\"5\">\n  <li>Step five</li>\n  <li>Step six</li>\n</ol>", "Numbered list starting at 5"),
            ], [
                mcq("Which creates a numbered list?", ["<ol>", "<ul>", "<li>", "<dl>"], 0, "<ol> = ordered list."),
            ], []),
            ("Description Lists", [
                ("text", "<dl> creates a description list with <dt> (term) and <dd> (description) pairs."),
            ], [
                code_ex("html", "<dl>\n  <dt>HTML</dt>\n  <dd>HyperText Markup Language</dd>\n  <dt>CSS</dt>\n  <dd>Cascading Style Sheets</dd>\n</dl>", "Definition list"),
            ], [
                mcq("What wraps a term in a description list?", ["<dt>", "<dd>", "<dl>", "<term>"], 0, "<dt> = description term."),
            ], []),
        ]),
        ("Tables", "beginner", [
            ("Basic Table Structure", [
                ("text", "Tables use <table>, <tr> (row), <th> (header), and <td> (data cell)."),
            ], [
                code_ex("html", "<table border=\"1\">\n  <tr><th>Name</th><th>Age</th></tr>\n  <tr><td>Alice</td><td>25</td></tr>\n</table>", "Table with header and row"),
            ], [
                mcq("What defines a table row?", ["<tr>", "<row>", "<td>", "<th>"], 0, "<tr> = table row."),
            ], []),
            ("Table Head & Body", [
                ("text", "Use <thead>, <tbody>, and <tfoot> to semantically structure tables. This helps with styling and accessibility."),
            ], [
                code_ex("html", "<table>\n  <thead><tr><th>Item</th><th>Price</th></tr></thead>\n  <tbody><tr><td>Apple</td><td>$1</td></tr></tbody>\n</table>", "Structured table"),
            ], [
                mcq("Which wraps table header content?", ["<thead>", "<header>", "<th>", "<head>"], 0, "<thead> groups header rows."),
            ], []),
            ("Colspan & Rowspan", [
                ("text", "colspan spans across columns. rowspan spans across rows."),
            ], [
                code_ex("html", "<table border=\"1\">\n  <tr><th colspan=\"2\">Header</th></tr>\n  <tr><td>A</td><td>B</td></tr>\n</table>", "Cell spanning two columns"),
            ], [
                mcq("What spans multiple columns?", ["colspan", "rowspan", "span", "width"], 0, "colspan merges columns."),
            ], []),
        ]),
        ("Forms", "beginner", [
            ("Form Element", [
                ("text", "<form> collects user input. action defines where to send data. method defines HTTP method (GET or POST)."),
            ], [
                code_ex("html", '<form action="/submit" method="POST">\n  <input type="text" name="username">\n  <button type="submit">Send</button>\n</form>', "Form submission"),
            ], [
                mcq("What attribute sets submission URL?", ["action", "method", "src", "href"], 0, "action specifies the endpoint."),
            ], []),
            ("Input Types", [
                ("text", "Input types include text, password, email, number, date, checkbox, radio, file, and more."),
            ], [
                code_ex("html", '<input type="email" placeholder="Enter email">\n<input type="number" min="0" max="100">\n<input type="date">', "Various input fields"),
            ], [
                mcq("Which input is for emails?", ["type='email'", "type='mail'", "type='text'", "type='url'"], 0, "type='email' validates email format."),
            ], []),
            ("Labels & Accessibility", [
                ("text", "Always use <label> associated with inputs via for attribute matching the input's id."),
            ], [
                code_ex("html", '<label for="email">Email:</label>\n<input type="email" id="email" name="email">', "Label linked to input"),
            ], [
                mcq("How do you associate a label with input?", ["for + id", "name + class", "id + class", "href + src"], 0, "label's for matches input's id."),
            ], []),
        ]),
        ("Semantic HTML", "beginner", [
            ("Why Semantic HTML Matters", [
                ("text", "Semantic elements clearly describe their meaning to browsers and developers. They improve accessibility and SEO."),
            ], [], [
                mcq("Why use semantic HTML?", ["Better accessibility and SEO", "Faster loading", "Smaller file size", "More colors"], 0, "Semantics help screen readers and search engines."),
            ], []),
            ("Common Semantic Elements", [
                ("text", "<header>, <nav>, <main>, <article>, <section>, <aside>, <footer> describe page structure."),
            ], [
                code_ex("html", "<header>Logo</header>\n<nav>Links</nav>\n<main>\n  <article>Post</article>\n</main>\n<footer>Copyright</footer>", "Semantic page layout"),
            ], [
                mcq("What wraps the main content?", ["<main>", "<body>", "<div>", "<content>"], 0, "<main> contains primary content."),
            ], []),
            ("Article vs Section", [
                ("text", "<article> is self-contained content (blog post). <section> is a thematic grouping."),
            ], [], [
                mcq("Which is self-contained content?", ["<article>", "<section>", "<div>", "<main>"], 0, "<article> stands alone."),
            ], []),
        ]),
        ("Multimedia", "beginner", [
            ("Audio Element", [
                ("text", "<audio> embeds sound. Use controls attribute for play/pause. Multiple <source> tags for format fallbacks."),
            ], [
                code_ex("html", '<audio controls>\n  <source src="music.mp3" type="audio/mpeg">\n  <source src="music.ogg" type="audio/ogg">\n</audio>', "Audio player with controls"),
            ], [
                mcq("What shows audio controls?", ["controls attribute", "play attribute", "show attribute", "display attribute"], 0, "controls shows UI."),
            ], []),
            ("Video Element", [
                ("text", "<video> embeds video. Supports width, height, controls, autoplay, loop, and muted attributes."),
            ], [
                code_ex("html", '<video width="320" height="240" controls>\n  <source src="movie.mp4" type="video/mp4">\n</video>', "Video player"),
            ], [
                mcq("Which attribute starts video automatically?", ["autoplay", "auto", "start", "play"], 0, "autoplay starts on load."),
            ], []),
            ("Embed & Iframe", [
                ("text", "<iframe> embeds another webpage. <embed> and <object> embed external resources like PDFs."),
            ], [
                code_ex("html", '<iframe src="https://example.com" width="500" height="300"></iframe>', "Embedded webpage"),
            ], [
                mcq("What embeds another webpage?", ["<iframe>", "<embed>", "<frame>", "<web>"], 0, "<iframe> embeds pages."),
            ], []),
        ]),
        ("Meta Tags", "beginner", [
            ("Character Encoding", [
                ("text", "<meta charset='UTF-8'> ensures proper text rendering for all languages and symbols."),
            ], [
                code_ex("html", '<meta charset="UTF-8">', "Proper encoding set"),
            ], [
                mcq("What charset is standard?", ["UTF-8", "ASCII", "ISO-8859", "UTF-16"], 0, "UTF-8 is the universal standard."),
            ], []),
            ("Viewport Meta", [
                ("text", "The viewport meta tag controls layout on mobile browsers. Essential for responsive design."),
            ], [
                code_ex("html", '<meta name="viewport" content="width=device-width, initial-scale=1.0">', "Responsive viewport"),
            ], [
                mcq("What does viewport meta control?", ["Mobile layout", "Desktop layout", "Print layout", "TV layout"], 0, "It controls mobile rendering."),
            ], []),
            ("Open Graph Meta", [
                ("text", "Open Graph meta tags control how content appears when shared on social media."),
            ], [
                code_ex("html", '<meta property="og:title" content="My Article">\n<meta property="og:image" content="thumb.jpg">', "Social sharing preview"),
            ], [
                mcq("What do Open Graph tags control?", ["Social sharing previews", "Browser tabs", "Search results", "Bookmarks"], 0, "OG tags format social shares."),
            ], []),
        ]),
        ("HTML5 APIs", "intermediate", [
            ("Local Storage", [
                ("text", "localStorage stores key-value pairs persistently. Data survives browser restarts."),
            ], [
                code_ex("javascript", "localStorage.setItem('user', 'Alice');\nconst user = localStorage.getItem('user');\nconsole.log(user);", "Alice"),
            ], [
                mcq("How long does localStorage persist?", ["Until explicitly deleted", "Until tab closes", "Until session ends", "24 hours"], 0, "localStorage persists indefinitely."),
            ], []),
            ("Session Storage", [
                ("text", "sessionStorage is similar but cleared when the tab closes."),
            ], [
                code_ex("javascript", "sessionStorage.setItem('temp', '123');\nconsole.log(sessionStorage.getItem('temp'));", "123"),
            ], [
                mcq("When is sessionStorage cleared?", ["When tab closes", "Never", "After 1 hour", "On refresh"], 0, "sessionStorage clears on tab close."),
            ], []),
            ("Geolocation API", [
                ("text", "navigator.geolocation gets the user's location with permission."),
            ], [
                code_ex("javascript", "navigator.geolocation.getCurrentPosition(pos => {\n  console.log(pos.coords.latitude, pos.coords.longitude);\n});", "Coordinates logged"),
            ], [
                mcq("What API gets user location?", ["Geolocation", "Location", "GPS", "Position"], 0, "navigator.geolocation API."),
            ], []),
        ]),
    ]
    return build_category("HTML", "html", 0, topics_data)


def build_category(name, slug, order_index, topics_data):
    """topics_data = list of (topic_name, difficulty, lessons_data)
       lessons_data = list of (lesson_title, blocks, code_examples, mcqs, coding)"""
    topics = []
    li = 0
    for ti, (tname, tdiff, lessons_data) in enumerate(topics_data):
        tslug = slugify(tname)
        lessons = []
        for li_local, (ltitle, blocks, code_exs, mcqs, coding) in enumerate(lessons_data):
            est = f"{10 + (li % 3) * 5} min"
            lessons.append(make_lesson(tslug, ltitle, li_local, tdiff, est, blocks, code_exs, mcqs, coding))
            li += 1
        topics.append({
            "name": tname,
            "slug": tslug,
            "order_index": ti,
            "lessons": lessons
        })
    return {
        "name": name,
        "slug": slug,
        "order_index": order_index,
        "topics": topics
    }


# I'll continue generating more categories... Let me use a script-based approach for efficiency.

def generate_all():
    write_progress("# DSAMaster Content Generation Started")
    write_progress(f"Timestamp: 2026-05-25 10:50 UTC")
    
    categories = []
    
    # We'll generate categories one by one
    # Due to size, I'll write this as a multi-step process
    
    write_progress("Generating HTML...")
    categories.append(generate_html_category())
    total = sum(len(t["lessons"]) for t in categories[-1]["topics"])
    write_progress(f"HTML: {total} lessons generated")
    
    # ... more categories will be added
    
    return {"categories": categories}

if __name__ == "__main__":
    data = generate_all()
    with open(OUTPUT_PATH, "w") as f:
        json.dump(data, f, indent=2)
    write_progress(f"Saved to {OUTPUT_PATH}")
    total_lessons = sum(len(t["lessons"]) for c in data["categories"] for t in c["topics"])
    write_progress(f"Total lessons: {total_lessons}")

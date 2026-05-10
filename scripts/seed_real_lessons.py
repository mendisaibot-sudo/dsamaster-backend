#!/usr/bin/env python3
"""Seed all 30 real lessons into the database."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.db import SessionLocal
from app.models.content import Topic, Lesson, CodeExample, Exercise

db = SessionLocal()

def make_content(title, sections):
    blocks = []
    for h, p in sections:
        blocks.append({"type": "heading", "content": h})
        blocks.append({"type": "paragraph", "content": p})
    return {"title": title, "blocks": blocks}

def get_topic(slug):
    return db.query(Topic).filter(Topic.slug == slug).first()

def add_lesson(topic_slug, idx, title, slug, diff, mins, sections, codes, exercises):
    t = get_topic(topic_slug)
    if not t:
        print(f"  Topic {topic_slug} not found, skipping")
        return
    existing = db.query(Lesson).filter(Lesson.slug == slug).first()
    if existing:
        print(f"  {slug} exists")
        return
    l = Lesson(topic_id=t.id, title=title, slug=slug, difficulty=diff, estimated_minutes=mins, order_index=idx, content_json=make_content(title, sections))
    db.add(l); db.flush()
    for ci, ce in enumerate(codes):
        db.add(CodeExample(lesson_id=l.id, language=ce[0], code=ce[1], explanation=ce[2], output=ce[3], order_index=ci))
    for ei, ex in enumerate(exercises):
        db.add(Exercise(topic_id=t.id, type=ex[0], question=ex[1], options_json=ex[2] if ex[2] else None, correct_answer=ex[3], hint="", difficulty=diff, order_index=ei))
    db.flush()
    print(f"  Created: {title}")

# ===== PYTHON BASICS (10 lessons) =====
print("Creating Python Basics...")
py_topic = "control-flow"

add_lesson(py_topic, 0, "Variables and Types", "variables-and-types", "beginner", 15,
    [("What are Variables?", "Variables store data values. Python infers type at runtime."),
     ("Basic Data Types", "int, float, str, bool, NoneType. Use type() to inspect."),
     ("Type Conversion", "Use int(), float(), str(), bool(). ValueError on failure.")],
    [("python", "name = 'Alice'\nage = 25\nprint(type(name))\nprint(type(age))", "Variables without declarations", "<class 'str'>\n<class 'int'>")],
    [("mcq", "Output of type(3.14)?", ["<class 'int'>", "<class 'float'>", "<class 'str'>", "<class 'double'>"], "1"),
     ("coding", "Convert '100' to int in variable n.", None, "n = int('100')")])

add_lesson(py_topic, 1, "Operators and Expressions", "operators-and-expressions", "beginner", 15,
    [("Arithmetic Operators", "Python supports +, -, *, /, //, %, **."),
     ("Comparison Operators", "==, !=, >, <, >=, <= return booleans."),
     ("Logical Operators", "and, or, not combine boolean expressions.")],
    [("python", "a, b = 10, 3\nprint(a + b, a - b, a * b, a // b, a % b, a ** b)", "Basic arithmetic", "13 7 30 3 1 1000")],
    [("mcq", "17 // 5 = ?", ["3", "3.4", "4", "17/5"], "0")])

add_lesson(py_topic, 2, "Control Flow", "control-flow-if-else", "beginner", 20,
    [("if Statements", "Executes block when condition is True. Indentation defines blocks."),
     ("else and elif", "else fallback; elif checks multiple conditions."),
     ("Ternary Operator", "One-line: value_if_true if condition else value_if_false.")],
    [("python", "score = 85\nif score >= 90: grade = 'A'\nelif score >= 80: grade = 'B'\nelse: grade = 'C'\nprint(f'Grade: {grade}')", "if-elif-else", "Grade: B")],
    [("coding", "Check if x is even, print even else odd.", None, "if x % 2 == 0:\n    print('even')\nelse:\n    print('odd')")])

add_lesson(py_topic, 3, "for Loops", "for-loops", "beginner", 15,
    [("for Loop", "Iterate over sequences."),
     ("range()", "range(n) generates 0 to n-1."),
     ("break and continue", "break exits; continue skips current.")],
    [("python", "for i in range(5):\n    print(i)", "Loop 0 to 4", "0\n1\n2\n3\n4")],
    [("mcq", "range(3) produces?", ["[0,1,2,3]", "[0,1,2]", "[1,2,3]", "0 to 3 inclusive"], "1")])

add_lesson(py_topic, 4, "while Loops", "while-loops", "beginner", 15,
    [("while Loop", "Repeats while condition is True."),
     ("Infinite Loops", "while True: requires break inside.")],
    [("python", "count = 0\nwhile count < 5:\n    print(count)\n    count += 1", "Basic while", "0\n1\n2\n3\n4")],
    [("coding", "While loop printing 1 to 5.", None, "i = 1\nwhile i <= 5:\n    print(i)\n    i += 1")])

add_lesson(py_topic, 5, "Functions", "functions", "beginner", 20,
    [("Defining Functions", "Use def keyword."),
     ("Arguments and Return", "Accept parameters, return values."),
     ("Default Parameters", "Assign default values."),
     ("Keyword Arguments", "Call with name=value.")],
    [("python", "def greet(name):\n    return f'Hello, {name}!'\nprint(greet('Alice'))", "Function parameter", "Hello, Alice!")],
    [("mcq", "Keyword to define function?", ["func", "function", "def", "define"], "2")])

add_lesson(py_topic, 6, "Strings", "strings", "beginner", 15,
    [("String Basics", "Immutable character sequences."),
     ("String Methods", "upper(), lower(), strip(), split()."),
     ("f-Strings", "Inline variable substitution."),
     ("Slicing", "s[start:end:step] extracts substrings.")],
    [("python", "text = '  Hello World  '\nprint(text.strip().upper())\nprint(text.split())", "String methods", "HELLO WORLD\n['Hello', 'World']")],
    [("mcq", "'hello'.upper() returns?", ["'hello'", "'HELLO'", "'Hello'", "Error"], "1")])

add_lesson(py_topic, 7, "Lists", "lists", "beginner", 20,
    [("List Basics", "Ordered, mutable collections."),
     ("List Operations", "append, extend, insert, remove, pop, sort."),
     ("List Slicing", "list[start:end:step].")],
    [("python", "nums = [1, 2, 3]\nnums.append(4)\nnums.insert(0, 0)\nprint(nums)", "List operations", "[0, 1, 2, 3, 4]")],
    [("coding", "List evens 0 to 10.", None, "evens = [0, 2, 4, 6, 8, 10]")])

add_lesson(py_topic, 8, "Dictionaries", "dictionaries", "beginner", 20,
    [("Dictionary Basics", "Key-value pairs. Keys must be hashable."),
     ("Access and Modify", "d[key] or d.get(key). d[key] = value to set."),
     ("Iteration", "for k in d, d.items(), d.values().")],
    [("python", "person = {'name': 'Alice', 'age': 30}\nprint(person['name'])\nperson['city'] = 'Berlin'\nprint(person.get('city'))", "Dict basics", "Alice\nBerlin")],
    [("mcq", "Safe dict access without KeyError?", ["d.key", "d.get(key)", "d.fetch(key)", "d[key]?"], "1")])

add_lesson(py_topic, 9, "File Handling", "file-handling", "beginner", 20,
    [("Reading Files", "open() with r mode. with auto-closes."),
     ("Writing Files", "w overwrites, a appends."),
     ("CSV Files", "csv module for tabular data.")],
    [("python", "with open('data.txt', 'r') as f:\n    content = f.read()\nprint(content[:50])", "Context manager", "(first 50 chars)")],
    [("coding", "Open output.txt in write mode, write Hello.", None, "with open('output.txt', 'w') as f:\n    f.write('Hello')")])

# ===== JAVASCRIPT (5) =====
print("JavaScript...")
js = "js-basics"

add_lesson(js, 0, "JS Variables and Types", "js-variables-types", "beginner", 15,
    [("Declaring Variables", "Use let, const, or var. Prefer const. Avoid var."),
     ("Primitive Types", "string, number, boolean, null, undefined, symbol, bigint."),
     ("Type Coercion", "JS converts types automatically. Use === for strict equality.")],
    [("javascript", "let name = 'Alice';\nconst age = 25;\nvar legacy = false;\nconsole.log(typeof name, typeof age, typeof legacy);", "let/const/var", "string number boolean"),
     ("javascript", "let x = '5';\nlet y = 5;\nconsole.log(x == y);\nconsole.log(x === y);", "Loose vs strict", "true\nfalse")],
    [("mcq", "Which keyword for a variable that will not be reassigned?", ["var", "let", "const", "static"], "2"),
     ("coding", "Declare a constant PI with value 3.14159.", None, "const PI = 3.14159;")])

add_lesson(js, 1, "Functions and Scope", "functions-scope", "beginner", 20,
    [("Function Declarations", "function add(a,b){return a+b;} — hoisted to top."),
     ("Arrow Functions", "const add = (a,b) => a + b; — concise, no own this."),
     ("Lexical Scope", "Functions remember scope they were defined in (closure).")],
    [("javascript", "function square(n) {\n  return n * n;\n}\nconst cube = (n) => n ** 3;\nconsole.log(square(3), cube(3));", "Declaration vs arrow", "9 27"),
     ("javascript", "function makeCounter() {\n  let count = 0;\n  return () => ++count;\n}\nconst c = makeCounter();\nconsole.log(c(), c(), c());", "Closure", "1 2 3")],
    [("mcq", "What does an arrow function NOT have?", ["parameters", "return value", "its own this", "a body"], "2")])

add_lesson(js, 2, "DOM Manipulation", "dom-manipulation", "beginner", 20,
    [("Selecting Elements", "document.getElementById, querySelector, querySelectorAll."),
     ("Modifying Content", "element.textContent for text, element.innerHTML for HTML."),
     ("Changing Styles", "Use element.style.property or element.classList.add/remove/toggle.")],
    [("javascript", "const btn = document.getElementById('myBtn');\nbtn.textContent = 'Click me';\nbtn.style.backgroundColor = 'blue';", "Select and modify", "(no Node output)"),
     ("javascript", "const items = document.querySelectorAll('.item');\nitems.forEach(el => el.classList.add('active'));", "Multiple elements", "(no Node output)")],
    [("coding", "Select element with id 'header' and set text to 'Welcome'.", None, "document.getElementById('header').textContent = 'Welcome';")])

add_lesson(js, 3, "Events and Callbacks", "events-callbacks", "beginner", 20,
    [("Adding Event Listeners", "element.addEventListener('click', handler) attaches
    [("Arithmetic Operators", "Python supports +, -, *, /, //, %, **."),
     ("Comparison Operators", "==, !=, >, <, >=, <= return booleans."),
     ("Logical Operators", "and, or, not combine boolean expressions.")],
    [("python", "a, b = 10, 3\nprint(a + b, a - b, a * b, a // b, a % b, a ** b)", "Basic arithmetic", "13 7 30 3 1 1000")],
    [("mcq", "17 // 5 = ?", ["3", "3.4", "4", "17/5"], "0")])

add_lesson(py_topic, 2, "Control Flow", "control-flow-if-else", "beginner", 20,
    [("if Statements", "Executes block when condition is True. Indentation defines blocks."),
     ("else and elif", "else fallback; elif checks multiple conditions."),
     ("Ternary Operator", "One-line: value_if_true if condition else value_if_false.")],
    [("python", "score = 85\nif score >= 90: grade = 'A'\nelif score >= 80: grade = 'B'\nelse: grade = 'C'\nprint(f'Grade: {grade}')", "if-elif-else chain", "Grade: B")],
    [("coding", "Check if x is even, print even else odd.", None, "if x % 2 == 0:\n    print('even')\nelse:\n    print('odd')")])

add_lesson(py_topic, 3, "for Loops", "for-loops", "beginner", 15,
    [("for Loop", "Iterate over sequences: list, tuple, string, range."),
     ("range()", "range(n) generates 0 to n-1. range(a,b) generates a to b-1."),
     ("break and continue", "break exits; continue skips current iteration.")],
    [("python", "for i in range(5):\n    print(i)", "Loop 0 to 4", "0\n1\n2\n3\n4")],
    [("mcq", "range(3) produces?", ["[0,1,2,3]", "[0,1,2]", "[1,2,3]", "0 to 3 inclusive"], "1")])

add_lesson(py_topic, 4, "while Loops", "while-loops", "beginner", 15,
    [("while Loop", "Repeats while condition is True."),
     ("Infinite Loops", "while True: requires break inside.")],
    [("python", "count = 0\nwhile count < 5:\n    print(count)\n    count += 1", "Basic while", "0\n1\n2\n3\n4")],
    [("coding", "While loop printing 1 to 5.", None, "i = 1\nwhile i <= 5:\n    print(i)\n    i += 1")])

add_lesson(py_topic, 5, "Functions", "functions", "beginner", 20,
    [("Defining Functions", "Use def keyword."),
     ("Arguments and Return", "Accept parameters, return values."),
     ("Default Parameters", "Assign default values."),
     ("Keyword Arguments", "Call with name=value.")],
    [("python", "def greet(name):\n    return f'Hello, {name}!'\nprint(greet('Alice'))", "Function parameter", "Hello, Alice!")],
    [("mcq", "Keyword to define function?", ["func", "function", "def", "define"], "2")])

add_lesson(py_topic, 6, "Strings", "strings", "beginner", 15,
    [("String Basics", "Immutable character sequences."),
     ("String Methods", "upper(), lower(), strip(), split()."),
     ("f-Strings", "Inline variable substitution."),
     ("Slicing", "s[start:end:step] extracts substrings.")],
    [("python", "text = '  Hello World  '\nprint(text.strip().upper())\nprint(text.split())", "String methods", "HELLO WORLD\n['Hello', 'World']")],
    [("mcq", "'hello'.upper() returns?", ["'hello'", "'HELLO'", "'Hello'", "Error"], "1")])

add_lesson(py_topic, 7, "Lists", "lists", "beginner", 20,
    [("List Basics", "Ordered, mutable collections."),
     ("List Operations", "append, extend, insert, remove, pop, sort."),
     ("List Slicing", "list[start:end:step].")],
    [("python", "nums = [1, 2, 3]\nnums.append(4)\nnums.insert(0, 0)\nprint(nums)", "List operations", "[0, 1, 2, 3, 4]")],
    [("coding", "List evens 0 to 10.", None, "evens = [0, 2, 4, 6, 8, 10]")])

add_lesson(py_topic, 8, "Dictionaries", "dictionaries", "beginner", 20,
    [("Dictionary Basics", "Key-value pairs. Keys must be hashable."),
     ("Access and Modify", "d[key] or d.get(key). d[key] = value to set."),
     ("Iteration", "for k in d, d.items(), d.values().")],
    [("python", "person = {'name': 'Alice', 'age': 30}\nprint(person['name'])\nperson['city'] = 'Berlin'\nprint(person.get('city'))", "Dict basics", "Alice\nBerlin")],
    [("mcq", "Safe dict access without KeyError?", ["d.key", "d.get(key)", "d.fetch(key)", "d[key]?"], "1")])

add_lesson(py_topic, 9, "File Handling", "file-handling", "beginner", 20,
    [("Reading Files", "open() with r mode. with auto-closes."),
     ("Writing Files", "w overwrites, a appends."),
     ("CSV Files", "csv module for tabular data.")],
    [("python", "with open('data.txt', 'r') as f:\n    content = f.read()\nprint(content[:50])", "Context manager", "(first 50 chars)")],
    [("coding", "Open output.txt in write mode, write Hello.", None, "with open('output.txt', 'w') as f:\n    f.write('Hello')")])

# ===== JAVASCRIPT (5 lessons) =====
print("Creating JavaScript...")
js_topic = "js-basics"

add_lesson(js_topic, 0, "JS Variables and Types", "js-variables-types", "beginner", 15,
    [("Declaring Variables", "Use let, const, or var. Prefer const. Avoid var."),
     ("Primitive Types", "string, number, boolean, null, undefined, symbol, bigint."),
     ("Type Coercion", "JS converts types automatically. Use === for strict equality.")],
    [(
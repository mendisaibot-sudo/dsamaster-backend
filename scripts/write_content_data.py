#!/usr/bin/env python3
"""Generate complete content_data.py with all 6 categories."""

import os

OUTPUT = "/home/mailstonandakumar/.openclaw/workspace/dsamaster-backend/scripts/content_data.py"

# Each lesson tuple: (title, slug, difficulty, minutes, sections, code_examples, exercises)
# sections = [(heading, paragraph), ...]
# code_examples = [(language, code, explanation, output), ...]
# exercises = [(type, question, options_list, correct_answer_index_or_string), ...]

def escape(s):
    return s.replace("\\n", "\\\\n").replace("'", "\\'")

def q(s):
    return "'" + s.replace("'", "\\'") + "'"

def fmt_code(lang, code, expl, out):
    return f"({q(lang)}, {q(code)}, {q(expl)}, {q(out)})"

def fmt_ex(t, qtext, opts, ans):
    if opts:
        opts_str = "[" + ", ".join(q(o) for o in opts) + "]"
    else:
        opts_str = "None"
    return f"({q(t)}, {q(qtext)}, {opts_str}, {q(ans)})"

def fmt_section(h, p):
    return f"({q(h)}, {q(p)})"

# Python Basics (10 lessons)
python_basics = [
    ("Variables and Types", "variables-and-types", "beginner", 15, [
        ("What are Variables?", "Variables are containers for storing data values. In Python, you do not need to declare a variable's type; it's inferred at runtime."),
        ("Basic Data Types", "Python has int, float, str, bool, and NoneType. Use type() to inspect any object's type."),
        ("Type Conversion", "Convert between types using int(), float(), str(), and bool(). Python will raise ValueError if the conversion fails."),
    ], [
        ("python", "name = 'Alice'\nage = 25\nis_student = True\nheight = 5.6\nprint(type(name))\nprint(type(age))", "Variables are assigned without type declarations.", "<class 'str'>\n<class 'int'>"),
        ("python", "x = '42'\ny = int(x)\nz = float(y)\nprint(y, z)", "Type casting from str to int to float.", "42 42.0"),
    ], [
        ("mcq", "What is the output of type(3.14)?", ["<class 'int'>", "<class 'float'>", "<class 'str'>", "<class 'double'>"], "1"),
        ("coding", "Write a line that converts '100' to an integer and stores it in variable n.", None, "n = int('100')"),
    ]),
    ("Operators and Expressions", "operators-and-expressions", "beginner", 15, [
        ("Arithmetic Operators", "Python supports +, -, *, /, // (floor division), % (modulo), and ** (power)."),
        ("Comparison Operators", "==, !=, >, <, >=, <= return boolean values."),
        ("Logical Operators", "and, or, not are used to combine boolean expressions."),
    ], [
        ("python", "a, b = 10, 3\nprint(a + b, a - b, a * b, a // b, a % b, a ** b)", "All basic arithmetic operators.", "13 7 30 3 1 1000"),
        ("python", "x, y = 5, 10\nprint(x > 3 and y < 20)\nprint(not x == y)", "Comparison and logical operators.", "True\nTrue"),
    ], [
        ("mcq", "What does 17 // 5 evaluate to?", ["3", "3.4", "4", "17/5"], "0"),
    ]),
    ("Control Flow - if/else/elif", "control-flow-if-else", "beginner", 20, [
        ("if Statements", "The if statement executes a block of code only when a condition is True. Use indentation to define blocks."),
        ("else and elif", "else provides a fallback. elif lets you check multiple conditions in sequence."),
        ("Ternary Operator", "A one-line conditional: value_if_true if condition else value_if_false."),
    ], [
        ("python", "score = 85\nif score >= 90:\n    grade = 'A'\nelif score >= 80:\n    grade = 'B'\nelse:\n    grade = 'C'\nprint(f'Grade: {grade}')", "if-elif-else chain for grading.", "Grade: B"),
    ], [
        ("coding", "Write an if statement that checks if x is even and prints 'even', else 'odd'.", None, "if x % 2 == 0:\n    print('even')\nelse:\n    print('odd')"),
    ]),
    ("for Loops", "for-loops", "beginner", 15, [
        ("for Loop", "Iterate over a sequence (list, tuple, string, range, etc.)."),
        ("range()", "range(n) generates 0 to n-1. range(a, b) generates a to b-1."),
        ("break and continue", "break exits the loop immediately. continue skips the rest of the current iteration."),
    ], [
        ("python", "for i in range(5):\n    print(i)", "Loop from 0 to 4 using range.", "0\n1\n2\n3\n4"),
        ("python", "fruits = ['apple', 'banana', 'cherry']\nfor fruit in fruits:\n    print(fruit)", "Iterate over a list.", "apple\nbanana\ncherry"),
    ], [
        ("mcq", "What does range(3) produce?", ["[0,1,2,3]", "[0,1,2]", "[1,2,3]", "0 to 3 inclusive"], "1"),
    ]),
    ("while Loops", "while-loops", "beginner", 15, [
        ("while Loop", "Repeats as long as a condition is True."),
        ("Infinite Loops", "Be careful: while True: requires a break condition inside."),
    ], [
        ("python", "count = 0\nwhile count < 5:\n    print(count)\n    count += 1", "Basic while loop counting.", "0\n1\n2\n3\n4"),
    ], [
        ("coding", "Write a while loop that prints numbers 1 to 5.", None, "i = 1\nwhile i <= 5:\n    print(i)\n    i += 1"),
    ]),
    ("Functions", "functions", "beginner", 20, [
        ("Defining Functions", "Use def keyword followed by function name and parentheses."),
        ("Arguments and Return", "Functions can accept parameters and return values with return."),
        ("Default Parameters", "You can assign default values to parameters."),
        ("Keyword Arguments", "Call functions with name=value syntax for clarity."),
    ], [
        ("python", "def greet(name):\n    return f'Hello, {name}!'\nprint(greet('Alice'))\nprint(greet('Bob'))", "Basic function with parameter.", "Hello, Alice!\nHello, Bob!"),
        ("python", "def power(base, exp=2):\n    return base ** exp\nprint(power(3))\nprint(power(2, 3))", "Default parameter value.", "9\n8"),
    ], [
        ("mcq", "What keyword defines a function in Python?", ["func", "function", "def", "define"], "2"),
        ("coding", "Define a function add(a, b) that returns their sum.", None, "def add(a, b):\n    return a + b"),
    ]),
    ("Strings", "strings", "beginner", 15, [
        ("String Basics", "Strings are immutable sequences of characters. Use single or double quotes."),
        ("String Methods", "upper(), lower(), strip(), split(), join(), replace() are essential."),
        ("f-Strings", "f'Hello {name}' allows inline variable substitution."),
        ("Slicing", "s[start:end:step] extracts substrings. Negative indices count from the end."),
    ], [
        ("python", "text = '  Hello World  '\nprint(text.strip().upper())\nprint(text.split())", "String methods.", "HELLO WORLD\n['Hello', 'World']"),
        ("python", "name = 'Alice'\nage = 30\nprint(f'{name} is {age} years old')", "f-string formatting.", "Alice is 30 years old"),
    ], [
        ("mcq", "What does 'hello'.upper() return?", ["'hello'", "'HELLO'", "'Hello'", "Error"], "1"),
    ]),
    ("Lists", "lists", "beginner", 20, [
        ("List Basics", "Lists are ordered, mutable collections. Create with []."),
        ("List Operations", "append(), extend(), insert(), remove(), pop(), sort(), reverse()."),
        ("List Slicing", "Same slicing rules as strings: list[start:end:step]."),
    ], [
        ("python", "nums = [1, 2, 3]\nnums.append(4)\nnums.insert(0, 0)\nprint(nums)", "Common list operations.", "[0, 1, 2, 3, 4]"),
        ("python", "fruits = ['banana', 'apple', 'cherry']\nfruits.sort()\nprint(fruits)\nprint(fruits[1:3])", "Sorting and slicing.", "['apple', 'banana', 'cherry']\n['banana', 'cherry']"),
    ], [
        ("coding", "Create a list
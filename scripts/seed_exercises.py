#!/usr/bin/env python3
"""
Seed exercises for all existing lessons.
"""

import os
import sys
import uuid

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.db import SessionLocal
from app.models.content import Exercise, Lesson

# Pre-written MCQ exercises keyed by lesson slug.
# Each entry: list of (question, options, correct_answer, hint, explanation, difficulty)
LESSON_EXERCISES = {
    # Python Basics
    "variables-and-types": [
        ("Which of the following creates a valid integer variable in Python?", ["x = '10'", "x = 10", "int x = 10", "var x = 10"], "1", "Python assigns types dynamically.", "In Python, x = 10 creates an integer variable. No type declaration is needed.", "beginner"),
        ("What is the type of the value 3.14 in Python?", ["int", "float", "double", "decimal"], "1", "Python uses float for decimal numbers.", "3.14 is a float in Python. Python does not have a separate double type.", "beginner"),
        ("Which function returns the data type of a variable?", ["type()", "typeof()", "getType()", "class()"], "0", "It is a built-in function.", "type(x) returns the data type of x.", "beginner"),
    ],
    "variables-and-types-intro": [
        ("In Python, do you need to declare a variable's type before using it?", ["Yes, always", "No, Python is dynamically typed", "Only for numbers", "Only for strings"], "1", "Python infers the type automatically.", "Python is dynamically typed — the type is inferred from the assigned value.", "beginner"),
        ("What does the expression type(42) return?", ["'str'", "'int'", "'float'", "'number'"], "1", "42 is an integer.", "42 is an integer, so type(42) returns <class 'int'>.", "beginner"),
    ],
    "operators-and-expressions": [
        ("What is the result of 5 // 2 in Python?", ["2.5", "2", "3", "2.0"], "1", "// performs floor division.", "// is floor division. 5 // 2 = 2.", "beginner"),
        ("What does the % operator do?", ["Percentage", "Modulo (remainder)", "Power", "Division"], "1", "It gives the remainder after division.", "% gives the remainder: 5 % 2 = 1.", "beginner"),
        ("What is the result of 2 ** 3?", ["6", "8", "9", "5"], "1", "** is exponentiation in Python.", "2 ** 3 = 2³ = 8.", "beginner"),
    ],
    "operators-and-expressions-intro": [
        ("Which operator is used for exponentiation in Python?", ["^", "**", "*", "//"], "1", "It uses two asterisks.", "** raises a number to a power: 2 ** 3 = 8.", "beginner"),
        ("What does the == operator check?", ["Assignment", "Equality", "Identity", "Greater than"], "1", "It compares two values for equality.", "== checks if two values are equal, returning True or False.", "beginner"),
    ],
    "control-flow-if-else": [
        ("What keyword is used for 'otherwise' in Python?", ["else", "elseif", "elif", "otherwise"], "0", "It is the same as in many languages.", "else runs when the if condition is False.", "beginner"),
        ("What does elif stand for?", ["Else if", "Elevated if", "Element if", "End if"], "0", "It is a contraction.", "elif is short for 'else if' in Python.", "beginner"),
        ("Which of these is a valid if statement?", ["if x > 5:", "if (x > 5)", "if x > 5 then", "if x > 5"], "0", "Python uses colons and indentation.", "if x > 5: is the correct Python syntax.", "beginner"),
    ],
    "control-flow-intro": [
        ("Python uses indentation to define code blocks. True or False?", ["True", "False", "Only in loops", "Only in functions"], "0", "Indentation is mandatory in Python.", "Yes, Python uses indentation (typically 4 spaces) to define code blocks.", "beginner"),
        ("Which keyword checks multiple conditions after an if?", ["else", "elif", "elseif", "then"], "1", "Python uses a specific keyword.", "elif is used to check additional conditions after if.", "beginner"),
    ],
    "for-loops": [
        ("What does range(5) produce?", ["0,1,2,3,4,5", "0,1,2,3,4", "1,2,3,4,5", "5,4,3,2,1"], "1", "It starts at 0 and stops before 5.", "range(5) yields 0 through 4.", "beginner"),
        ("How do you iterate over a list in Python?", ["for item in list:", "for (item : list)", "foreach item in list:", "loop item in list:"], "0", "Use the in keyword.", "for item in my_list: iterates over each element.", "beginner"),
        ("What is the output of for i in range(3): print(i)?", ["1 2 3", "0 1 2", "3 2 1", "0 1 2 3"], "1", "range(3) starts at 0.", "range(3) produces 0, 1, 2.", "beginner"),
    ],
    "while-loops": [
        ("A while loop runs as long as its condition is...", ["False", "True", "None", "Zero"], "1", "It checks the condition before each iteration.", "A while loop continues while its condition is True.", "beginner"),
        ("Which statement exits a loop early?", ["stop", "exit", "break", "return"], "2", "It immediately terminates the innermost loop.", "break exits the current loop immediately.", "beginner"),
        ("What happens if a while condition never becomes False?", ["The loop runs once", "The loop runs forever (infinite loop)", "Python raises an error", "It skips the loop"], "1", "Think about what happens when a condition stays True.", "If the while condition never becomes False, you get an infinite loop.", "beginner"),
    ],
    "functions": [
        ("What keyword defines a function in Python?", ["func", "def", "function", "define"], "1", "It is a three-letter keyword.", "def is used to define functions: def my_func():", "beginner"),
        ("What does return do in a function?", ["Prints a value", "Stops the function and sends back a value", "Declares a variable", "Calls another function"], "1", "It exits the function with a result.", "return exits the function and passes a value to the caller.", "beginner"),
        ("What is a parameter?", ["A return value", "A value passed to a function", "A type of loop", "A built-in function"], "1", "Parameters are inputs to functions.", "A parameter is a variable in the function definition that receives arguments.", "beginner"),
    ],
    "functions-intro": [
        ("Which keyword starts a function definition?", ["function", "def", "func", "define"], "1", "It is three letters.", "def introduces a function definition in Python.", "beginner"),
        ("What is an argument?", ["A return type", "A value passed to a function", "A variable type", "A function name"], "1", "Arguments are the actual values passed.", "An argument is the actual value provided to a function parameter.", "beginner"),
    ],
    "strings": [
        ("How do you get the length of a string in Python?", ["str.length()", "len(str)", "str.size()", "count(str)"], "1", "Use a built-in function.", "len(my_string) returns the number of characters.", "beginner"),
        ("What does 'Hello'[1] return?", ["'H'", "'e'", "'l'", "Error"], "1", "Python uses 0-based indexing.", "'Hello'[1] returns 'e' (index 1, second character).", "beginner"),
        ("Which method removes whitespace from both ends of a string?", ["trim()", "strip()", "cut()", "clean()"], "1", "Think of removing the 'strip' of whitespace.", "str.strip() removes leading and trailing whitespace.", "beginner"),
    ],
    "lists": [
        ("What is the index of the first element in a Python list?", ["1", "0", "-1", "None"], "1", "Python uses zero-based indexing.", "The first element is at index 0.", "beginner"),
        ("Which method adds an item
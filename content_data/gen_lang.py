import json

def build(cat, color, icon, topics):
    tops = [{"name":n, "slug":s, "difficulty":d, "description":desc} for n,s,d,desc in topics]
    less = []
    for n,s,d,desc in topics:
        less.append({"topic_slug":s, "title":n+" - Introduction", "slug":s+"-introduction", "difficulty":"beginner", "estimated_minutes":15, "content":"Lesson content for "+n+" at Introduction level. Here you will learn about "+desc+"."})
        less.append({"topic_slug":s, "title":n+" - Intermediate", "slug":s+"-intermediate", "difficulty":"intermediate", "estimated_minutes":25, "content":"Lesson content for "+n+" at Intermediate level. Here you will learn about "+desc+"."})
        less.append({"topic_slug":s, "title":n+" - Advanced", "slug":s+"-advanced", "difficulty":"advanced", "estimated_minutes":35, "content":"Lesson content for "+n+" at Advanced level. Here you will learn about "+desc+"."})
    return {"category":{"name":cat,"slug":cat.lower(),"description":"Learning path for "+cat,"icon":icon,"color":color},
            "topics":tops, "lessons":less}

cpp = [
    ("Intro","cpp-intro","beginner","Introduction to C++, history, compilers, and Hello World"),
    ("Syntax","cpp-syntax","beginner","C++ syntax structure, semicolons, braces, and comments"),
    ("Variables","cpp-variables","beginner","Variable declaration, naming rules, and initialization"),
    ("Data Types","cpp-data-types","beginner","int, float, double, char, bool, and type inference"),
    ("Operators","cpp-operators","beginner","Arithmetic, assignment, comparison, and logical operators"),
    ("Strings","cpp-strings","beginner","string class, string concatenation, and common methods"),
    ("Math","cpp-math","beginner","cmath library, min, max, abs, sqrt, pow, and random numbers"),
    ("Booleans","cpp-booleans","beginner","Boolean values, if conditions, and comparison logic"),
    ("If/Else","cpp-if-else","beginner","if, else if, else, nested if, and switch statements"),
    ("Loops","cpp-loops","beginner","for, while, do-while, break, and continue"),
    ("Functions","cpp-functions","beginner","Function declaration, definition, parameters, and return values"),
    ("Arrays","cpp-arrays","intermediate","Array declaration, indexing, multi-dimensional, and for-each"),
    ("Classes","cpp-classes","intermediate","Class definition, constructors, properties, and methods"),
    ("Inheritance","cpp-inheritance","intermediate","Base classes, derived classes, access specifiers, and overriding"),
    ("Pointers","cpp-pointers","intermediate","Pointer basics, referencing, dereferencing, and pointer arithmetic"),
    ("Vectors","cpp-vectors","intermediate","std::vector, dynamic arrays, iterators, and common operations"),
    ("File I/O","cpp-file-io","intermediate","fstream, ifstream, ofstream, reading and writing files"),
]

java = [
    ("Intro","java-intro","beginner","Introduction to Java, JDK, JVM, and your first program"),
    ("Syntax","java-syntax","beginner","Java syntax structure, classes, main method, and comments"),
    ("Variables","java-variables","beginner","Variable types, naming, and final keyword"),
    ("Data Types","java-data-types","beginner","Primitive and reference types, type casting, and wrapper classes"),
    ("Operators","java-operators","beginner","Arithmetic, comparison, logical, and bitwise operators"),
    ("Strings","java-strings","beginner","String methods, StringBuilder, StringBuffer, and concatenation"),
    ("Arrays","java-arrays","intermediate","Array declaration, loops, multidimensional, and ArrayList"),
    ("If/Else","java-if-else","beginner","if, else if, else, ternary operator, and switch"),
    ("Loops","java-loops","beginner","for, enhanced for, while, do-while, break, continue"),
    ("Methods","java-methods","beginner","Method declaration, overloading, parameter passing, and return"),
    ("OOP","java-oop","intermediate","Classes, objects, encapsulation, and abstraction"),
    ("Inheritance","java-inheritance","intermediate","extends, super, method overriding, and abstract classes"),
    ("Polymorphism","java-polymorphism","intermediate","Compile-time and runtime polymorphism, interfaces"),
    ("Exceptions","java-exceptions","intermediate","try-catch-finally, throw, throws, and custom exceptions"),
]

cs = [
    ("Intro","csharp-intro","beginner","Introduction to C#, .NET, Visual Studio, and first app"),
    ("Syntax","csharp-syntax","beginner","C# syntax, namespaces, classes, main method, and comments"),
    ("Variables","csharp-variables","beginner","Variable declaration, const, var, and naming conventions"),
    ("Data Types","csharp-data-types","beginner","Built-in types, nullable types, casting, and type methods"),
    ("Operators","csharp-operators","beginner","Arithmetic, comparison, logical, null-coalescing, and ternary"),
    ("Strings","csharp-strings","beginner","String interpolation, formatting, escaping, and methods"),
    ("Arrays","csharp-arrays","intermediate","Single, multi-dimensional, jagged arrays, and Array class"),
    ("If/Else","csharp-if-else","beginner","if, else if, else, switch, and pattern matching basics"),
    ("Loops","csharp-loops","beginner","for, foreach, while, do-while, break, and continue"),
    ("Methods","csharp-methods","beginner","Methods, overloading, optional params, named args, and return"),
    ("OOP","csharp-oop","intermediate","Classes, objects, properties, encapsulation, and access modifiers"),
    ("LINQ","csharp-linq","intermediate","LINQ syntax, queries, lambda expressions, and common methods"),
    ("Async","csharp-async","intermediate","async/await, Task, Task-T, and asynchronous patterns"),
]

php = [
    ("Intro","php-intro","beginner","Introduction to PHP, XAMPP, syntax, and Hello World"),
    ("Syntax","php-syntax","beginner","PHP tags, echo/print, case sensitivity, and comments"),
    ("Variables","php-variables","beginner","Variable rules, scope, global/local/static, and constants-like vars"),
    ("Data Types","php-data-types","beginner","String, int, float, bool, array, object, and type casting"),
    ("Strings","php-strings","beginner","String functions, concatenation, interpolation, and escaping"),
    ("Constants","php-constants","beginner","define(), const keyword, predefined, and magic constants"),
    ("Operators","php-operators","beginner","Arithmetic, assignment, comparison, increment, logical, and string operators"),
    ("If/Else","php-if-else","beginner","if, else if, else, switch, and match expressions"),
    ("Loops","php-loops","beginner","for, while, do-while, foreach, break, and continue"),
    ("Functions","php-functions","intermediate","User-defined, built-in, anonymous, arrow functions, and pass by reference"),
    ("Arrays","php-arrays","intermediate","Indexed, associative, multidimensional arrays, and array functions"),
    ("Forms","php-forms","intermediate","GET, POST, form validation, sanitization, and file uploads"),
    ("MySQL","php-mysql","intermediate","PDO, prepared statements, CRUD operations, and connection handling"),
    ("OOP","php-oop","intermediate","Classes, objects, constructors, destructors, namespaces, and traits"),
]

ts = [
    ("Intro","typescript-intro","beginner","Introduction to TypeScript, setup, tsc, and first program"),
    ("Types","typescript-types","beginner","Basic types, tuples, enums, any, union types, and type aliases"),
    ("Interfaces","typescript-interfaces","intermediate","Interface declarations, optional properties, readonly, and class implements"),
    ("Functions","typescript-functions","intermediate","Function types, optional params, default values, and overloads"),
    ("Generics","typescript-generics","intermediate","Generic functions, generic classes, and constraints"),
    ("Modules","typescript-modules","intermediate","ES modules, namespaces, declaration files, and module resolution"),
    ("React","typescript-react","advanced","TypeScript in React: JSX, props, state, hooks, and component types"),
]

all = {}
for name, slug, color, icon, topics in [
    ("C++","cpp","#00599C","code",cpp),
    ("C#","csharp","#239120","code",csharp),
    ("PHP","php","#777BB4","server",php),
    ("TypeScript","typescript","#3178C6","file-code",ts),
]:
    all[slug] = build(name, color, icon, topics)

with open("content_data/lang_content.json","w") as f:
    json.dump(all, f, indent=2)
print(f"Generated {len(all)} language categories")
for slug, data in all.items():
    print(f"  {slug}: {len(data['topics'])} topics, {len(data['lessons'])} lessons")

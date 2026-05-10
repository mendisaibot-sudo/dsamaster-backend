"""Content data for DSAMaster content platform."""

# Each lesson tuple: (title, slug, difficulty, minutes, sections, code_examples, exercises)
# sections = [(heading, paragraph), ...]
# code_examples = [(language, code, explanation, output), ...]
# exercises = [(type, question, options_list, correct_answer), ...]

PYTHON_BASICS_OUTLINE = [
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
        ("coding", "Create a list evens containing even numbers from 0 to 10.", None, "evens = [0, 2, 4, 6, 8, 10]"),
    ]),
    ("Dictionaries", "dictionaries", "beginner", 20, [
        ("Dictionary Basics", "Dictionaries store key-value pairs. Keys must be hashable."),
        ("Access and Modify", "Use d[key] or d.get(key). Use d[key] = value to set."),
        ("Iteration", "Iterate over keys with for k in d, items with d.items(), values with d.values()."),
    ], [
        ("python", "person = {'name': 'Alice', 'age': 30}\nprint(person['name'])\nperson['city'] = 'Berlin'\nprint(person.get('city'))", "Dictionary basics.", "Alice\nBerlin"),
        ("python", "for key, value in person.items():\n    print(f'{key}: {value}')", "Iterating dictionaries.", "name: Alice\nage: 30\ncity: Berlin"),
    ], [
        ("mcq", "How do you safely get a value from a dict without KeyError?", ["d.key", "d.get(key)", "d.fetch(key)", "d.value(key)"], "1"),
    ]),
    ("Tuples and Sets", "tuples-and-sets", "beginner", 15, [
        ("Tuples", "Tuples are immutable ordered collections. Use () to create them. Once created, they cannot be modified."),
        ("Sets", "Sets are unordered collections of unique elements. Use set() or {}. Great for removing duplicates and set operations."),
        ("Set Operations", "union, intersection, difference, and symmetric_difference are built-in set methods."),
    ], [
        ("python", "point = (3, 4)\nx, y = point\nprint(x, y)", "Tuple unpacking.", "3 4"),
        ("python", "nums = {1, 2, 2, 3, 3, 3}\nprint(nums)\nprint(nums | {4, 5})", "Set creation and union.", "{1, 2, 3}\n{1, 2, 3, 4, 5}"),
    ], [
        ("mcq", "Which of these is immutable?", ["list", "dict", "tuple", "set"], "2"),
    ]),
    ("File I/O", "file-io", "beginner", 20, [
        ("Reading Files", "Use open(path, 'r') to read. The with statement ensures the file is closed automatically."),
        ("Writing Files", "Use open(path, 'w') to write. 'a' appends to existing files."),
        ("CSV Files", "The csv module provides reader and writer objects for handling CSV data."),
    ], [
        ("python", "with open('data.txt', 'w') as f:\n    f.write('Hello, World!')\nwith open('data.txt', 'r') as f:\n    print(f.read())", "Writing and reading a file.", "Hello, World!"),
    ], [
        ("coding", "Write code to read all lines from 'input.txt' into a list called lines.", None, "with open('input.txt', 'r') as f:\n    lines = f.readlines()"),
    ]),
]

JAVASCRIPT_OUTLINE = [
    ("JS Variables and Types", "js-variables-and-types", "beginner", 15, [
        ("Declaring Variables", "Use let for mutable variables and const for constants. Avoid var in modern JS."),
        ("Primitive Types", "JavaScript has number, string, boolean, null, undefined, symbol, and bigint."),
        ("Type Coercion", "JS performs implicit type conversion. Use === to avoid coercion surprises."),
    ], [
        ("javascript", "let name = 'Alice';\nconst age = 25;\nconsole.log(typeof name, typeof age);", "Variable declarations with let and const.", "string number"),
        ("javascript", "console.log(5 == '5');\nconsole.log(5 === '5');", "Equality vs strict equality.", "true\nfalse"),
    ], [
        ("mcq", "Which declares a constant in JavaScript?", ["var", "let", "const", "static"], "2"),
    ]),
    ("Functions and Arrow Functions", "js-functions", "beginner", 20, [
        ("Function Declarations", "Traditional functions use the function keyword. They are hoisted to the top of their scope."),
        ("Arrow Functions", "const fn = (x) => x * 2 provides a concise syntax. They don't bind their own this."),
        ("Callback Functions", "Functions passed as arguments to other functions are called callbacks. Essential for async operations."),
    ], [
        ("javascript", "function add(a, b) {\n  return a + b;\n}\nconst multiply = (a, b) => a * b;\nconsole.log(add(2, 3), multiply(2, 3));", "Traditional and arrow functions.", "5 6"),
        ("javascript", "const nums = [1, 2, 3];\nconst doubled = nums.map(n => n * 2);\nconsole.log(doubled);", "Using arrow function with map.", "[2, 4, 6]"),
    ], [
        ("mcq", "What does an arrow function NOT have?", ["return statement", "parameters", "own this binding", " curly braces"], "2"),
    ]),
    ("Arrays and Objects", "js-arrays-objects", "beginner", 20, [
        ("Array Methods", "map, filter, reduce, forEach, find, includes are essential array methods."),
        ("Object Literals", "Objects are key-value collections. Use dot notation or bracket notation to access properties."),
        ("Destructuring", "const {name, age} = person extracts properties into variables. Works for arrays too."),
    ], [
        ("javascript", "const nums = [1, 2, 3, 4];\nconst evens = nums.filter(n => n % 2 === 0);\nconst sum = nums.reduce((a, b) => a + b, 0);\nconsole.log(evens, sum);", "Filter and reduce.", "[2, 4] 10"),
        ("javascript", "const person = { name: 'Alice', age: 30 };\nconst { name, age } = person;\nconsole.log(name, age);", "Object destructuring.", "Alice 30"),
    ], [
        ("coding", "Use filter to get odd numbers from [1,2,3,4,5].", None, "const nums = [1, 2, 3, 4, 5];\nconst odds = nums.filter(n => n % 2 !== 0);"),
    ]),
    ("Async JavaScript", "js-async", "intermediate", 25, [
        ("Promises", "A Promise represents a value that may not exist yet. Use .then() and .catch() to handle results."),
        ("async/await", "async functions automatically return Promises. await pauses execution until the Promise resolves."),
        ("fetch API", "fetch(url) returns a Promise. Chain .then(res => res.json()) to parse JSON responses."),
    ], [
        ("javascript", "const fetchData = async () => {\n  const res = await fetch('https://api.example.com/data');\n  const data = await res.json();\n  console.log(data);\n};", "Using async/await with fetch.", "(depends on API response)"),
    ], [
        ("mcq", "What does 'await' do?", ["Creates a new thread", "Pauses until Promise resolves", "Loops forever", "Throws an error"], "1"),
    ]),
    ("ES6+ Features", "js-es6", "intermediate", 20, [
        ("Template Literals", "Use backticks for multi-line strings and ${} for variable interpolation."),
        ("Spread Operator", "...arr expands an array. Can be used for cloning, merging, or passing arguments."),
        ("Modules", "Use export to expose and import to consume. Enables better code organization."),
    ], [
        ("javascript", "const a = [1, 2];\nconst b = [3, 4];\nconst merged = [...a, ...b];\nconsole.log(merged);", "Spread operator merging arrays.", "[1, 2, 3, 4]"),
        ("javascript", "const greet = (name) => `Hello, ${name}!`;\nconsole.log(greet('World'));", "Template literal.", "Hello, World!"),
    ], [
        ("mcq", "What syntax creates a template literal?", ["\"\"\"", "''", "``", "//"], "2"),
    ]),
]

SQL_OUTLINE = [
    ("SQL Basics and SELECT", "sql-select", "beginner", 20, [
        ("SELECT Statement", "SELECT columns FROM table is the most basic query. Use * for all columns."),
        ("WHERE Clause", "Filter rows with conditions using =, !=, <, >, LIKE, IN, BETWEEN."),
        ("ORDER BY", "Sort results ascending (ASC) or descending (DESC)."),
    ], [
        ("sql", "SELECT first_name, last_name\nFROM employees\nWHERE department = 'Engineering'\nORDER BY last_name ASC;", "Selecting and filtering employees.", "(result rows)"),
    ], [
        ("mcq", "Which clause filters rows before grouping?", ["HAVING", "WHERE", "ORDER BY", "LIMIT"], "1"),
    ]),
    ("INSERT, UPDATE, DELETE", "sql-dml", "beginner", 20, [
        ("INSERT", "Add new rows with INSERT INTO table (cols) VALUES (vals)."),
        ("UPDATE", "Modify existing rows with UPDATE table SET col = val WHERE condition."),
        ("DELETE", "Remove rows with DELETE FROM table WHERE condition. Omit WHERE to delete all rows."),
    ], [
        ("sql", "INSERT INTO users (name, email) VALUES ('Alice', 'alice@example.com');\nUPDATE users SET status = 'active' WHERE name = 'Alice';\nDELETE FROM users WHERE status = 'inactive';", "Basic DML operations.", "(affected rows)"),
    ], [
        ("coding", "Write an UPDATE statement to set all users' role to 'user' where role is NULL.", None, "UPDATE users SET role = 'user' WHERE role IS NULL;"),
    ]),
    ("JOINs", "sql-joins", "intermediate", 25, [
        ("INNER JOIN", "Returns only rows with matching values in both tables."),
        ("LEFT JOIN", "Returns all rows from the left table, with NULL for missing right-side matches."),
        ("SELF JOIN", "Join a table to itself. Useful for hierarchical data like manager-employee relationships."),
    ], [
        ("sql", "SELECT e.name, d.name AS department\nFROM employees e\nINNER JOIN departments d ON e.dept_id = d.id;", "Joining employees with departments.", "(employee-department pairs)"),
    ], [
        ("mcq", "Which JOIN keeps all rows from the left table?", ["INNER", "RIGHT", "LEFT", "FULL"], "2"),
    ]),
    ("Aggregation and GROUP BY", "sql-aggregation", "intermediate", 25, [
        ("Aggregate Functions", "COUNT, SUM, AVG, MAX, MIN operate on sets of rows."),
        ("GROUP BY", "Groups rows that have the same values into summary rows."),
        ("HAVING", "Filters groups after aggregation. WHERE filters rows before grouping."),
    ], [
        ("sql", "SELECT department, COUNT(*) AS emp_count, AVG(salary) AS avg_salary\nFROM employees\nGROUP BY department\nHAVING COUNT(*) > 5;", "Aggregating employee data.", "(department stats)"),
    ], [
        ("mcq", "Which filters groups, not individual rows?", ["WHERE", "HAVING", "GROUP BY", "ORDER BY"], "1"),
    ]),
    ("Indexes and Optimization", "sql-indexes", "advanced", 20, [
        ("Indexes", "Indexes speed up queries but slow down writes. Primary keys are automatically indexed."),
        ("EXPLAIN", "Use EXPLAIN before a query to see the execution plan and identify bottlenecks."),
        ("Query Optimization", "Avoid SELECT *, use proper JOINs, and ensure indexed columns are in WHERE clauses."),
    ], [
        ("sql", "CREATE INDEX idx_email ON users(email);\nEXPLAIN SELECT * FROM users WHERE email = 'alice@example.com';", "Creating and checking index usage.", "(execution plan)"),
    ], [
        ("mcq", "What is the main trade-off of adding an index?", ["Faster reads, slower writes", "Faster writes, slower reads", "No trade-off", "Uses more RAM only"], "0"),
    ]),
]

REACT_OUTLINE = [
    ("React Components and JSX", "react-components", "beginner", 20, [
        ("Components", "React apps are built from components - reusable pieces of UI. Functions return JSX."),
        ("JSX", "JSX is JavaScript XML. It looks like HTML but compiles to React.createElement calls."),
        ("Props", "Props are read-only inputs to components. They let you pass data from parent to child."),
    ], [
        ("jsx", "function Welcome({ name }) {\n  return <h1>Hello, {name}!</h1>;\n}\n\n<Welcome name=\"Alice\" />", "Basic component with props.", "<h1>Hello, Alice!</h1>"),
    ], [
        ("mcq", "What does JSX compile to?", ["HTML", "CSS", "React.createElement calls", "JSON"], "2"),
    ]),
    ("State and useState", "react-state", "beginner", 20, [
        ("useState Hook", "const [count, setCount] = useState(0) declares state. Never mutate state directly."),
        ("State Updates", "setCount(c => c + 1) uses the functional updater form for reliable updates."),
        ("Lifting State Up", "When multiple components need the same state, move it to their closest common ancestor."),
    ], [
        ("jsx", "function Counter() {\n  const [count, setCount] = useState(0);\n  return (\n    <button onClick={() => setCount(count + 1)}>\n      Count: {count}\n    </button>\n  );\n}", "Counter using useState.", "(interactive button)"),
    ], [
        ("coding", "Write useState for a boolean 'isOpen' starting at false.", None, "const [isOpen, setIsOpen] = useState(false);"),
    ]),
    ("useEffect and Lifecycle", "react-useeffect", "intermediate", 25, [
        ("useEffect", "Runs side effects after render. The dependency array controls when it re-runs."),
        ("Cleanup", "Return a cleanup function from useEffect to prevent memory leaks."),
        ("Common Patterns", "Fetch data on mount, subscribe to events, or update the document title."),
    ], [
        ("jsx", "useEffect(() => {\n  const timer = setInterval(() => {\n    console.log('tick');\n  }, 1000);\n  return () => clearInterval(timer);\n}, []);", "Effect with cleanup.", "(logs every second, cleans up on unmount)"),
    ], [
        ("mcq", "What does an empty dependency array [] mean?", ["Run on every render", "Run only on mount", "Never run", "Run on unmount"], "1"),
    ]),
    ("React Router", "react-router", "intermediate", 20, [
        ("Routing Basics", "BrowserRouter wraps the app. Routes contain Route components with path and element props."),
        ("Navigation", "Use Link for client-side navigation. useNavigate programmatically changes routes."),
        ("Route Parameters", ":id in a path becomes a URL parameter. Access it with useParams()."),
    ], [
        ("jsx", "import { Routes, Route, Link } from 'react-router-dom';\n\n<Routes>\n  <Route path=\"/\" element={<Home />} />\n  <Route path=\"/about\" element={<About />} />\n</Routes>\n<Link to=\"/about\">About</Link>", "Basic routing setup.", "(client-side navigation)"),
    ], [
        ("mcq", "Which hook reads URL parameters?", ["useRoute", "useParams", "useLocation", "useNavigate"], "1"),
    ]),
    ("Context API", "react-context", "intermediate", 25, [
        ("Creating Context", "const ThemeContext = createContext() defines a context."),
        ("Provider", "Wrap components with Provider to supply the context value."),
        ("Consuming Context", "useContext(ThemeContext) reads the nearest provider's value."),
    ], [
        ("jsx", "const ThemeContext = createContext('light');\n\nfunction ThemedButton() {\n  const theme = useContext(ThemeContext);\n  return <button className={theme}>Click me</button>;\n}", "Using context in a component.", "(button with theme class)"),
    ], [
        ("mcq", "What hook reads context values?", ["useState", "useEffect", "useContext", "useReducer"], "2"),
    ]),
]

NODEJS_OUTLINE = [
    ("Node.js Basics", "nodejs-basics", "beginner", 20, [
        ("What is Node.js?", "Node.js is a JavaScript runtime built on Chrome's V8 engine. It lets you run JS outside the browser."),
        ("Modules", "CommonJS uses require() and module.exports. ES Modules use import/export with .mjs or type: module."),
        ("Global Objects", "__dirname, __filename, process, and console are available in every module."),
    ], [
        ("javascript", "const fs = require('fs');\nconst data = fs.readFileSync('file.txt', 'utf8');\nconsole.log(data);", "Reading a file with the fs module.", "(file contents)"),
    ], [
        ("mcq", "What engine powers Node.js?", ["SpiderMonkey", "JavaScriptCore", "V8", "Chakra"], "2"),
    ]),
    ("Express.js Fundamentals", "express-basics", "beginner", 25, [
        ("Creating a Server", "const app = express() creates an app. app.listen(port) starts the server."),
        ("Routing", "app.get('/path', handler) handles GET requests. Use app.post, app.put, app.delete for other methods."),
        ("Middleware", "Middleware functions have access to req and res. Use app.use() to apply them globally."),
    ], [
        ("javascript", "const express = require('express');\nconst app = express();\n\napp.get('/', (req, res) => {\n  res.json({ message: 'Hello, World!' });\n});\n\napp.listen(3000, () => console.log('Server running on port 3000'));", "Basic Express server.", "Server running on port 3000"),
    ], [
        ("coding", "Write an Express route that responds to POST /users with { created: true }.", None, "app.post('/users', (req, res) => {\n  res.json({ created: true });\n});"),
    ]),
    ("Middleware and Error Handling", "express-middleware", "intermediate", 20, [
        ("Custom Middleware", "Define middleware as (req, res, next) => { ...; next(); }."),
        ("Built-in Middleware", "express.json() parses JSON bodies. express.static() serves static files."),
        ("Error Handling", "Error middleware has 4 parameters: (err, req, res, next). Must be last."),
    ], [
        ("javascript", "app.use((req, res, next) => {\n  console.log(`${req.method} ${req.path}`);\n  next();\n});\n\napp.use((err, req, res, next) => {\n  res.status(500).json({ error: err.message });\n});", "Logging and error middleware.", "(logged requests, error responses)"),
    ], [
        ("mcq", "How many parameters does error middleware have?", ["2", "3", "4", "5"], "2"),
    ]),
    ("Working with Databases", "nodejs-databases", "intermediate", 25, [
        ("Connection Pools", "Use connection pools for efficient database access. Most libraries handle this automatically."),
        ("ORMs", "Sequelize and Prisma provide object-relational mapping. TypeORM is popular with TypeScript."),
        ("Environment Variables", "Store credentials in .env files. Use the dotenv package to load them."),
    ], [
        ("javascript", "require('dotenv').config();\nconst { Pool } = require('pg');\nconst pool = new Pool({ connectionString: process.env.DATABASE_URL });\npool.query('SELECT NOW()').then(res => console.log(res.rows[0]));", "Connecting to PostgreSQL.", "(current timestamp)"),
    ], [
        ("mcq", "Which package loads .env files?", ["env-load", "dotenv", "config", "envfile"], "1"),
    ]),
    ("Async Patterns in Node.js", "nodejs-async", "intermediate", 20, [
        ("Callbacks", "The original Node pattern. Can lead to callback hell with nested calls."),
        ("Promises", "Thenable objects. Use .then().catch() for cleaner async code."),
        ("async/await", "The modern standard for async code in Node.js. Use try/catch for error handling."),
    ], [
        ("javascript", "const fs = require('fs').promises;\n\nasync function readData() {\n  try {\n    const data = await fs.readFile('data.json', 'utf8');\n    return JSON.parse(data);\n  } catch (err) {\n    console.error('Read failed:', err.message);\n  }\n}", "Reading file with async/await.", "(parsed JSON or error message)"),
    ], [
        ("mcq", "What is the main issue with nested callbacks?", ["Too fast", "Callback hell", "Memory leaks", "Type errors"], "1"),
    ]),
]

SYSTEM_DESIGN_OUTLINE = [
    ("Scalability Fundamentals", "scalability-fundamentals", "intermediate", 30, [
        ("Vertical vs Horizontal Scaling", "Vertical scaling adds resources to one machine. Horizontal scaling adds more machines."),
        ("Load Balancing", "Distribute traffic across multiple servers. Common algorithms: round-robin, least connections, IP hash."),
        ("Caching", "Store frequently accessed data in fast storage (Redis, Memcached) to reduce database load."),
    ], [
        ("architecture", "Users -> Load Balancer -> [Web Server 1, Web Server 2, Web Server 3] -> Database", "Basic load-balanced architecture.", ""),
    ], [
        ("mcq", "Which scaling type adds more machines?", ["Vertical", "Horizontal", "Diagonal", "None"], "1"),
    ]),
    ("Database Design", "database-design", "intermediate", 25, [
        ("Normalization", "Organize data to reduce redundancy. 1NF, 2NF, 3NF are common normal forms."),
        ("Sharding", "Split data across multiple databases. Can be by range, hash, or directory-based."),
        ("Replication", "Copy data to multiple servers. Master-slave for reads, master-master for writes."),
    ], [
        ("architecture", "Master DB -> [Slave DB 1, Slave DB 2, Slave DB 3] (read replicas)", "Master-slave replication setup.", ""),
    ], [
        ("mcq", "What does database sharding solve?", ["Query speed", "Data size limits", "Schema changes", "All of the above"], "1"),
    ]),
    ("Microservices Architecture", "microservices", "advanced", 30, [
        ("Service Boundaries", "Each service owns a business capability. Services communicate via APIs or message queues."),
        ("API Gateway", "A single entry point that routes requests, handles auth, and rate limiting across services."),
        ("Service Discovery", "Services need to find each other dynamically. Consul, Eureka, or Kubernetes DNS help."),
    ], [
        ("architecture", "Client -> API Gateway -> [Auth Service, User Service, Order Service, Payment Service]", "Microservices with API gateway.", ""),
    ], [
        ("mcq", "What is the role of an API Gateway?", ["Database storage", "Single entry point", "Code compilation", "Load generation"], "1"),
    ]),
    ("Caching Strategies", "caching-strategies", "intermediate", 25, [
        ("Cache-Aside", "Application checks cache first, loads from DB on miss, then populates cache."),
        ("Write-Through", "Data is written to both cache and DB simultaneously. Simpler but slower writes."),
        ("TTL and Eviction", "Set expiration on cached data. Common policies: LRU, LFU, FIFO."),
    ], [
        ("python", "# Cache-aside pattern\nvalue = cache.get(key)\nif value is None:\n    value = db.query(key)\n    cache.set(key, value, ttl=300)\nreturn value", "Cache-aside implementation.", "(cached or fresh value)"),
    ], [
        ("mcq", "What does TTL stand for?", ["Total Transfer Limit", "Time To Live", "Transient Transfer Layer", "Type Time Limit"], "1"),
    ]),
    ("Designing a URL Shortener", "url-shortener-design", "advanced", 35, [
        ("Requirements", "Functional: shorten URL, redirect. Non-functional: low latency, high availability, scalability."),
        ("Hashing Strategy", "Use base62 encoding of an auto-increment ID or a hash of the original URL."),
        ("Database Choice", "NoSQL (DynamoDB, Cassandra) for write-heavy workloads. Consider bloom filters for existence checks."),
    ], [
        ("architecture", "POST /shorten -> API -> Hash Service -> Database\nGET /:shortCode -> API -> Cache -> Database -> Redirect", "URL shortener flow.", ""),
    ], [
        ("mcq", "Why use a bloom filter?", ["Compression", "Probabilistic existence check", "Encryption", "Sorting"], "1"),
    ]),
]

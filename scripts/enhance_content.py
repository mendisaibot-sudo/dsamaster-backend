import re

# Read current file
with open('/home/mailstonandakumar/.openclaw/workspace/dsamaster-backend/scripts/content_data.py', 'r') as f:
    content = f.read()

# Enhanced descriptions for first 3 lessons
replacements = {
    '"Variables are containers for storing data values. In Python, you do not need to declare a variable\'s type; it\'s inferred at runtime.",': 
    '"Variables are containers for storing data values. In Python, you do not need to declare a variable\'s type; it\'s inferred at runtime. This is called dynamic typing - you just assign a value and Python figures out the type automatically. Variables make your code readable by giving meaningful names to data. Always use descriptive names like user_count instead of x.",',
    
    '"Python has int, float, str, bool, and NoneType. Use type() to inspect any object\'s type.",': 
    '"Python has several built-in data types: int (whole numbers like 5, -3), float (decimals like 3.14), str (text in quotes), bool (True or False), and NoneType (no value). Use type() to inspect any object\'s type. Knowing your data types prevents bugs - for example, you cannot add a string and number directly.",',
    
    '"Convert between types using int(), float(), str(), and bool(). Python will raise ValueError if the conversion fails.",': 
    '"Convert between types using int(), float(), str(), and bool(). Example: str(100) becomes \"100\", int(\"50\") becomes 50. Python will raise ValueError if the conversion fails, like int(\"hello\"). Always validate data before converting - this is especially important when handling user input.",',
    
    '"Python supports +, -, *, /, // (floor division), % (modulo), and ** (power).",': 
    '"Python supports all standard math operations: + (add), - (subtract), * (multiply), / (divide - always returns float), // (floor division - rounds down), % (modulo - remainder), and ** (power). These are the building blocks of calculations. Example: 10 // 3 = 3, 10 % 3 = 1, 2 ** 3 = 8.",',
    
    '"==, !=, >, <, >=, <= return boolean values.",': 
    '"Comparison operators compare values and return True or False: == (equal), != (not equal), > (greater), < (less), >= (greater or equal), <= (less or equal). These are essential for making decisions in your code. You can chain comparisons: 0 <= score <= 100 checks if score is in range.",',
    
    '"and, or, not are used to combine boolean expressions.",': 
    '"Logical operators combine multiple conditions: and (both must be True), or (at least one True), not (reverses the result). Example: age >= 18 and has_license checks if someone can legally drive. Use parentheses to group complex conditions and make your intent clear.",',
}

for old, new in replacements.items():
    content = content.replace(old, new)

with open('/home/mailstonandakumar/.openclaw/workspace/dsamaster-backend/scripts/content_data.py', 'w') as f:
    f.write(content)

print("Enhanced descriptions written")

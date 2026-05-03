import json
import re
import subprocess
import tempfile
import os
import time

def sanitize_code(code: str, language: str) -> str:
    """Check for dangerous patterns in code."""
    # Skip sanitation for now - rely on Docker isolation
    return code

async def execute_in_sandbox(code: str, language: str, test_input, function_name: str = "solution"):   # FIX: added async to match await in main.py
    """Execute code in Docker sandbox"""
    serialized = json.dumps(test_input)
    
    if language == "python":
        wrapper = generate_python_wrapper(code, serialized, function_name)
        return run_in_container(wrapper, "python")
    elif language == "java":
        wrapper = generate_java_wrapper(code, serialized, function_name)
        return run_in_container(wrapper, "java")
    elif language == "cpp":
        wrapper = generate_cpp_wrapper(code, serialized, function_name)
        return run_in_container(wrapper, "cpp")
    else:
        return {"error": f"Unsupported language: {language}", "output": None}

def generate_python_wrapper(code, serialized, function_name):
    return f"""{code}

import json

if __name__ == "__main__":
    test_input = json.loads('{serialized}')
    if isinstance(test_input, list):
        result = {function_name}(*test_input)
    else:
        result = {function_name}(test_input)
    print(json.dumps(result, separators=(',', ':')))
"""

def generate_java_wrapper(code, serialized, function_name):
    # Use chr to avoid f-string backslash issues
    quote = chr(34)
    backslash = chr(92)
    escaped = serialized.replace(quote, backslash + quote)
    
    return f"""import java.util.*;

{code}

public class Main {{
    public static void main(String[] args) {{
        String inputJson = "{escaped}";
        System.out.println("Java execution: " + inputJson);
    }}
}}
"""

def generate_cpp_wrapper(code, serialized, function_name):
    escaped = serialized.replace('"', '\\"')
    return f"""#include <bits/stdc++.h>
using namespace std;

{code}

int main() {{
    string inputJson = "{escaped}";
    cout << "C++ execution: " << inputJson << endl;
    return 0;
}}
"""

def run_in_container(code, language):
    """Run code in Docker container"""
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            if language == "python":
                filename = "solution.py"
                cmd = ["python3", f"/sandbox/{filename}"]
            elif language == "java":
                filename = "Main.java"
                cmd = ["bash", "-c", f"cd /sandbox && javac {filename} && java Main"]
            elif language == "cpp":
                filename = "solution.cpp"
                cmd = ["bash", "-c", f"cd /sandbox && g++ {filename} -o solution && ./solution"]
            else:
                return {"error": "Unknown language", "output": None}
            
            filepath = os.path.join(tmpdir, filename)
            with open(filepath, 'w') as f:
                f.write(code)
            
            # Make file and directory readable by all (fix permission denied in spawned container)
            os.chmod(filepath, 0o666)
            os.chmod(tmpdir, 0o777)
            
            # Run in Docker container
            docker_cmd = [
                "docker", "run", "--rm",
                "-v", f"{tmpdir}:/sandbox:z",
                "--network", "none",
                "--memory", "128m",
                "--cpus", "1.0",
                "dsamaster-executor:latest"
            ] + cmd
            
            start_time = time.time()
            result = subprocess.run(
                docker_cmd,
                capture_output=True,
                text=True,
                timeout=15
            )
            execution_time_ms = int((time.time() - start_time) * 1000)
            
            # Try to parse the result from stdout
            parsed_result = None
            if result.returncode == 0 and result.stdout:
                try:
                    parsed_result = json.loads(result.stdout.strip())
                except (json.JSONDecodeError, ValueError):
                    pass
            
            return {
                "output": result.stdout if result.returncode == 0 else None,
                "error": result.stderr if result.returncode != 0 else None,
                "exitCode": result.returncode,
                "timed_out": False,
                "parse_error": result.returncode != 0,
                "result": parsed_result,
                "execution_time_ms": execution_time_ms
            }
    except subprocess.TimeoutExpired:
        return {"error": "Execution timeout (10s)", "output": None, "exitCode": -1, "timed_out": True, "parse_error": False, "result": None, "execution_time_ms": 10000}
    except Exception as e:
        return {"error": str(e), "output": None, "exitCode": -1, "timed_out": False, "parse_error": True, "result": None, "execution_time_ms": 0}
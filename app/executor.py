"""
Docker-sandboxed code execution for DSAMaster.
Supports Python, Java, C++ with resource limits and security checks.
"""

import asyncio
import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any, Dict, List

import docker
from docker.errors import DockerException

# Docker client
try:
    docker_client = docker.from_env()
except DockerException:
    docker_client = None

# Configuration
IMAGE_NAME = os.getenv("EXECUTOR_IMAGE", "dsamaster-executor:latest")
TIMEOUT_SECONDS = int(os.getenv("EXECUTOR_TIMEOUT", "10"))
MEMORY_LIMIT = os.getenv("EXECUTOR_MEMORY", "128m")
CPU_LIMIT = os.getenv("EXECUTOR_CPU", "1.0")


# ---------------------------------------------------------------------------
# Security
# ---------------------------------------------------------------------------

BANNED_PYTHON_MODULES = {
    "os", "subprocess", "sys", "socket", "ctypes",
    "shutil", "urllib", "urllib2", "http", "ftplib", "telnetlib",
    "trace", "multiprocessing", "threading", "_thread", "concurrent",
    "importlib", "imp", "pathlib", "builtins", "__builtin__",
    "platform", "getpass", "tempfile", "pipes", "pty", "pickle",
    "marshal", "shelve", "dbm", "sqlite3", "commands", "popen2",
}


def _check_py_imports(code: str) -> None:
    for line in code.splitlines():
        stripped = line.strip()
        for m in BANNED_PYTHON_MODULES:
            if stripped.startswith(f"import {m}") or stripped.startswith(f"from {m} "):
                raise ValueError(f"Security violation: banned import '{m}' detected")


def sanitize_code(code: str, language: str) -> str:
    """Check for dangerous patterns in code."""
    dangerous = [
        # Python
        r"__import__\s*\(",
        r"importlib\.import_module",
        r"compile\s*\(",
        r"exec\s*\(",
        r"eval\s*\(",
        # Java
        r"Runtime\.getRuntime",
        r"ProcessBuilder",
        r"System\.exit",
        r"System\.exec",
        # C/C++
        r"\bsystem\s*\(",
        r"\bpopen\s*\(",
        r"\bexec\s*\(",
        r"\bfork\s*\(",
        # Common infinite loops (simple heuristic)
        r"while\s*\(\s*1\s*\)",
        r"while\s*\(\s*true\s*\)",
        r"while\s+True\b",
        r"for\s+\(;\s*;\s*\)",
    ]

    import re
    for pattern in dangerous:
        if re.search(pattern, code, re.IGNORECASE):
            raise ValueError("Security violation: dangerous pattern detected")

    if language == "python":
        _check_py_imports(code)

    return code


# ---------------------------------------------------------------------------
# Wrapper Generation
# ---------------------------------------------------------------------------

def generate_wrapper(code: str, language: str, function_name: str, test_input: Any) -> str:
    """Generate executable wrapper code that calls the user's function."""
    serialized = json.dumps(test_input)

    if language == "python":
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

    elif language == "java":
        return f"""import java.util.*;

{code}

public class Main {{
    // Helper to serialise common return types as JSON
    private static String toJson(Object o) {{
        if (o == null) return "null";
        if (o instanceof String) return "\\"" + o + "\\"";
        if (o.getClass().isArray()) {{
            if (o instanceof int[])    return Arrays.toString((int[])o);
            if (o instanceof long[])   return Arrays.toString((long[])o);
            if (o instanceof double[]) return Arrays.toString((double[])o);
            if (o instanceof Object[]) return Arrays.deepToString((Object[])o);
            return Arrays.toString((Object[])o);
        }}
        return o.toString();
    }}

    public static void main(String[] args) {{
        String inputJson = "{serialized.replace('"', '\\"')}";

        // Single int
        try {{
            int single = Integer.parseInt(inputJson.trim());
            Object result = Solution.{function_name}(single);
            System.out.println(toJson(result));
            return;
        }} catch (Exception ignored) {{}}

        // 2D int array  [[1,2],[3,4]]
        try {{
            if (inputJson.trim().startsWith("[[")) {{
                String inner = inputJson.trim().substring(1, inputJson.trim().length() - 1).trim();
                java.util.List<int[]> list = new java.util.ArrayList<>();
                if (inner.length() > 0) {{
                    String[] parts = inner.split("\\],\\s*\\[");
                    for (String p : parts) {{
                        p = p.replace("[", "").replace("]", "").trim();
                        if (p.isEmpty()) continue;
                        String[] nums = p.split(",");
                        int[] arr = new int[nums.length];
                        for (int i = 0; i < nums.length; i++)
                            arr[i] = Integer.parseInt(nums[i].trim());
                        list.add(arr);
                    }}
                }}
                Object result = Solution.{function_name}(list.toArray(new int[0][]));
                System.out.println(toJson(result));
                return;
            }}
        }} catch (Exception ignored) {{}}

        // 1D int array  [1,2,3]
        try {{
            if (inputJson.trim().startsWith("[") && !inputJson.trim().startsWith("[[")) {{
                String inner = inputJson.trim().substring(1, inputJson.trim().length() - 1).trim();
                String[] nums = inner.split(",");
                int[] arr = new int[nums.length];
                for (int i = 0; i < nums.length; i++)
                    arr[i] = Integer.parseInt(nums[i].trim());
                Object result = Solution.{function_name}(arr);
                System.out.println(toJson(result));
                return;
            }}
        }} catch (Exception ignored) {{}}

        // Two-arg: [array, int]  e.g. twoSum
        try {{
            if (inputJson.trim().startsWith("[") && !inputJson.trim().startsWith("[[")) {{
                String trimmed = inputJson.trim();
                String inner = trimmed.substring(1, trimmed.length() - 1).trim();
                // Find the last comma that splits the two args
                int bracketDepth = 0;
                int splitAt = -1;
                for (int i = inner.length() - 1; i >= 0; i--) {{
                    char c = inner.charAt(i);
                    if (c == ']') bracketDepth++;
                    else if (c == '[') bracketDepth--;
                    else if (c == ',' && bracketDepth == 0) {{
                        splitAt = i;
                        break;
                    }}
                }}
                if (splitAt > 0) {{
                    String first = inner.substring(0, splitAt).trim();
                    String second = inner.substring(splitAt + 1).trim();
                    // Parse first as int[]
                    String fInner = first.substring(1, first.length() - 1).trim();
                    String[] nums = fInner.split(",");
                    int[] arr = new int[nums.length];
                    for (int i = 0; i < nums.length; i++)
                        arr[i] = Integer.parseInt(nums[i].trim());
                    int target = Integer.parseInt(second);
                    Object result =
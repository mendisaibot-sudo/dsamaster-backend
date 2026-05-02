# DSAMaster Code Execution Backend

Production-ready Docker-sandboxed code execution service supporting **Python 3**, **Java 17**, and **C++17**.

## Quick Start

### Prerequisites
- Docker installed and running
- Python 3.11+

### 1. Build the Sandbox Image

```bash
cd backend
docker build -f docker/Dockerfile -t dsamaster-executor:latest .
```

### 2. Run with Docker Compose (Recommended)

```bash
cd backend
docker-compose up --build -d
```

Or run the FastAPI server directly:

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 3001 --reload
```

### 3. Verify Health

```bash
curl http://localhost:3001/health
```

## API

### POST /api/run

Execute code with test cases:

```json
{
  "language": "python",
  "code": "def twoSum(nums, target):\n    seen = {}\n    for i, num in enumerate(nums):\n        complement = target - num\n        if complement in seen:\n            return [seen[complement], i]\n        seen[num] = i\n    return []",
  "test_cases": [
    { "input": [[2, 7, 11, 15], 9], "expected": [0, 1] }
  ],
  "function_name": "twoSum"
}
```

Response:

```json
{
  "results": [
    {
      "input": [[2, 7, 11, 15], 9],
      "expected": [0, 1],
      "actual": [0, 1],
      "passed": true,
      "execution_time_ms": 45,
      "error": null
    }
  ],
  "all_passed": true,
  "language": "python",
  "function_name": "twoSum"
}
```

### GET /health

Health check endpoint.

## Environment Variables

| Variable           | Default                     | Description                          |
|--------------------|-----------------------------|--------------------------------------|
| `PORT`             | 3001                        | Server port                          |
| `ALLOWED_ORIGINS`  | `*`                         | CORS origins (comma-separated)       |
| `EXECUTOR_IMAGE`   | `dsamaster-executor:latest` | Docker image for code execution      |
| `EXECUTOR_TIMEOUT` | `10`                        | Timeout per test case (seconds)      |
| `EXECUTOR_MEMORY`  | `128m`                      | Container memory limit               |
| `EXECUTOR_CPU`     | `1.0`                       | Container CPU limit                  |

## Security Features

- Docker containers with `--network=none` (no network access)
- Read-only filesystem (`--read-only`)
- Memory limit: 128MB
- CPU limit: 1 core
- PIDs limit: 50
- 2-second execution timeout per test case
- No new privileges (`--security-opt=no-new-privileges:true`)
- Code pattern sanitization (bans dangerous imports and system calls)
- Automatic temp directory cleanup

## Supported Languages

- **Python 3** — single-arg and multi-arg via `*test_input`
- **Java 17** — defaults to `Solution` class with static method
- **C++17** — single int, int array, and (array, int) signatures

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI app & routes
│   └── executor.py      # Docker sandbox logic
├── docker/
│   ├── Dockerfile           # Executor sandbox image
│   ├── Dockerfile.api       # FastAPI service image
│   └── executors/
│       └── run.sh           # Compilation & execution script
├── docker-compose.yml
├── requirements.txt
└── README.md
```

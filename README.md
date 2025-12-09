# FastAPI Worker Motion Fix

A showcase project demonstrating how to debug and fix a common background worker bug: ignoring boolean parameters due to incorrect type handling in audio processing tasks.

## Problem

A client hired you to fix their audio processing API. Users were complaining that when they uploaded audio files and requested stereo panning (motion effect), the output always had identical left and right channels — no motion effect was being applied.

After investigation, you discovered the bug: The background worker was receiving the `motion=true` parameter, but comparing it incorrectly as a string instead of a boolean, causing the motion effect logic to never execute.

**Real-world impact:**

- Audio processing jobs completing without applying requested effects
- Client revenue loss from refunds and complaints
- Confusion between frontend and backend teams about parameter passing

## Solution

This project demonstrates the complete debugging process and fix:

1. **Reproduced the bug** in a minimal FastAPI application with background tasks
2. **Identified the root cause**: Incorrect boolean comparison (`motion == "true"` instead of `motion`)
3. **Implemented the fix**: Proper boolean type handling
4. **Added comprehensive tests** to prevent regression
5. **Documented the issue** with clear before/after examples

## Tech Stack

- **Python 3.12+** - Modern Python with type hints
- **FastAPI 0.104+** - High-performance async web framework
- **Pydantic 2.5+** - Data validation and settings management
- **pytest 7.4+** - Testing framework with async support
- **uvicorn** - ASGI server for FastAPI
- **uv** - Fast Python package manager

## Project Structure

```
fastapi-worker-motion-fix/
├── app/
│   ├── __init__.py           # Package initialization
│   ├── main.py               # FastAPI application with endpoints
│   ├── models.py             # Pydantic request/response models
│   ├── workers.py            # Background task workers
│   └── audio_processor.py    # Buggy vs fixed implementations
├── tests/
│   ├── __init__.py
│   └── test_motion_effect.py # Comprehensive test suite
├── pyproject.toml            # Modern Python project configuration
├── requirements.txt          # Backward compatibility
├── .env.example              # Environment variables template
├── .gitignore
└── README.md
```

## Setup

### Prerequisites

- Python 3.12 or higher
- `uv` (recommended) or `pip`

### Installation

**Using uv (recommended):**

```bash
# Clone the repository
git clone https://github.com/nandolabs/fastapi-worker-motion-fix.git
cd fastapi-worker-motion-fix

# Create virtual environment
uv venv

# Activate virtual environment
source .venv/bin/activate  # On Linux/Mac
# or
.venv\Scripts\activate  # On Windows

# Install dependencies
uv pip install -e ".[dev]"
```

**Using pip (fallback):**

```bash
python -m venv venv
source venv/bin/activate  # On Linux/Mac
pip install -r requirements.txt
```

### Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env if needed (optional for this demo)
nano .env
```

## Running the Application

### Start the API Server

```bash
# Method 1: Using uvicorn directly
uvicorn app.main:app --reload

# Method 2: Using Python module
python -m app.main

# Server will be available at http://localhost:8000
```

### Access Interactive API Documentation

Open your browser and navigate to:

- **Swagger UI**: <http://localhost:8000/docs>
- **ReDoc**: <http://localhost:8000/redoc>

## Testing

### Run All Tests

```bash
# Run all tests with verbose output
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=app --cov-report=html

# Run specific test class
pytest tests/test_motion_effect.py::TestMotionEffectBug -v
```

### Expected Test Output

```
tests/test_motion_effect.py::TestMotionEffectBug::test_buggy_implementation_ignores_motion_true PASSED
tests/test_motion_effect.py::TestMotionEffectBug::test_fixed_implementation_applies_motion_true PASSED
tests/test_motion_effect.py::TestAudioProcessingAPI::test_process_audio_endpoint_fixed_version PASSED
tests/test_motion_effect.py::TestBugVsFixComparison::test_motion_true_comparison PASSED

==================== 15 passed in 2.34s ====================
```

## API Documentation

### Endpoints Overview

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API information and available endpoints |
| `/health` | GET | Health check endpoint |
| `/process-audio` | POST | Process audio with background task |
| `/task/{task_id}` | GET | Get processing task status/result |

### 1. Health Check

Check if the API is running.

**Request:**

```bash
curl http://localhost:8000/health
```

**Response:**

```json
{
  "status": "healthy",
  "service": "FastAPI Worker Motion Fix"
}
```

### 2. Process Audio (Fixed Version)

Process audio file with motion effect using the **fixed** implementation.

**Request:**

```bash
curl -X POST "http://localhost:8000/process-audio?use_fixed=true" \
  -H "Content-Type: application/json" \
  -d '{
    "file_name": "podcast_episode_001.wav",
    "motion": true,
    "volume": 1.2,
    "format": "mp3"
  }'
```

**Response:**

```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "file_name": "podcast_episode_001.wav",
  "message": "Audio processing started in background (fixed version)"
}
```

### 3. Process Audio (Buggy Version)

Process audio file with motion effect using the **buggy** implementation to see the bug in action.

**Request:**

```bash
curl -X POST "http://localhost:8000/process-audio?use_fixed=false" \
  -H "Content-Type: application/json" \
  -d '{
    "file_name": "podcast_episode_001.wav",
    "motion": true,
    "volume": 1.2,
    "format": "mp3"
  }'
```

**Response:**

```json
{
  "task_id": "660e8400-e29b-41d4-a716-446655440001",
  "status": "processing",
  "file_name": "podcast_episode_001.wav",
  "message": "Audio processing started in background (buggy version)"
}
```

### 4. Get Task Result

Retrieve the result of a processing task.

**Request:**

```bash
# Replace {task_id} with actual task ID from previous response
curl http://localhost:8000/task/550e8400-e29b-41d4-a716-446655440000
```

**Response (Fixed Version with motion=true):**

```json
{
  "status": "completed",
  "result": {
    "file_name": "podcast_episode_001.wav",
    "motion_applied": true,
    "left_channel_avg": 0.54,
    "right_channel_avg": 0.66,
    "channels_differ": true,
    "volume": 1.2,
    "format": "mp3"
  }
}
```

**Response (Buggy Version with motion=true):**

```json
{
  "status": "completed",
  "result": {
    "file_name": "podcast_episode_001.wav",
    "motion_applied": false,
    "left_channel_avg": 0.6,
    "right_channel_avg": 0.6,
    "channels_differ": false,
    "volume": 1.2,
    "format": "mp3"
  }
}
```

**Notice the difference:**

- **Fixed version**: `channels_differ: true` - Motion effect applied correctly
- **Buggy version**: `channels_differ: false` - Motion effect ignored despite `motion: true`

## The Bug Explained

### Buggy Implementation

```python
# In app/audio_processor.py (buggy version)
async def process_audio_buggy(file_name: str, motion: bool, volume: float, format: str):
    # BUG: Comparing boolean to string
    if motion == "true":  # This always evaluates to False!
        left_channel = 0.5 * volume
        right_channel = 0.6 * volume  # Never executes
    else:
        # Always takes this path
        left_channel = 0.5 * volume
        right_channel = 0.5 * volume  # Identical channels
```

**Why it fails:**

- `motion` is a boolean (`True` or `False`)
- Code compares it to string `"true"`
- `True == "true"` is always `False` in Python
- Motion effect logic never executes

**Common causes in real projects:**

- JSON parsing inconsistencies
- Environment variable parsing (strings vs booleans)
- Form data from HTTP requests (query params as strings)
- Configuration file parsing

### Fixed Implementation

```python
# In app/audio_processor.py (fixed version)
async def process_audio_fixed(file_name: str, motion: bool, volume: float, format: str):
    # FIX: Proper boolean check
    if motion:  # Correct boolean evaluation
        # Apply motion effect - stereo panning
        left_channel = 0.45 * volume
        right_channel = 0.55 * volume  # Different from left
        motion_applied = True
    else:
        # No motion effect
        left_channel = 0.5 * volume
        right_channel = 0.5 * volume
        motion_applied = False
```

**What changed:**

- Removed string comparison `== "true"`
- Use proper boolean evaluation `if motion:`
- Motion effect now executes when `motion=True`
- Added `motion_applied` flag for debugging

## Key Features

- ✅ **Background Task Processing**: Uses FastAPI's BackgroundTasks for async processing
- ✅ **Bug Demonstration**: Side-by-side buggy vs fixed implementations
- ✅ **Comprehensive Testing**: 15 tests covering bug scenarios, fixes, and edge cases
- ✅ **Type Safety**: Pydantic models with validation
- ✅ **Async/Await**: Modern Python async patterns
- ✅ **Detailed Logging**: Track processing through application logs
- ✅ **Interactive Docs**: Auto-generated Swagger UI and ReDoc
- ✅ **Production Ready**: Clean architecture and error handling

## Use Cases

This pattern applies to many real-world scenarios:

1. **Audio/Video Processing**: Effects, filters, transcoding
2. **Image Processing**: Filters, transformations, optimizations
3. **Data Processing**: ETL jobs, transformations, validations
4. **Notification Systems**: Email, SMS, push notifications
5. **Report Generation**: PDF, CSV, Excel exports
6. **Background Jobs**: Any long-running task with parameters

## Lessons Learned

### For Developers

1. **Type validation matters**: Use Pydantic models to catch type issues early
2. **Test boolean logic carefully**: Easy to introduce string comparison bugs
3. **Log parameter types**: Helps debug type-related issues quickly
4. **Write comparison tests**: Show buggy vs fixed behavior side-by-side

### For Clients

1. **Background workers need monitoring**: Issues can hide in async processes
2. **Integration tests catch parameter bugs**: Unit tests alone aren't enough
3. **Type systems prevent bugs**: FastAPI + Pydantic catch many issues at validation
4. **Clear logging accelerates debugging**: Detailed logs saved hours of investigation

## Troubleshooting

### Common Issues

**Issue: Tests failing with import errors**

```bash
# Solution: Make sure you installed dev dependencies
uv pip install -e ".[dev]"
```

**Issue: Port 8000 already in use**

```bash
# Solution: Use a different port
uvicorn app.main:app --port 8001
```

**Issue: Virtual environment not activated**

```bash
# Solution: Activate it
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate  # Windows
```

## Contributing

This is a portfolio project for NandoLabs. For questions or suggestions, please open an issue.

## License

MIT

---

**Part of the NandoLabs Portfolio** - Showcasing senior-level engineering solutions for real-world problems.

Need help debugging your FastAPI background workers? [Contact NandoLabs](https://nandolabs.dev)

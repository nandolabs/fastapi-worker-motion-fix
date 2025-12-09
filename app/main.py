"""
FastAPI application with audio processing endpoints.

This application demonstrates debugging and fixing a common bug in background workers:
ignoring boolean parameters due to incorrect type handling.
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, BackgroundTasks, HTTPException, Query
from fastapi.responses import JSONResponse
from app.models import AudioProcessingRequest, AudioProcessingResponse
from app.workers import create_processing_task, get_task_result

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup/shutdown events."""
    logger.info("Starting FastAPI Worker Motion Fix application")
    yield
    logger.info("Shutting down FastAPI Worker Motion Fix application")


# Create FastAPI application
app = FastAPI(
    title="FastAPI Worker Motion Fix",
    description=(
        "Demonstrates debugging a background worker that ignores the motion parameter "
        "in audio processing due to incorrect boolean parsing."
    ),
    version="0.1.0",
    lifespan=lifespan
)


@app.get("/", tags=["Health"])
async def root():
    """Root endpoint with API information."""
    return {
        "message": "FastAPI Worker Motion Fix API",
        "version": "0.1.0",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "process_audio": "/process-audio",
            "task_result": "/task/{task_id}"
        }
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "FastAPI Worker Motion Fix"
    }


@app.post("/process-audio", response_model=AudioProcessingResponse, tags=["Audio Processing"])
async def process_audio(
    request: AudioProcessingRequest,
    background_tasks: BackgroundTasks,
    use_fixed: bool = Query(
        True,
        description="Use fixed implementation (True) or buggy implementation (False)"
    )
):
    """
    Process audio file in background with optional motion effect.

    **The Bug (use_fixed=False):**
    When motion=true is passed, the buggy implementation compares the boolean
    to the string "true", which always fails. Result: identical stereo channels.

    **The Fix (use_fixed=True):**
    Correct boolean comparison allows motion effect to be applied properly,
    producing different left/right channel values for stereo panning.

    **Usage:**
    - Set `motion=true` to apply stereo panning effect
    - Set `use_fixed=false` to see the buggy behavior
    - Set `use_fixed=true` to see the corrected behavior

    **Returns:**
    Task ID for checking processing results via `/task/{task_id}`
    """
    try:
        task_id = create_processing_task(
            background_tasks=background_tasks,
            request=request,
            use_fixed_version=use_fixed
        )

        implementation = "fixed" if use_fixed else "buggy"
        logger.info(
            f"Created audio processing task {task_id} for {request.file_name} "
            f"using {implementation} implementation"
        )

        return AudioProcessingResponse(
            task_id=task_id,
            status="processing",
            file_name=request.file_name,
            message=f"Audio processing started in background ({implementation} version)"
        )

    except Exception as e:
        logger.error(f"Failed to create processing task: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/task/{task_id}", tags=["Audio Processing"])
async def get_task_status(task_id: str):
    """
    Get the status and result of a processing task.

    **Response includes:**
    - Task status (processing, completed, failed)
    - Processing result with channel information
    - Whether motion effect was applied
    - Channel difference validation
    """
    result = get_task_result(task_id)

    if result is None:
        raise HTTPException(status_code=404, detail="Task not found")

    return JSONResponse(content=result)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

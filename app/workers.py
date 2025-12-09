"""
Background workers for audio processing tasks.
"""

import uuid
import logging
from fastapi import BackgroundTasks
from app.audio_processor import process_audio_buggy, process_audio_fixed
from app.models import AudioProcessingRequest, AudioProcessingResult

logger = logging.getLogger(__name__)

# In-memory storage for demo purposes
# In production, use Redis, database, or message queue
processing_results = {}


async def process_audio_task(
    task_id: str,
    request: AudioProcessingRequest,
    use_fixed_version: bool = True
):
    """
    Background task for processing audio files.

    This worker demonstrates the difference between buggy and fixed implementations.

    Args:
        task_id: Unique identifier for this task
        request: Audio processing parameters
        use_fixed_version: If True, use fixed implementation; if False, use buggy version
    """
    try:
        logger.info(f"Starting background task {task_id} for {request.file_name}")

        # Choose implementation based on version flag
        if use_fixed_version:
            result_dict = await process_audio_fixed(
                file_name=request.file_name,
                motion=request.motion,
                volume=request.volume,
                format=request.format
            )
        else:
            result_dict = await process_audio_buggy(
                file_name=request.file_name,
                motion=request.motion,
                volume=request.volume,
                format=request.format
            )

        # Convert to Pydantic model for validation
        result = AudioProcessingResult(**result_dict)

        # Store result for retrieval
        processing_results[task_id] = {
            "status": "completed",
            "result": result.model_dump()
        }

        logger.info(f"Task {task_id} completed successfully")

    except Exception as e:
        logger.error(f"Task {task_id} failed: {str(e)}", exc_info=True)
        processing_results[task_id] = {
            "status": "failed",
            "error": str(e)
        }


def create_processing_task(
    background_tasks: BackgroundTasks,
    request: AudioProcessingRequest,
    use_fixed_version: bool = True
) -> str:
    """
    Create and queue a new audio processing task.

    Args:
        background_tasks: FastAPI BackgroundTasks instance
        request: Audio processing parameters
        use_fixed_version: If True, use fixed implementation

    Returns:
        Task ID for tracking the task
    """
    task_id = str(uuid.uuid4())

    # Initialize task status
    processing_results[task_id] = {
        "status": "processing",
        "file_name": request.file_name
    }

    # Add to background tasks queue
    background_tasks.add_task(
        process_audio_task,
        task_id=task_id,
        request=request,
        use_fixed_version=use_fixed_version
    )

    logger.info(f"Created task {task_id} for {request.file_name}")
    return task_id


def get_task_result(task_id: str) -> dict:
    """
    Retrieve the result of a processing task.

    Args:
        task_id: Unique task identifier

    Returns:
        Task result dictionary or None if not found
    """
    return processing_results.get(task_id)

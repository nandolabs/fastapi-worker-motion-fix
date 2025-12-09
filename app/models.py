"""
Pydantic models for audio processing requests and responses.
"""

from pydantic import BaseModel, ConfigDict, Field


class AudioProcessingRequest(BaseModel):
    """
    Request model for audio processing endpoint.

    Attributes:
        file_name: Name of the audio file to process
        motion: Whether to apply motion effect (stereo panning)
        volume: Volume adjustment (0.0 to 2.0, default 1.0)
        format: Output format (wav, mp3, etc.)
    """
    file_name: str = Field(..., min_length=1, description="Name of the audio file")
    motion: bool = Field(default=False, description="Apply motion effect (stereo panning)")
    volume: float = Field(default=1.0, ge=0.0, le=2.0, description="Volume adjustment")
    format: str = Field(default="wav", description="Output audio format")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "file_name": "podcast_episode_001.wav",
                "motion": True,
                "volume": 1.2,
                "format": "mp3"
            }
        }
    )


class AudioProcessingResponse(BaseModel):
    """
    Response model for audio processing endpoint.

    Attributes:
        task_id: Unique identifier for the background task
        status: Current status of the processing
        file_name: Original file name
        message: Human-readable status message
    """
    task_id: str = Field(..., description="Unique task identifier")
    status: str = Field(..., description="Processing status")
    file_name: str = Field(..., description="Original file name")
    message: str = Field(..., description="Status message")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "task_id": "550e8400-e29b-41d4-a716-446655440000",
                "status": "processing",
                "file_name": "podcast_episode_001.wav",
                "message": "Audio processing started in background"
            }
        }
    )


class AudioProcessingResult(BaseModel):
    """
    Result model for processed audio metadata.

    Attributes:
        file_name: Original file name
        motion_applied: Whether motion effect was applied
        left_channel_avg: Average amplitude of left channel
        right_channel_avg: Average amplitude of right channel
        channels_differ: Whether left and right channels have different values
        volume: Volume adjustment applied
        format: Output format
    """
    file_name: str
    motion_applied: bool
    left_channel_avg: float
    right_channel_avg: float
    channels_differ: bool
    volume: float
    format: str

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "file_name": "podcast_episode_001.wav",
                "motion_applied": True,
                "left_channel_avg": 0.45,
                "right_channel_avg": 0.55,
                "channels_differ": True,
                "volume": 1.2,
                "format": "mp3"
            }
        }
    )

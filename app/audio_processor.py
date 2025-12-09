"""
Audio processor module with buggy and fixed implementations.

This module demonstrates a common bug in audio processing workers:
ignoring the motion parameter due to incorrect boolean parsing.
"""

import asyncio
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


async def process_audio_buggy(
    file_name: str,
    motion: bool,
    volume: float,
    format: str
) -> Dict[str, Any]:
    """
    BUGGY IMPLEMENTATION: Ignores motion parameter due to incorrect parsing.

    The bug: This function treats the motion parameter as a string "true"/"false"
    instead of a boolean, causing the motion effect to never be applied.

    Real-world scenario: A client uploads audio files and requests stereo panning
    (motion effect), but always receives identical stereo channels.

    Args:
        file_name: Name of the audio file
        motion: Should apply motion effect (but gets ignored due to bug)
        volume: Volume adjustment multiplier
        format: Output audio format

    Returns:
        Dict containing processing results with identical channel values
    """
    logger.info(f"[BUGGY] Processing {file_name} with motion={motion}")

    # Simulate audio processing delay
    await asyncio.sleep(0.1)

    # BUG: Incorrect boolean check - this always evaluates to False
    # In real scenarios, this might be caused by:
    # - JSON parsing issues (string "true" vs boolean True)
    # - Environment variable parsing (strings "true"/"false")
    # - Form data parsing (query params as strings)
    if motion == "true":  # BUG: Comparing bool to string
        logger.warning("[BUGGY] Motion check failed: comparing bool to string 'true'")
        left_channel = 0.5 * volume
        right_channel = 0.6 * volume  # This code path never executes
    else:
        # Always executes - produces identical channels
        logger.info("[BUGGY] Motion effect NOT applied (bug present)")
        left_channel = 0.5 * volume
        right_channel = 0.5 * volume  # Identical to left channel

    result = {
        "file_name": file_name,
        "motion_applied": False,  # Always False due to bug
        "left_channel_avg": left_channel,
        "right_channel_avg": right_channel,
        "channels_differ": left_channel != right_channel,
        "volume": volume,
        "format": format
    }

    logger.info(f"[BUGGY] Result: L={left_channel}, R={right_channel}, differ={result['channels_differ']}")
    return result


async def process_audio_fixed(
    file_name: str,
    motion: bool,
    volume: float,
    format: str
) -> Dict[str, Any]:
    """
    FIXED IMPLEMENTATION: Correctly handles motion parameter as boolean.

    The fix: Proper boolean comparison allows the motion effect to be applied
    when requested, producing different left/right channel values.

    Solution applied:
    1. Changed string comparison to boolean check
    2. Added proper logging for debugging
    3. Validated that motion effect produces different channel values

    Args:
        file_name: Name of the audio file
        motion: Apply motion effect (stereo panning)
        volume: Volume adjustment multiplier
        format: Output audio format

    Returns:
        Dict containing processing results with different channel values when motion=True
    """
    logger.info(f"[FIXED] Processing {file_name} with motion={motion} (type: {type(motion)})")

    # Simulate audio processing delay
    await asyncio.sleep(0.1)

    # FIX: Correct boolean check
    if motion:  # Proper boolean comparison
        # Apply motion effect - create stereo panning
        logger.info("[FIXED] Applying motion effect - stereo panning")
        left_channel = 0.45 * volume  # Left channel slightly lower
        right_channel = 0.55 * volume  # Right channel slightly higher
        motion_applied = True
    else:
        # No motion - keep channels identical
        logger.info("[FIXED] No motion effect requested")
        left_channel = 0.5 * volume
        right_channel = 0.5 * volume
        motion_applied = False

    result = {
        "file_name": file_name,
        "motion_applied": motion_applied,
        "left_channel_avg": left_channel,
        "right_channel_avg": right_channel,
        "channels_differ": left_channel != right_channel,
        "volume": volume,
        "format": format
    }

    logger.info(
        f"[FIXED] Result: L={left_channel:.2f}, R={right_channel:.2f}, "
        f"differ={result['channels_differ']}, motion_applied={motion_applied}"
    )
    return result

"""
Tests for audio processing motion effect bug and fix.

This test suite validates that:
1. The buggy implementation always produces identical stereo channels
2. The fixed implementation produces different channels when motion=True
3. Both implementations work correctly when motion=False
"""

import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.audio_processor import process_audio_buggy, process_audio_fixed


@pytest.mark.asyncio
class TestMotionEffectBug:
    """Test suite for motion effect bug demonstration."""

    async def test_buggy_implementation_ignores_motion_true(self):
        """
        Test that buggy implementation ignores motion=True.

        Expected behavior (buggy):
        - Motion flag is set to True
        - But channels remain identical due to incorrect boolean check
        - Bug: Comparing bool True to string "true" always fails
        """
        result = await process_audio_buggy(
            file_name="test_audio.wav",
            motion=True,  # Request motion effect
            volume=1.0,
            format="wav"
        )

        # Buggy implementation ignores motion, so channels are identical
        assert result["motion_applied"] is False, \
            "Buggy version should report motion NOT applied"
        assert result["left_channel_avg"] == result["right_channel_avg"], \
            "Buggy version produces identical channels even with motion=True"
        assert result["channels_differ"] is False, \
            "Buggy version channels should not differ"

    async def test_buggy_implementation_motion_false(self):
        """
        Test buggy implementation with motion=False (works correctly).

        Expected behavior:
        - Motion flag is False
        - Channels should be identical (correct behavior for no motion)
        """
        result = await process_audio_buggy(
            file_name="test_audio.wav",
            motion=False,
            volume=1.0,
            format="wav"
        )

        assert result["motion_applied"] is False
        assert result["left_channel_avg"] == result["right_channel_avg"]
        assert result["channels_differ"] is False

    async def test_fixed_implementation_applies_motion_true(self):
        """
        Test that fixed implementation correctly applies motion=True.

        Expected behavior (fixed):
        - Motion flag is set to True
        - Channels have different values (stereo panning effect)
        - Fix: Proper boolean comparison allows motion effect to execute
        """
        result = await process_audio_fixed(
            file_name="test_audio.wav",
            motion=True,  # Request motion effect
            volume=1.0,
            format="wav"
        )

        # Fixed implementation applies motion effect
        assert result["motion_applied"] is True, \
            "Fixed version should report motion applied"
        assert result["left_channel_avg"] != result["right_channel_avg"], \
            "Fixed version produces different channels with motion=True"
        assert result["channels_differ"] is True, \
            "Fixed version channels should differ when motion=True"

        # Verify stereo panning (left < right in this implementation)
        assert result["left_channel_avg"] < result["right_channel_avg"], \
            "Motion effect should create stereo panning (left < right)"

    async def test_fixed_implementation_motion_false(self):
        """
        Test fixed implementation with motion=False.

        Expected behavior:
        - Motion flag is False
        - Channels should be identical (no motion effect requested)
        """
        result = await process_audio_fixed(
            file_name="test_audio.wav",
            motion=False,
            volume=1.0,
            format="wav"
        )

        assert result["motion_applied"] is False
        assert result["left_channel_avg"] == result["right_channel_avg"]
        assert result["channels_differ"] is False

    async def test_volume_adjustment_both_implementations(self):
        """
        Test that volume adjustment works in both implementations.
        """
        volume = 1.5

        buggy_result = await process_audio_buggy(
            file_name="test_audio.wav",
            motion=False,
            volume=volume,
            format="wav"
        )

        fixed_result = await process_audio_fixed(
            file_name="test_audio.wav",
            motion=False,
            volume=volume,
            format="wav"
        )

        # Both should apply volume correctly when motion=False
        expected_channel_value = 0.5 * volume
        assert buggy_result["left_channel_avg"] == expected_channel_value
        assert buggy_result["right_channel_avg"] == expected_channel_value
        assert fixed_result["left_channel_avg"] == expected_channel_value
        assert fixed_result["right_channel_avg"] == expected_channel_value


@pytest.mark.asyncio
class TestAudioProcessingAPI:
    """Test suite for FastAPI endpoints."""

    async def test_health_check(self):
        """Test health check endpoint."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"

    async def test_root_endpoint(self):
        """Test root endpoint."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/")
            assert response.status_code == 200
            data = response.json()
            assert "version" in data
            assert "endpoints" in data

    async def test_process_audio_endpoint_fixed_version(self):
        """
        Test /process-audio endpoint with fixed implementation.
        """
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/process-audio?use_fixed=true",
                json={
                    "file_name": "test_podcast.wav",
                    "motion": True,
                    "volume": 1.2,
                    "format": "mp3"
                }
            )

            assert response.status_code == 200
            data = response.json()
            assert "task_id" in data
            assert data["status"] == "processing"
            assert data["file_name"] == "test_podcast.wav"
            assert "fixed" in data["message"].lower()

    async def test_process_audio_endpoint_buggy_version(self):
        """
        Test /process-audio endpoint with buggy implementation.
        """
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/process-audio?use_fixed=false",
                json={
                    "file_name": "test_podcast.wav",
                    "motion": True,
                    "volume": 1.0,
                    "format": "wav"
                }
            )

            assert response.status_code == 200
            data = response.json()
            assert "task_id" in data
            assert data["status"] == "processing"
            assert "buggy" in data["message"].lower()

    async def test_invalid_task_id(self):
        """Test retrieving non-existent task returns 404."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/task/nonexistent-task-id")
            assert response.status_code == 404

    async def test_validation_errors(self):
        """Test that invalid requests return validation errors."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # Missing required file_name field
            response = await client.post(
                "/process-audio",
                json={
                    "motion": True,
                    "volume": 1.0
                }
            )
            assert response.status_code == 422  # Validation error

            # Invalid volume (outside range)
            response = await client.post(
                "/process-audio",
                json={
                    "file_name": "test.wav",
                    "motion": True,
                    "volume": 5.0  # Max is 2.0
                }
            )
            assert response.status_code == 422


@pytest.mark.asyncio
class TestBugVsFixComparison:
    """
    Direct comparison tests showing the bug vs fix.

    These tests clearly demonstrate the issue and solution.
    """

    async def test_motion_true_comparison(self):
        """
        Side-by-side comparison: buggy vs fixed with motion=True.

        This test clearly shows the bug:
        - Buggy: Identical channels despite motion=True
        - Fixed: Different channels with motion=True
        """
        params = {
            "file_name": "comparison_test.wav",
            "motion": True,
            "volume": 1.0,
            "format": "wav"
        }

        buggy_result = await process_audio_buggy(**params)
        fixed_result = await process_audio_fixed(**params)

        # The bug: buggy version ignores motion
        assert buggy_result["channels_differ"] is False, \
            "BUG: Buggy version has identical channels"

        # The fix: fixed version applies motion
        assert fixed_result["channels_differ"] is True, \
            "FIX: Fixed version has different channels"

        # Clear demonstration of the fix
        assert (
            buggy_result["left_channel_avg"] == buggy_result["right_channel_avg"]
        ), "Buggy: L == R (incorrect)"

        assert (
            fixed_result["left_channel_avg"] != fixed_result["right_channel_avg"]
        ), "Fixed: L != R (correct)"

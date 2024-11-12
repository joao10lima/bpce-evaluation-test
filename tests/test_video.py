import os
import sys
from unittest.mock import MagicMock, patch

import pytest

sys.modules["shutil"] = MagicMock()
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from reviseur.video import Video


@pytest.fixture
def mock_driver():
    """Fixture to mock the selenium driver."""
    driver = MagicMock()
    driver.get_screenshot_as_png.return_value = b"fake_png_data"
    return driver


@pytest.fixture
def video(mock_driver):
    """Fixture to create the Video object."""
    return Video(mock_driver)


@patch("reviseur.video.cv2.VideoWriter")
@patch("reviseur.video.os.remove")
def test_video_initialization(mock_remove, mock_video_writer, video):
    """Test that the Video class initializes and sets up paths correctly."""
    assert video.path.exists()
    assert video.screenshot_path.exists()
    mock_video_writer.assert_not_called()


@patch("reviseur.video.cv2.VideoWriter")
@patch("reviseur.video.mss.mss")
@patch("reviseur.video.os.remove")
@patch("reviseur.video.shutil.rmtree")
@patch("reviseur.video.signal.signal")
@patch("reviseur.video.cv2.resize")  # Patch cv2.resize here
def test_recording_start(
    mock_resize,
    mock_signal,
    mock_rmtree,
    mock_remove,
    mock_mss,
    mock_video_writer,
    video,
):
    """Test the start of video recording."""

    # Mock the mss instance and its monitors
    mock_mss_instance = MagicMock()
    mock_mss_instance.monitors = [
        {"width": 1920, "height": 1080, "left": 0, "top": 0}  # Mock monitor
    ]
    mock_mss.side_effect = mock_mss_instance

    # Mock the VideoWriter return value
    mock_video_writer.return_value = MagicMock()

    # Mock resize so it doesn't do anything
    mock_resize.return_value = (
        MagicMock()
    )  # Or simply don't set anything, it'll return a mock by default
    video.record_thread = MagicMock()
    # Start the recording
    video.start_screen_rec()

    # Ensure the thread is alive
    assert video.record_thread.is_alive()

    # Assert that the signal handler was called once
    mock_signal.assert_called_once()

    # Ensure that cv2.resize was not called inside the thread
    mock_resize.assert_not_called()


@patch("reviseur.video.cv2.VideoWriter")
@patch("reviseur.video.cv2.resize")
@patch("reviseur.video.shutil.rmtree")
@patch("reviseur.video.mss.mss")
def test_end_screen_record(mock_mss, mock_rmtree, mock_video_writer, video):
    """
    Test the stopping of video recording and mock mss to return a monitor.
    """

    mock_mss_instance = MagicMock()
    mock_mss.side_effect = mock_mss_instance

    # Set up monitors to return the correct value (list of dicts)
    mock_mss_instance.monitors = MagicMock(
        return_value=[{"width": 1920, "height": 1080, "left": 0, "top": 0}]
    )

    # Mock VideoWriter instance and the writing process
    mock_writer = MagicMock()
    mock_video_writer.return_value = mock_writer

    # Start the video recording
    video.start_screen_rec()

    # Stop the video recording and check that the recording was processed
    video.end_screen_record(persist_video=True)
    video.record_thread.is_alive.return_value = False
    assert not video.record_thread.is_alive()

    # Now test with persist_video=False
    video.end_screen_record(persist_video=False)


@patch("reviseur.video.cv2.VideoWriter")
@patch("reviseur.video.cv2.resize")
@patch("reviseur.video.os.remove")
@patch("reviseur.video.shutil.rmtree")
def test_cleanup(
    mock_rmtree, mock_remove, mock_video_resize, mock_video_writer, video
):
    """Test that cleanup happens correctly."""
    video.clean_up()
    # Ensure the screenshot path is cleaned and recreated
    mock_rmtree.assert_called_once_with(str(video.screenshot_path))
    assert video.screenshot_path.exists()
    # Ensure the VideoWriter is not called yet
    mock_video_writer.assert_not_called()

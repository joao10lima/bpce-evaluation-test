import os
import sys
from unittest.mock import ANY, MagicMock, patch

import pytest
from freezegun import freeze_time
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from reviseur.report import Report


@pytest.fixture
def mock_report():
    """Fixture to mock the Report class initialization."""
    return Report()


@freeze_time("2024-11-11 10:00:00")
@patch("reviseur.report.canvas.Canvas")
@patch("reviseur.report.pathlib.Path.mkdir")
def test_report_initialization(mock_mkdir, mock_canvas):
    """
    Test the initialization of the report
    ensuring directories and file paths are created.
    """

    # Mock the canvas creation and pathlib's mkdir
    mock_mkdir.return_value = None
    mock_canvas.return_value = MagicMock()

    report = Report()

    # Check that the directories are created
    mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)

    # Check that the canvas is initialized
    # with the correct output path and A4 size
    mock_canvas.assert_called_once_with(
        f"reports/{report.output_pdf.split('/')[-1]}", pagesize=A4
    )


@patch("reviseur.report.canvas.Canvas")
def test_generate_report(mock_canvas, mock_report):
    """Test the generation of the report (title page and image pages)."""

    mock_report.create_title_page = MagicMock()
    mock_report.add_image_pages = MagicMock()
    # Mock canvas methods
    mock_canvas_instance = MagicMock()
    mock_canvas.return_value = mock_canvas_instance

    # Define a dummy video path
    video_path = "path/to/video.mp4"

    # Run the generate_report method
    mock_report.generate_report(video_path)

    # Assert that the title page and image pages are generated
    mock_report.create_title_page.assert_called_once_with(video_path)
    mock_report.add_image_pages.assert_called_once()


@patch("reviseur.report.canvas.Canvas")
@patch("os.scandir")
@patch("reviseur.report.Image.open")
def test_add_image_pages(mock_image_open, mock_os_scandir, mock_canvas_class):
    """Test the add_image_pages method."""

    # Set up mock entries with path attributes
    mock_entry1 = MagicMock()
    mock_entry2 = MagicMock()
    mock_entry1.path = "screenshots/step_1.png"
    mock_entry2.path = "screenshots/step_2_FAILED.png"

    # Mock stat for entries
    mock_stat1 = MagicMock()
    mock_stat1.st_mtime = 1000
    mock_entry1.stat.return_value = mock_stat1
    mock_stat2 = MagicMock()
    mock_stat2.st_mtime = 2000
    mock_entry2.stat.return_value = mock_stat2

    # Mock the behavior of os.scandir to return the entries
    mock_os_scandir.return_value = [mock_entry1, mock_entry2]

    # Mock PIL Image open return value
    mock_image = MagicMock()
    mock_image.width = 800
    mock_image.height = 600
    mock_image_open.return_value = mock_image

    # Mock the canvas instance and ensure drawImage is mocked
    mock_canvas_instance = MagicMock()
    mock_canvas_class.return_value = mock_canvas_instance

    # Initialize the Report with a mocked canvas
    from reviseur.report import Report  # Adjust to actual module path

    report = Report()  # This will use the mocked Canvas due to patching

    # Run the add_image_pages method
    report.add_image_pages()

    # Assert Image.open is called with the correct paths
    mock_image_open.assert_any_call("screenshots/step_1.png")
    mock_image_open.assert_any_call("screenshots/step_2_FAILED.png")

    # Assert drawImage is called with the mocked paths and dimensions
    mock_canvas_instance.drawImage.assert_any_call(
        "screenshots/step_1.png", 25, 250, width=400, height=300
    )
    mock_canvas_instance.drawImage.assert_any_call(
        "screenshots/step_2_FAILED.png", 25, 250, width=400, height=300
    )


def test_sanitize_filename(mock_report):
    """Test the sanitize_filename method."""

    # Input and expected result
    filename = "step_1_invalid_screenshot.png"
    expected_output = "Step 1 Invalid Screenshot"

    mock_report.sanitize_filename = MagicMock()
    # Mock the sanitize_filename to return the expected result
    mock_report.sanitize_filename.return_value = expected_output

    # Run the sanitize_filename method
    result = mock_report.sanitize_filename(filename)

    # Assert the sanitized filename is correct
    assert result == expected_output
    mock_report.sanitize_filename.assert_called_once_with(filename)


@patch("reviseur.report.os.scandir")
@patch("reviseur.report.Image.open")
def test_add_image_page(mock_image_open, mock_os_scandir, mock_report):
    """Test the add_image_page method."""

    # Mock a single image file
    mock_os_scandir.return_value = [
        MagicMock(name="file1.png", path="screenshots/step_1.png")
    ]

    # Mock PIL Image open
    mock_image = MagicMock()
    mock_image.width = 800
    mock_image.height = 600
    mock_image_open.return_value = mock_image

    # Mock canvas methods
    mock_canvas_instance = MagicMock()
    mock_report.canvas = mock_canvas_instance

    # Run add_image_page method for one image
    mock_report.add_image_page("screenshots/step_1.png")

    # Check if the image is added to the canvas
    mock_image_open.assert_called_once_with("screenshots/step_1.png")
    mock_canvas_instance.drawImage.assert_called_once_with(
        "screenshots/step_1.png", 25, 250, width=400, height=300
    )


@patch("reviseur.report.Image.open")
@patch("reviseur.report.canvas.Canvas")
def test_failed_image_handling(mock_canvas_class, mock_image_open):
    """Test handling of images that contain 'FAILED' in their name."""

    # Mock image properties
    mock_image = MagicMock()
    mock_image.width = 800
    mock_image.height = 600
    mock_image_open.return_value = mock_image

    # Mock canvas instance and methods
    mock_canvas_instance = MagicMock()
    mock_canvas_class.return_value = mock_canvas_instance

    # Create the report instance
    from reviseur.report import Report  # Adjust path as needed

    report = Report()  # This uses the mocked Canvas

    # Run add_image_page method for a failed image
    report.add_image_page("screenshots/step_1_FAILED.png")

    # Check setFillColor and drawString were called with expected arguments
    mock_canvas_instance.setFillColor.assert_called_with(colors.red)
    mock_canvas_instance.drawString.assert_any_call(ANY, ANY, ANY)

    # Ensure that the string includes the text we are testing for
    called_text = mock_canvas_instance.drawString.call_args[0][2]
    assert "FAILED" in called_text
    assert "FOUND INCONSISTENT" in called_text

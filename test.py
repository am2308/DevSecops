import pytest
from unittest.mock import patch, MagicMock
from app import app, allowed_file, upload_file
from flask import Flask

@pytest.fixture
def app_instance():
    """Provide a Flask app instance for testing."""
    app.config['TESTING'] = True
    app.secret_key = 'test_secret_key'
    return app

def test_allowed_file():
    """Test allowed_file function with valid and invalid inputs."""
    assert allowed_file("image.png") is True
    assert allowed_file("image.jpg") is True
    assert allowed_file("image.jpeg") is True
    assert allowed_file("image.gif") is False
    assert allowed_file("image") is False

@patch('app.redirect')
@patch('app.flash')
def test_upload_no_file(mock_flash, mock_redirect, app_instance):
    """Test upload_file when no file is provided."""
    with app_instance.test_request_context(method='POST'):
        response = upload_file()
        mock_flash.assert_called_with('No file part in the request', 'danger')
        mock_redirect.assert_called_once()

@patch('app.redirect')
@patch('app.flash')
def test_upload_invalid_file_format(mock_flash, mock_redirect, app_instance):
    """Test upload_file with an invalid file format."""
    mock_file = MagicMock()
    mock_file.filename = "image.gif"
    with app_instance.test_request_context(method='POST', data={'file': mock_file}):
        response = upload_file()
        mock_flash.assert_called_with('Invalid file format. Only PNG, JPG, and JPEG are allowed.', 'danger')
        mock_redirect.assert_called_once()

@patch('app.Image.open')
@patch('app.flash')
@patch('app.redirect')
def test_upload_invalid_image(mock_redirect, mock_flash, mock_open, app_instance):
    """Test upload_file when the image file is corrupted."""
    mock_open.side_effect = Exception("UnidentifiedImageError")
    mock_file = MagicMock()
    mock_file.filename = "image.png"
    with app_instance.test_request_context(method='POST', data={'file': mock_file}):
        response = upload_file()
        mock_flash.assert_called_with('Invalid image file. Please upload a valid image.', 'danger')
        mock_redirect.assert_called_once()

@patch('app.remove')
@patch('app.Image.open')
@patch('app.BytesIO')
def test_upload_valid_image(mock_bytes_io, mock_open, mock_remove, app_instance):
    """Test upload_file when a valid image is uploaded."""
    mock_image = MagicMock()
    mock_open.return_value = mock_image
    mock_remove.return_value = mock_image

    mock_bytes_io_instance = MagicMock()
    mock_bytes_io.return_value = mock_bytes_io_instance

    mock_file = MagicMock()
    mock_file.filename = "image.png"
    with app_instance.test_request_context(method='POST', data={'file': mock_file}):
        response = upload_file()
        assert response.status_code == 200  # Check for a successful response

# Importing the required modules
import os
from unittest.mock import patch, MagicMock
from flask_wtf.csrf import generate_csrf


def test_home_page():
    from youtube_web_downloader.app.app import app
    client = app.test_client()
    response = client.get('/')
    assert response.status_code == 200
    assert b'<title>YouTube Downloader</title>' in response.data


@patch('youtube_web_downloader.app.app.FlaskForm.validate_on_submit', return_value=True)        #TODO: Dont mock this. Fix the poest call so it validates true
@patch('youtube_web_downloader.app.app.download_video')
@patch('youtube_web_downloader.app.app.download_audio')
def test_download_submit_buttons( mock_download_audio: MagicMock,mock_download_video: MagicMock, mock_validate_on_submit: MagicMock):
    from youtube_web_downloader.app.app import app
    app.testing = True
    client = app.test_client()
    
    # Act
    with app.test_request_context():
        response = client.post('/', data={'url': 'https://www.youtube.com/watch?v=eFyc1g_6ffs', 'video': 'Download Video', 'csrf_token': generate_csrf()}, content_type='multipart/form-data')

    # Assert
    mock_download_video.assert_called_once()  # Check that the mock function was called
    mock_download_audio.assert_not_called()


    #Reset mocks
    mock_download_audio.reset_mock()
    mock_download_video.reset_mock()

    #Act download audio
    with app.test_request_context():
        response = client.post('/', data={'url': 'https://www.youtube.com/watch?v=eFyc1g_6ffs', 'audio': 'Download Audio', 'csrf_token': generate_csrf()}, content_type='multipart/form-data')

    #Assert
    mock_download_audio.assert_called_once()
    mock_download_video.assert_not_called()
    

@patch('os.environ',{'DOWNLOAD_FOLDER_PATH': './test_downloads', 'SECRET_KEY': 'test_secret'})
@patch('youtube_web_downloader.app.app.YouTube')
def test_download_video(mock_youtube):
    from youtube_web_downloader.app.app import download_video
    
    url = 'https://www.youtube.com/watch?v=eFyc1g_6ffs'
    # Test case 1: DOWNLOAD_FOLDER_PATH environment variable is set
    # Act
    download_video(url)  # Call the download_video function with the given URL

    # Assert
    mock_youtube.assert_called_once_with(url)  # Check that the mock YouTube object was called with the URL
    mock_youtube.return_value.streams.get_highest_resolution().download.assert_called_once_with(output_path='./test_downloads/video')  # Check that the download function was called with the correct output path

    # Test case 2: DOWNLOAD_FOLDER_PATH environment variable is not set
    #Reset mocks
    mock_youtube.reset_mock()

    # Act
    with patch('os.environ', {'DOWNLOAD_FOLDER_PATH': ''}):
        response = download_video(url)
    
    # Assert
    assert response == 'DOWNLOAD_FOLDER_PATH environment variable is not set'

@patch('os.environ',{'DOWNLOAD_FOLDER_PATH': './test_downloads', 'SECRET_KEY': 'test_secret'})
@patch('youtube_web_downloader.app.app.AudioSegment')
@patch('youtube_web_downloader.app.app.YouTube')
def test_download_audio(mock_youtube: MagicMock, mock_audio_segment: MagicMock):
    from youtube_web_downloader.app.app import download_audio
    #Setup mocks
    mock_youtube.return_value.streams.filter.return_value.first.return_value.download.return_value = './test_downloads/audio/audio.mp4'



    url = 'https://www.youtube.com/watch?v=eFyc1g_6ffs'
    # Test case 1: DOWNLOAD_FOLDER_PATH environment variable is set
    # Act
    download_audio(url)

    # Assert
    mock_youtube.assert_called_once_with(url)
    mock_youtube.return_value.streams.filter(only_audio=True).first().download.assert_called_once_with(output_path='./test_downloads/audio')
    mock_audio_segment.from_file.assert_called_once_with('./test_downloads/audio/audio.mp4')
    mock_audio_segment.from_file.return_value.export.assert_called_once_with('./test_downloads/audio/audio.mp3', format='mp3')

    # Test case 2: DOWNLOAD_FOLDER_PATH environment variable is not set
    #Reset mocks
    mock_youtube.reset_mock()

    # Act
    with patch('os.environ', {'DOWNLOAD_FOLDER_PATH': ''}):
        response = download_audio(url)

    # Assert
    assert response == 'DOWNLOAD_FOLDER_PATH environment variable is not set'


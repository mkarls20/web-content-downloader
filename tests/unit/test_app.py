# Importing the required modules
import os
from unittest.mock import patch, MagicMock
from flask_wtf.csrf import generate_csrf
from flask import url_for


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
    youtube_url = 'https://www.youtube.com/watch?v=eFyc1g_6ffs'
    # Act
    with app.test_request_context():
        response = client.post('/', data={'url': youtube_url , 'video': 'Download Video', 'csrf_token': generate_csrf()}, content_type='multipart/form-data')

    # Assert
    mock_download_video.assert_called_once()  # Check that the mock function was called
    mock_download_audio.assert_not_called()


    #Reset mocks
    mock_download_audio.reset_mock()
    mock_download_video.reset_mock()

    #Act download audio
    with app.test_request_context():
        response = client.post('/', data={'url': youtube_url, 'audio': 'Download Audio', 'csrf_token': generate_csrf()}, content_type='multipart/form-data')

    # Assert
    assert response.status_code == 302
    assert response.location == f'/set_track_info?url={youtube_url.replace("=", "%3D")}'

    
    

@patch('os.environ',{'DOWNLOAD_FOLDER_PATH': './test_downloads', 'SECRET_KEY': 'test_secret'})
@patch('youtube_web_downloader.app.app.YouTube')
@patch('youtube_web_downloader.app.app.pickle')
@patch('youtube_web_downloader.app.app.open')
def test_download_video(mock_open,mock_pickle,mock_youtube):
    from youtube_web_downloader.app.app import download_youtube_video
    
    url = 'https://www.youtube.com/watch?v=eFyc1g_6ffs'
    # Test case 1: DOWNLOAD_FOLDER_PATH environment variable is set
    # Act
    download_youtube_video(url)  # Call the download_video function with the given URL

    # Assert
    mock_youtube.assert_called_once_with(url)  # Check that the mock YouTube object was called with the URL
    mock_youtube.return_value.streams.get_highest_resolution().download.assert_called_once_with(output_path='./test_downloads/video')  # Check that the download function was called with the correct output path
    mock_pickle.dump.assert_called_once()
    # Test case 2: DOWNLOAD_FOLDER_PATH environment variable is not set
    #Reset mocks
    mock_youtube.reset_mock()

    # Act
    with patch('os.environ', {'DOWNLOAD_FOLDER_PATH': ''}):
        response = download_youtube_video(url)
    
    # Assert
    assert response == 'DOWNLOAD_FOLDER_PATH environment variable is not set'

@patch('os.environ',{'DOWNLOAD_FOLDER_PATH': './test_downloads', 'SECRET_KEY': 'test_secret'})
@patch('youtube_web_downloader.app.app.open')
@patch('youtube_web_downloader.app.app.pickle')
@patch('youtube_web_downloader.app.app.AudioSegment')
@patch('youtube_web_downloader.app.app.YouTube')
def test_download_audio(mock_youtube: MagicMock, mock_audio_segment: MagicMock, mock_pickle: MagicMock,mock_open: MagicMock):
    from youtube_web_downloader.app.app import download_youtube_audio
    #Setup mocks
    mock_youtube.return_value.streams.filter.return_value.first.return_value.download.return_value = './test_downloads/audio/audio.mp4'



    url = 'https://www.youtube.com/watch?v=eFyc1g_6ffs'
    # Test case 1: DOWNLOAD_FOLDER_PATH environment variable is set
    # Act
    download_youtube_audio(url,"Test","Tchoupi","Unknown")

    # Assert
    mock_youtube.assert_called_once_with(url)
    mock_youtube.return_value.streams.filter(only_audio=True).first().download.assert_called_once_with(output_path='./test_downloads/audio')
    mock_audio_segment.from_file.assert_called_once_with('./test_downloads/audio/audio.mp4')
    mock_audio_segment.from_file.return_value.export.assert_called_once_with('./test_downloads/audio/audio.mp3', format='mp3', tags={'title': 'Test', 'artist': 'Tchoupi', 'album': 'Unknown'})
    mock_pickle.dump.assert_called_once()
    # Test case 2: DOWNLOAD_FOLDER_PATH environment variable is not set
    #Reset mocks
    mock_youtube.reset_mock()

    # Act
    with patch('os.environ', {'DOWNLOAD_FOLDER_PATH': ''}):
        response = download_youtube_audio(url,"Test","Tchoupi","Tchoupi")

    # Assert
    assert response == 'DOWNLOAD_FOLDER_PATH environment variable is not set'

@patch('youtube_web_downloader.app.app.download_audio')
@patch('youtube_web_downloader.app.app.YouTube')
def test_set_track_info_1(mock_youtube: MagicMock, mock_download_audio: MagicMock):
    from youtube_web_downloader.app.app import app
    
    app.testing = True
    
    client = app.test_client()
    youtube_url = 'https://www.youtube.com/watch?v=eFyc1g_6ffs'
    
    mock_youtube.return_value.title = 'Tchoupi - Test'
    mock_youtube.return_value.author = 'Hej'


    # Test case 1: GET request
    with app.test_request_context():
        response = client.get(f'/set_track_info?url={youtube_url}')
        print(client._cookies)

    
    assert response.status_code == 200
    assert b'<title>Set Track Info</title>' in response.data
    assert b'<form method="POST">' in response.data
    
    assert b'<input id="track_name" name="track_name" required size="20" type="text" value="Test">' in response.data
    assert b'<input id="artist_name" name="artist_name" required size="20" type="text" value="Tchoupi">' in response.data
    mock_download_audio.assert_not_called()
@patch('youtube_web_downloader.app.app.download_audio')
@patch('youtube_web_downloader.app.app.YouTube')
def test_set_track_info_2(mock_youtube: MagicMock, mock_download_audio: MagicMock):
    from youtube_web_downloader.app.app import app
    
    app.testing = True
    app.config['WTF_CSRF_ENABLED'] = False      #TODO: Fix this, looks like only testing-problem
    client = app.test_client()
    print(client._cookies)
    youtube_url = 'https://www.youtube.com/watch?v=eFyc1g_6ffs'
    
    mock_youtube.return_value.title = 'Tchoupi - Test'
    mock_youtube.return_value.author = 'Hej'

    # Test case 2: POST request
    mock_download_audio.reset_mock()
    with app.test_request_context():
        data={'track_name': 'Test', 'artist_name': 'Tchoupi', 'csrf_token': generate_csrf(),"url":youtube_url}

        #response = client.get(f'/set_track_info?url={youtube_url}')
        response = client.post(f'/set_track_info', data=data, content_type='multipart/form-data')
        print(client._cookies)
        #response = client.post('/set_track_info', data={'url': youtube_url, 'audio': 'Download Audio', 'csrf_token': generate_csrf()}, content_type='multipart/form-data')


    assert response.status_code == 200
    mock_download_audio.assert_called_once_with(youtube_url, 'Test', 'Tchoupi','Tchoupi')
    



def test_trackform():
    from youtube_web_downloader.app.app import TrackForm
    from youtube_web_downloader.app.app import app
    app.testing = True
    client = app.test_client()
    

    #Test case 1: Track name contains the word 'Tchoupi'
    with app.test_request_context():
        form = TrackForm()
        form.add_title(track_name='Tchoupi - Test', channel='Tchoupi')

    assert form.artist_name.default == 'Tchoupi'
    assert form.track_name.default == 'Test'



    #Test case 2: Track name does not contain the word 'Tchoupi'
    with app.test_request_context():
        form = TrackForm()
        form.add_title(track_name='Test', channel='Tchoupi')

    assert form.artist_name.default == 'Tchoupi'
    assert form.track_name.default == 'Test'

    #Test case 3: Track names contains word 'TchOupi'
    with app.test_request_context():
        form = TrackForm()
        form.add_title(track_name='TchOupi - Test', channel='Tchoupi')
    
    assert form.artist_name.default == 'Tchoupi'
    assert form.track_name.default == 'Test'

    #Test case 4: Track name is empty
    with app.test_request_context():
        form = TrackForm()
        form.add_title(track_name='', channel='Something Unknown')

    assert form.artist_name.default == 'Something Unknown'
    assert form.track_name.default == 'Unknown'

    #Test case 5: Channel is empty
    with app.test_request_context():
        form = TrackForm()
        form.add_title(track_name='Test', channel='')
        
    assert form.artist_name.default == 'Unknown'
    assert form.track_name.default == 'Test'

    #Test case 6: Both track name and channel are empty
    with app.test_request_context():
        form = TrackForm()
        form.add_title(track_name='', channel='')

    assert form.artist_name.default == 'Unknown'
    assert form.track_name.default == 'Unknown'

    #Test case 7: ' in T'choupi
    with app.test_request_context():
        form = TrackForm()
        form.add_title(track_name="T'choupi - Test", channel='Tchoupi')

    assert form.artist_name.default == 'Tchoupi'
    assert form.track_name.default == 'Test'
    import pytest

@patch('youtube_web_downloader.app.app.render_template')
@patch('youtube_web_downloader.app.app.load_prev_downloads')
def test_previous_downloads(mock_load_prev_downloads: MagicMock, render_template: MagicMock):
    from youtube_web_downloader.app.app import app
    app.testing = True
    client = app.test_client()

    # Set the return value of the mock function
    mock_load_prev_downloads.return_value = ['download1', 'download2', 'download3']
    
    # Call the previous_downloads function
    with app.test_request_context():
        client.get('/previous_downloads')
    
    # Assert that the render_template function was called with the correct arguments
    render_template.assert_called_once_with('previous_downloads.html', prev_downloads=['download1', 'download2', 'download3'])
    
#from youtube_web_downloader.app.app import delete, load_prev_downloads


@patch('youtube_web_downloader.app.app.open',MagicMock())
@patch('youtube_web_downloader.app.app.load_prev_downloads')
@patch('youtube_web_downloader.app.app.pickle.dump')
@patch('youtube_web_downloader.app.app.os.remove')
@patch('youtube_web_downloader.app.app.redirect')
def test_delete(mock_redirect: MagicMock ,mock_remove: MagicMock, mock_dump: MagicMock, mock_load_prev_downloads: MagicMock):
    from youtube_web_downloader.app.app import app

    app.testing = True
    client = app.test_client()




    # Arrange
    file_path = 'path/to/file'
    url = 'https://www.youtube.com/watch?v=eFyc1g_6ffs'
    prev_downloads = {url: 'downloaded_file.mp4'}
    mock_load_prev_downloads.return_value = prev_downloads
    download_folder_path= '/path/to/downloads/'
    

    # Test 1: DOWNLOAD_FOLDER_PATH environment variable is set
    # Act
    with app.test_request_context() ,patch.dict(os.environ, {'DOWNLOAD_FOLDER_PATH': download_folder_path}):
        response = client.get(f'/delete?url={url}&file_path={file_path}')
        redirect_url = url_for('previous_downloads')
        

    # Assert
    mock_load_prev_downloads.assert_called_once()
    mock_remove.assert_called_once_with(download_folder_path+file_path)
    mock_dump.assert_called_once()
    
    mock_redirect.assert_called_once_with(redirect_url)
    
    


    # Test 2: DOWNLOAD_FOLDER_PATH environment variable is not set
    # Act
    with app.test_request_context(), patch.dict(os.environ, {'DOWNLOAD_FOLDER_PATH': ''}):
        response = client.get(f'/delete?url={url}&file_path={file_path}')

    assert response.text == 'DOWNLOAD_FOLDER_PATH environment variable is not set'
    

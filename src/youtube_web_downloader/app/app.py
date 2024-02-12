from flask import Flask, render_template, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from pytube import YouTube
import os
from pydub import AudioSegment

app = Flask(__name__)


#from dotenv import load_dotenv


#load_dotenv(".env.dev")
if "DOWNLOAD_FOLDER_PATH" not in os.environ:
    os.environ['DOWNLOAD_FOLDER_PATH'] = './downloads'
if "SECRET_KEY" not in os.environ:
    os.environ['SECRET_KEY'] = "secret"
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

class DownloadForm(FlaskForm):
    url = StringField('YouTube URL')
    video = SubmitField('Download Video')
    audio = SubmitField('Download Audio')


@app.route('/', methods=['GET', 'POST'])
def home():
    form = DownloadForm()
    if form.validate_on_submit():
        if form.video.data:
            print("hej")
            return download_video(form.url.data)
        elif form.audio.data:
            return download_audio(form.url.data)
    return render_template('home.html', form=form)
    

def download_audio(url):
    folder_path = os.getenv('DOWNLOAD_FOLDER_PATH') + "/audio"
    if folder_path == "/audio":
        return 'DOWNLOAD_FOLDER_PATH environment variable is not set'
    
    yt = YouTube(url)
    audio = yt.streams.filter(only_audio=True).first()
    audio_path = audio.download(output_path=folder_path)
    
    # Convert audio to MP3 format
    audio_file = AudioSegment.from_file(audio_path)
    mp3_path = os.path.splitext(audio_path)[0] + '.mp3'
    audio_file.export(mp3_path, format='mp3')
    
    return 'Audio downloaded and encoded as MP3'

def download_video(url):
    folder_path = os.getenv('DOWNLOAD_FOLDER_PATH') + "/video"
    if folder_path == "/video":
        return 'DOWNLOAD_FOLDER_PATH environment variable is not set'
    
    yt = YouTube(url)
    video = yt.streams.get_highest_resolution()
    video.download(output_path=folder_path)
    return 'Video downloaded'

if __name__ == '__main__':
    app.run(debug=True)
    #download_audio('https://www.youtube.com/watch?v=eFyc1g_6ffs')

    
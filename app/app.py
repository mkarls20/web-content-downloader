from flask import Flask, render_template, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from pytube import YouTube
import os

app = Flask(__name__)


#from dotenv import load_dotenv


#load_dotenv(".env.dev")

os.environ['DOWNLOAD_FOLDER_PATH'] = './downloads'
#app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SECRET_KEY'] = "secret"
class DownloadForm(FlaskForm):
    url = StringField('YouTube URL')
    video = SubmitField('Download Video')
    audio = SubmitField('Download Audio')

@app.route('/', methods=['GET', 'POST'])
def home():
    form = DownloadForm()
    if form.validate_on_submit():
        if form.video.data:
            return download_video(form.url.data)
        elif form.audio.data:
            return download_audio(form.url.data)
    return render_template('home.html', form=form)

def download_audio(url):
    folder_path = os.getenv('DOWNLOAD_FOLDER_PATH')
    if not folder_path:
        return 'DOWNLOAD_FOLDER_PATH environment variable is not set'
    
    yt = YouTube(url)
    audio = yt.streams.filter(only_audio=True).first()
    audio.download(output_path=folder_path)
    return 'Audio downloaded'

def download_video(url):
    folder_path = os.getenv('DOWNLOAD_FOLDER_PATH')
    if not folder_path:
        return 'DOWNLOAD_FOLDER_PATH environment variable is not set'
    
    yt = YouTube(url)
    video = yt.streams.get_highest_resolution()
    video.download(output_path=folder_path)
    return 'Video downloaded'

if __name__ == '__main__':
    #app.run(debug=True)
    download_audio('https://www.youtube.com/watch?v=eFyc1g_6ffs')

    
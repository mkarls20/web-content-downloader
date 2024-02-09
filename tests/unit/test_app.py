from flask import Flask, render_template, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
import youtube_dl

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'

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

def download_video(url):
    ydl_opts = {}
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    return 'Video downloaded'

def download_audio(url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    return 'Audio downloaded'

if __name__ == '__main__':
    app.run(debug=True)
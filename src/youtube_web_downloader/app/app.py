import pickle
from flask import Flask, redirect, render_template, request, url_for
from flask_wtf import FlaskForm
from wtforms import HiddenField, StringField, SubmitField
from pytube import YouTube
import os
from pydub import AudioSegment
from wtforms.validators import DataRequired
import re
from dotenv import load_dotenv

app = Flask(__name__)


from dotenv import load_dotenv


load_dotenv(".env.dev")
if "DOWNLOAD_FOLDER_PATH" not in os.environ:
    os.environ["DOWNLOAD_FOLDER_PATH"] = "./downloads"
if "SECRET_KEY" not in os.environ:
    os.environ["SECRET_KEY"] = "secret"
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")


class DownloadForm(FlaskForm):
    url = StringField("YouTube URL")
    video = SubmitField("Download Video")
    audio = SubmitField("Download Audio")


class TrackForm(FlaskForm):
    url = HiddenField("YouTube URL", validators=[DataRequired()])
    track_name = StringField("Track Name", validators=[DataRequired()])
    artist_name = StringField("Artist Name", validators=[DataRequired()])
    album_name = StringField("Album Name")
    submit = SubmitField("Submit")

    def set_url(self, url):
        self.url.data = url

    def add_title(self, track_name, channel):
        """
        Adds a title to the application.

        Args:
            track_name (str): The name of the track.
            channel (str): The name of the channel.

        Returns:
            None
        """
        print(track_name)
        regexp = r"(?i)t.?choupi"
        print(re.search(regexp, track_name))
        if re.search(regexp, track_name):
            # If the track name matches the pattern "t[ch]oupi" (case-insensitive)
            self.artist_name.default = "Tchoupi"
            track_name = re.split(regexp, track_name, 1)[-1].strip()
            self.track_name.default = re.sub(r"^[^\w]+", "", track_name)
            # Capitalize the first letter of the track name
            self.track_name.default = (
                self.track_name.default[0].upper() + self.track_name.default[1:]
            )
        else:
            # If the track name does not match the pattern
            self.artist_name.default = channel
            self.track_name.default = track_name

        # Set default values for artist name and track name if they are empty
        if not self.artist_name.default:
            self.artist_name.default = "Unknown"
        if not self.track_name.default:
            self.track_name.default = "Unknown"

        # Set the data attribute instead of calling process()
        self.artist_name.data = self.artist_name.default
        self.track_name.data = self.track_name.default

    def set_album_name(self):
        print("Running set_album_name")
        print(self.artist_name.data)
        if self.artist_name.data:
            self.album_name.data = self.artist_name.data

        self.album_name.default = "Unknown"


@app.route("/", methods=["GET", "POST"])
def home():
    form = DownloadForm()
    if form.validate_on_submit():
        if form.video.data:
            print("hej")
            return download_youtube_video(form.url.data)
        elif form.audio.data:
            return redirect(url_for("set_track_info", url=form.url.data))
    return render_template("home.html", form=form)


@app.route("/previous_downloads", methods=["GET"])
def previous_downloads():
    prev_downloads = load_prev_downloads()
    return render_template("previous_downloads.html", prev_downloads=prev_downloads)


@app.route("/delete", methods=["GET"])
def delete():
    downloads_folder = os.getenv("DOWNLOAD_FOLDER_PATH")
    if not downloads_folder:
        return "DOWNLOAD_FOLDER_PATH environment variable is not set"
    file_path = downloads_folder + request.args.get("file_path")
    url = request.args.get("url")
    prev_downloads = load_prev_downloads()
    if url in prev_downloads:
        del prev_downloads[url]
        pickle.dump(
            prev_downloads,
            open(os.getenv("DOWNLOAD_FOLDER_PATH") + "downloads.pkl", "wb"),
        )
    try:
        os.remove(file_path)
    except FileNotFoundError:
        print(f"File {file_path} not found")
        pass

    return redirect(url_for("previous_downloads"))


    
@app.route('/previous_downloads', methods=['GET'])
def previous_downloads():
    prev_downloads = load_prev_downloads()
    return render_template('previous_downloads.html', prev_downloads=prev_downloads)

@app.route('/re_download', methods=['GET'])
def re_download():
    url = request.args.get('url')
    # Add your re-download logic here using the 'url' parameter
    return 'Re-download successful'

@app.route('/delete', methods=['GET'])
def delete():
    downloads_folder = os.getenv('DOWNLOAD_FOLDER_PATH')
    if not downloads_folder:
        return 'DOWNLOAD_FOLDER_PATH environment variable is not set'
    file_path = downloads_folder + request.args.get('file_path')
    url = request.args.get('url')
    prev_downloads = load_prev_downloads()
    if url in prev_downloads:
        del prev_downloads[url]
        pickle.dump(prev_downloads, open(os.getenv('DOWNLOAD_FOLDER_PATH') + 'downloads.pkl', 'wb'))
    try:
        os.remove(file_path)
    except FileNotFoundError:
        print(f'File {file_path} not found')
        pass

    return redirect(url_for('previous_downloads'))

def download_youtube_youtube_audio(url, track_name, artist_name, album_name):
    folder_path = os.getenv("DOWNLOAD_FOLDER_PATH") + "/audio"
    if folder_path == "/audio":
        return "DOWNLOAD_FOLDER_PATH environment variable is not set"

    yt = YouTube(url)
    audio = yt.streams.filter(only_audio=True).first()
    audio_path = audio.download(output_path=folder_path)

    # Convert audio to MP3 format
    audio_file = AudioSegment.from_file(audio_path)
    mp3_path = os.path.splitext(audio_path)[0] + ".mp3"

    # Set title, artist, and art metadata
    audio_file.export(
        mp3_path,
        format="mp3",
        tags={"title": track_name, "artist": artist_name, "album": album_name},
    )
    add_to_prev_downloads(url, mp3_path, yt.author, yt.title, yt.video_id, "audio")

    return f"Audio downloaded and encoded as MP3. Track Name: {track_name}, Artist Name: {artist_name}"


@app.route("/set_track_info", methods=["GET", "POST"])
def set_track_info():
    form = TrackForm()
    if request.method == "GET":
        url = request.args.get("url")
    elif request.method == "POST":
        url = request.form["url"]

    yt = YouTube(url)

    form.add_title(yt.title, yt.author)
    form.set_album_name()
    form.set_url(url)

    if form.validate_on_submit():
        return download_youtube_audio(
            url, form.track_name.data, form.artist_name.data, form.album_name.data
        )
    return render_template("set_track_info.html", form=form)


def load_prev_downloads():
    """
    Loads previous downloads from a pickle file.
    """
    folder_path = os.getenv("DOWNLOAD_FOLDER_PATH")
    try:
        with open(folder_path + "downloads.pkl", "rb") as f:
            prev_downloads = pickle.load(f)
    except FileNotFoundError:
        prev_downloads = {}
    return prev_downloads


def add_to_prev_downloads(url, file_path, artist, album, title, type):
    """
    Adds a download to the previous downloads pickle file."""
    folder_path = os.getenv("DOWNLOAD_FOLDER_PATH")
    prev_downloads = load_prev_downloads()
    prev_downloads[url] = {
        "file_path": file_path,
        "artist": artist,
        "album": album,
        "title": title,
        "type": type,
    }
    pickle.dump(prev_downloads, open(folder_path + "downloads.pkl", "wb"))


def download_youtube_video(url):
    """
    Downloads a YouTube video."""
    folder_path = os.getenv("DOWNLOAD_FOLDER_PATH") + "/video"
    if folder_path == "/video":
        return "DOWNLOAD_FOLDER_PATH environment variable is not set"

    yt = YouTube(url)
    video = yt.streams.get_highest_resolution()
    video.download(output_path=folder_path)
    add_to_prev_downloads(
        url,
        folder_path + "/" + yt.video_id + ".mp4",
        yt.author,
        yt.title,
        yt.video_id,
        "video",
    )
    return "Video downloaded"


if __name__ == "__main__":
    app.run(debug=True)
    # download_audio('https://www.youtube.com/watch?v=eFyc1g_6ffs')

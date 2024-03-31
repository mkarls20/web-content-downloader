import os
import pickle


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

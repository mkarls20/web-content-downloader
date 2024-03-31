from flask import render_template, redirect, url_for, request, Blueprint
import pickle
import os


from ._utils import load_prev_downloads

previous_bp = Blueprint("previous_bp", __name__)


@previous_bp.route("/previous_downloads", methods=["GET"])
def previous_downloads():
    prev_downloads = load_prev_downloads()
    return render_template("previous_downloads.html", prev_downloads=prev_downloads)


@previous_bp.route("/delete", methods=["GET"])
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

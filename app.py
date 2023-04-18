# Lucas Bubner, 2023
from flask import Flask, render_template, request, redirect, flash, send_file
from pytube import YouTube, Playlist
from os import environ, remove
from waitress import serve
from io import BytesIO
from moviepy.editor import VideoFileClip

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Parse link into pytube object
        try:
            link = request.form["link"]
            try:
                yt = YouTube(link, on_complete_callback=lambda _,path: convert(path))
            except:
                try:
                    yt = Playlist(link)
                    if yt is not None:
                        raise Exception("Playlists are currently not supported.")
                except:
                    raise Exception("Invalid link.")

            # Download video file
            try:
                yt = yt.streams.get_lowest_resolution()
                yt.download(output_path="./.temp")
            except:
                raise Exception("Failed to download video.")

            # Write file into memory
            data = BytesIO()
            with open(f"./.temp/{yt.title}.mp3", "rb") as f:
                data.write(f.read())
            data.seek(0)
            # Remove file as it is no longer needed and is in memory
            remove(f"./.temp/{yt.title}.mp3")

            # Send file to user
            return send_file(data, as_attachment=True, mimetype="audio/mp3", download_name=f"{yt.title}.mp3")
        except Exception as e:
            flash(str(e))
            return redirect("/")
    else:
        return render_template("index.html")


def convert(path):
    # Convert all downloaded mp4 files to mp3
    with VideoFileClip(path) as video:
        video.audio.write_audiofile(path[:-4] + ".mp3")
    # Delete mp4 file
    remove(path)


if __name__ == "__main__":
    app.secret_key = environ["SECRET_KEY"]
    app.config["SESSION_TYPE"] = "filesystem"
    serve(app, host="0.0.0.0")

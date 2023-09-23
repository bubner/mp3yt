# Lucas Bubner, 2023
from flask import Flask, render_template, request
from enum import Enum
from io import BytesIO
import subprocess
import os
import uuid

app = Flask(__name__)

class Format(Enum):
    MP4 = 1
    MP3 = 2

class Downloader:
    def __init__(self, url):
        self.url = url
    
    def get_title(self):
        command = ["./yt-dlp", "--get-title", self.url]
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        if process.returncode != 0:
            return {"res": None, "stderr": stderr.decode("utf-8")}
        
        return {"res": stdout.decode("utf-8"), "stderr": stderr.decode("utf-8")}

    def download(self, dtype: Format):
        gen = str(uuid.uuid4())
        out = os.path.join("/tmp", gen, "%(title)s.%(ext)s")

        formats = ["-x", "--audio-format", "mp3"] if dtype == Format.MP3 else ["-S", "res,ext:mp4:m4a", "--recode", "mp4"]

        command = [
            "./yt-dlp",
            *formats,
            "--break-on-reject",
            "--match-filter",
            "!is_live",
            "-I",
            "0",
            "-o",
            out,
            self.url,
        ]

        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        _, stderr = process.communicate()

        if process.returncode != 0:
            if stderr.decode("utf-8") == "":
                return {"res": None, "stderr": "Unsupported URL. mp3yt does not support downloading currently running livestreams, bulk playlists, or age-restricted videos."}
            return {"res": None, "stderr": stderr.decode("utf-8")}
        
        with open(os.path.join("/tmp", gen, os.listdir(os.path.join("/tmp", gen))[0]), "rb") as f:
            byte_stream = BytesIO(f.read())

        return byte_stream
    

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/title")
def title():
    url = request.args.get("url")
    if not url:
        return {"error": "No URL provided."}, 400
    
    downloader = Downloader(url)

    response = downloader.get_title()
    return response, 200


@app.route("/d", methods=["GET", "POST"])
def download():
    url = request.args.get("url")
    dtype = request.args.get("type")
    if not url and not dtype:
        data = request.json
        url = data.get("url")
        dtype = data.get("type")

    if not url:
        return {"error": "No URL provided."}, 400
    
    if not dtype:
        return {"error": "No type provided."}, 400
    
    if dtype not in ["mp3", "mp4"]:
        return {"error": "Invalid type."}, 400

    downloader = Downloader(url)

    response = downloader.download(Format.MP3 if dtype == "mp3" else Format.MP4)
    return response, 200

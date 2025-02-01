import os
import random
import base64
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager

from mutagen.id3 import ID3


audio_files = []

@asynccontextmanager
async def lifespan(app: FastAPI):
    audio_dir = "static/music"
    audio_files.extend([f for f in os.listdir(audio_dir)])
    yield

app = FastAPI(lifespan=lifespan)

app.mount("/static", StaticFiles(directory="static"), name="static")


templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={})


@app.get("/music", response_class=HTMLResponse)
async def play_music(request: Request):
    file = random.choice(audio_files) if audio_files else []
    if file:
        details = ID3(f"{os.getcwd()}/static/music/{file}")
        title = details.get("TIT2",None)
        artist = details.get("TPE1",None)
        album = details.get("TALB",None)
        album_arts = details.getall("APIC")

        if album_arts:
            album_art = album_arts[0].data
            mime_type = album_arts[0].mime
            base64_image = base64.b64encode(album_art).decode('utf-8')
            album_art = f"data:{mime_type};base64,{base64_image}"
        else:
            album_art = "/static/music.png"
        title = title.text[0] if title else 'Unknown'
        artist = artist.text[0] if title else 'Unknown'
        album = album.text[0] if title else 'Unknown'

    return templates.TemplateResponse(
        request=request,
        name="music.html",
        context={
            "file": f"/static/music/{file}",
            "title": title,
            "artist": artist,
            "album": album,
            "album_art": album_art
        },
    )

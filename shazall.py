import asyncio
import time
import sounddevice as sd
import soundfile as sf
from pydub import AudioSegment
from shazamio import Shazam
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import json
import pylast
import os

# Load settings file
settings_file = os.path.join(os.path.dirname(__file__), "shazall-settings.json")

# Get settings
try:
    with open(settings_file) as f:
        full_json = json.load(f)
        screen = full_json["screen"]
        lastfm = full_json["lastfm"]

    DEFAULT_DURATION = full_json.get("duration", 10)
    DURATION = DEFAULT_DURATION
    SAMPLERATE = full_json.get("samplerate", 44100)
    WIDTH = screen.get("width", 480)
    HEIGHT = screen.get("height", 320)
    SCROBBLE = lastfm.get("scrobble", False)

    if SCROBBLE:
        API_KEY = lastfm["api_key"]
        API_SECRET = lastfm["api_secret"]
        SESSION_KEY = lastfm["session_key"]
        USERNAME = lastfm["username"]
        lastfm_network = pylast.LastFMNetwork(
            api_key=API_KEY,
            api_secret=API_SECRET,
            session_key=SESSION_KEY
        )
    else:
        lastfm_network = None
except Exception as e:
    lastfm_network = None

FILENAME = "recording.wav"
last_title = ""
last_artist = ""

# LCD dimensions and fonts
font_main = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
font_status = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)

# Text size helper for Pillow >= 10
def get_text_size(draw, text, font):
    bbox = draw.textbbox((0, 0), text, font=font)
    width = bbox[2] - bbox[0]
    height = bbox[3] - bbox[1]
    return width, height

# Helper functions for LCD display
def wrap_text(draw, text, font, max_width):
    lines = []
    words = text.split()
    line = ""
    for word in words:
        test_line = line + word + " "
        w, _ = get_text_size(draw, test_line, font)
        if w <= max_width:
            line = test_line
        else:
            lines.append(line.strip())
            line = word + " "
    lines.append(line.strip())
    return lines

def draw_centered_lines(draw, lines, font, top_y, spacing=10, fill="white"):
    y = top_y
    for line in lines:
        w, h = get_text_size(draw, line, font)
        x = (WIDTH - w) // 2
        draw.text((x, y), line, font=font, fill=fill)
        y += h + spacing

def rgb888_to_rgb565(img):
    arr = np.array(img)
    r = (arr[:, :, 0] >> 3).astype(np.uint16)
    g = (arr[:, :, 1] >> 2).astype(np.uint16)
    b = (arr[:, :, 2] >> 3).astype(np.uint16)
    rgb565 = (r << 11) | (g << 5) | b
    return rgb565

def draw_to_lcd(title, artist="", status="", spacing=10):
    img = Image.new("RGB", (WIDTH, HEIGHT), "black")
    draw = ImageDraw.Draw(img)

    title_lines = wrap_text(draw, title or "", font_main, WIDTH - 40)
    artist_lines = wrap_text(draw, f"by {artist}" if artist else "", font_main, WIDTH - 40)
    status_line = [status] if status else []

    title_height = sum([get_text_size(draw, l, font_main)[1] + spacing for l in title_lines])
    artist_height = sum([get_text_size(draw, l, font_main)[1] + spacing for l in artist_lines])
    status_height = get_text_size(draw, status, font_status)[1] if status else 0

    total_height = title_height + artist_height + status_height + 20
    top_y = (HEIGHT - total_height) // 2

    draw_centered_lines(draw, title_lines, font_main, top_y)
    draw_centered_lines(draw, artist_lines, font_main, top_y + title_height)
    if status:
        draw_centered_lines(draw, status_line, font_status, top_y + title_height + artist_height + 10)

    rgb565 = rgb888_to_rgb565(img)
    with open("/dev/fb1", "wb") as f:
        f.write(rgb565.tobytes())

# Last.fm scrobbling
def scrobble_track(artist, title):
    if not SCROBBLE or not lastfm_network:
        return
    try:
        timestamp = int(time.time())
        lastfm_network.update_now_playing(artist=artist, title=title)
        lastfm_network.scrobble(artist=artist, title=title, timestamp=timestamp)
    except Exception as e:
        pass

# Audio and Shazam logic
def record_audio():
    draw_to_lcd(last_title, last_artist, "Listening")
    audio = sd.rec(int(DURATION * SAMPLERATE), samplerate=SAMPLERATE, channels=1)
    sd.wait()
    sf.write(FILENAME, audio, SAMPLERATE)

async def identify_song():
    global last_title, last_artist, DURATION

    draw_to_lcd(last_title, last_artist, "Identifying")

    shazam = Shazam()
    audio = AudioSegment.from_wav(FILENAME)
    audio = audio.set_channels(2).set_frame_rate(44100)
    stereo_filename = "stereo_recording.wav"
    audio.export(stereo_filename, format="wav")

    out = await shazam.recognize(stereo_filename)
    track = out.get("track")

    if track:
        title = track.get("title", "")
        artist = track.get("subtitle", "")
        if title != last_title or artist != last_artist:
            DURATION = DEFAULT_DURATION
            last_title = title
            last_artist = artist
            draw_to_lcd(title, artist, "Playing")
            scrobble_track(artist, title)
        else:
            draw_to_lcd(title, artist, "Still playing")
    else:
        DURATION = min(DURATION + 10, 30)
        draw_to_lcd(last_title, last_artist, "Match failed")
        time.sleep(1)

# Main loop
def main_loop():
    while True:
        try:
            record_audio()
            asyncio.run(identify_song())
        except Exception as e:
            draw_to_lcd("Error", "", str(e))
            time.sleep(1)

if __name__ == "__main__":
    main_loop()

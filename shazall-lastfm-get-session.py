import pylast
import getpass
import json
import os

settings_file = os.path.join(os.path.dirname(__file__), "shazall-settings.json")

# Load settings
with open(settings_file) as f:
    full_json = json.load(f)
    lastfm = full_json["lastfm"]

API_KEY = lastfm["api_key"]
API_SECRET = lastfm["api_secret"]

# Use session_key if it already exists
if "session_key" in lastfm and lastfm["session_key"]:
    print("Session key already present in settings.")
    print("Session Key:", lastfm["session_key"])
else:
    username = input("Last.fm username: ").strip()
    password = getpass.getpass("Last.fm password (won't echo): ").strip()

    network = pylast.LastFMNetwork(
        api_key=API_KEY,
        api_secret=API_SECRET,
        username=username,
        password_hash=pylast.md5(password),
    )

    session_key = network.session_key
    print("Retrieved Session Key:", session_key)

    # Save session_key back to JSON file
    full_json["lastfm"]["session_key"] = session_key

    with open(settings_file, "w") as f:
        json.dump(full_json, f, indent=4)
    print(f"Session key saved to {settings_file}")

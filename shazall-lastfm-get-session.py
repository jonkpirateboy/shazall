import pylast
import getpass

API_KEY = ""
API_SECRET = ""

username = input("Last.fm username: ").strip()
password = getpass.getpass("Last.fm password (won't echo): ").strip()

network = pylast.LastFMNetwork(
    api_key=API_KEY,
    api_secret=API_SECRET,
    username=username,
    password_hash=pylast.md5(password),
)

print("Session Key:")
print(network.session_key)

import json
from json import JSONDecodeError

from data_wrapper import Artist, TrackData


def send_track_info(json_str: str, callback: ()):
	try:
		data = json.loads(json_str)
	except JSONDecodeError:
		print("JSON was malformatted")
		print(json_str)
		return
	title = data["name"]
	artists: [Artist] = []
	for artist in data["artists"]:
		artists.append(Artist(artist["name"], artist["uri"]))
	image_url = data["album"]["images"][0]["url"]
	t = TrackData()
	t.name = title
	t.artists = artists
	t.image_url = image_url
	t.get_image()  # Download image now
	callback(t)

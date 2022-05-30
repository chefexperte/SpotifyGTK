import enum
import json
from json import JSONDecodeError

import requests as requests

import static_strings
from tools.data_wrapper import ArtistData, TrackData


def send_track_info(json_str: str, callback: ()):
	try:
		data = json.loads(json_str)
	except JSONDecodeError:
		print("JSON was malformatted")
		print(json_str)
		return
	title = data["name"]
	artists: [ArtistData] = []
	for artist in data["artists"]:
		artists.append(ArtistData(artist["name"], uri_to_id(artist["uri"])))
	image_url = data["album"]["images"][0]["url"]
	t = TrackData(title, artists)
	t.image_url = image_url
	t.get_image()  # Download image now
	callback(t)


def get_artist_info(artist_id: str):
	token = static_strings.get_token()
	headers = {'Authorization': f'Bearer {token}'}
	r = requests.get(url=static_strings.api_endpoint + "/artists/" + artist_id, headers=headers)
	try:
		data = r.json()
	except JSONDecodeError:
		print("JSON was malformatted when getting artist info")
		return None
	# print(data)
	if "error" in data:
		print("There has been an error: ")
		print(data["error"])
		return None
	name = data["name"]
	followers = data["followers"]["total"]
	genres = data["genres"]
	image_url = data["images"][0]["url"]
	popularity = data["popularity"]
	artist = ArtistData(name, artist_id, genres)
	artist.followers = followers
	artist.image_url = image_url
	artist.popularity = popularity
	return artist


class UriType(enum.Enum):
	artist = "artist"
	track = "track"
	album = "album"


def id_to_uri(data_id: str, uri_type: UriType):
	return f"spotify:{uri_type.value}:{data_id}"


def uri_to_id(uri: str):
	return uri.split(":")[-1]

import os.path
import re
import urllib.request
from os.path import exists

from tools import data_tools
from tools import image_tools
import static_strings as ss


class DataWithImage:
	image_url: str = None

	def get_image(self):
		if self.image_url is None:
			return None
		if not exists(ss.image_cache):
			os.mkdir(ss.image_cache)
		image_id = re.findall("(?<=image/).*", self.image_url)[0]
		file_path = ss.image_cache + image_id
		if not exists(file_path):
			# Download image
			urllib.request.urlretrieve(self.image_url, file_path)
			if image_tools.round_and_save(file_path):
				print("Downloaded and prepared image")
			else:
				file_path = ss.image_cache + ".no_album"
				print("Error while preparing image")
		if not exists(file_path):
			return None
		return file_path


class ArtistData(DataWithImage):
	name: str = None
	uri: str = None
	followers: int = 0
	genres: [str] = None
	popularity: int = 0

	def __init__(self, name: str, data_id: str, genres: [str] = None):
		self.name = name
		self.data_id = data_id
		self.uri = data_tools.id_to_uri(data_id, data_tools.UriType.artist)
		if genres is None:
			self.genres = []
		else:
			self.genres = genres


class TrackData(DataWithImage):
	name: str = None
	artists: [ArtistData] = None

	def __init__(self, name: str = None, artists: [ArtistData] = None):
		self.name = name
		if artists is None:
			self.artists = []
		else:
			self.artists = artists


class PlaybackInfo:
	title: str = None
	position: int = None
	duration: int = None
	volume: int = None
	playing: bool = None
	can_modify_volume: bool = None
	player_available: bool = None

	def __init__(self, title, position, duration):
		self.title = title
		self.position = position
		self.duration = duration

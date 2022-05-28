import os.path
import re
import urllib.request
from os.path import exists

import static_strings as ss


class Artist:
	name: str = None
	uri: str = None

	def __init__(self, name: str, uri: str):
		self.name = name
		self.uri = uri


class TrackData:
	name: str = None
	artists: [Artist] = None
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
			print("Downloaded image")
		if not exists(file_path):
			return None
		return file_path

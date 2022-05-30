import os

path = os.path.dirname(os.path.abspath(__file__))
image_cache = f"{path}/image_cache/"
api_endpoint = "https://api.spotify.com/v1"


def get_token():
	try:
		with open(path + "/server/token.txt", "r") as file:
			return file.readlines()[0][:-1]
	except FileNotFoundError or PermissionError:
		print("Error reading token file.")
	return None

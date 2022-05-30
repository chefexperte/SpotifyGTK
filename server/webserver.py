import cgi
import os
from http.server import CGIHTTPRequestHandler, HTTPServer
from os import getcwd

# get path of file
# local_path = os.path.dirname(os.path.abspath(__file__))
# setting ip and port
from tools.data_tools import send_track_info

hostName = "localhost"
serverPort = 8080

# set the cgi directory
handler = CGIHTTPRequestHandler
handler.cgi_directories.append('/cgi-files')


class MyServer(handler):
	cgi_list: [str] = None
	callbacks: [] = None

	def get_post_data(self) -> dict[str, str]:
		"""
		Formats the POST data from the header and returns it
		:return: a dictionary with the POST variables and values
		"""
		form = cgi.FieldStorage(fp=self.rfile, headers=self.headers,
		                        environ={'REQUEST_METHOD': 'POST', 'CONTENT_TYPE': self.headers['Content-Type'], })
		data = dict()
		for item in form.list:
			data[item.name] = item.value
		return data

	def clean_path(self):
		# Removes the first '/', GET variables and anchors from the path, leaving a clean path and filename
		return self.path[1:].split("?")[0].split("#")[0]

	def do_GET(self):
		if self.clean_path() in self.cgi_list:
			self.path = "/cgi-files" + self.path
		else:
			self.path = "/webapp" + self.path
		CGIHTTPRequestHandler.do_GET(self)

		# self.send_response(200)
		# self.send_header("Content-type", "text/html")
		# self.end_headers()
		# valid_files = ["index.html", "script.js", "save_backend.php", "test.php"]
		# if file in valid_files:
		#     self.wfile.write(open("webapp/" + file, "rb").read())

	def do_POST(self):
		if self.clean_path() == "save_track_info.py":
			form = cgi.FieldStorage(fp=self.rfile, headers=self.headers,
			                        environ={'REQUEST_METHOD': 'POST', 'CONTENT_TYPE': self.headers['Content-Type']})
			if "data" not in form:
				print("Data missing when calling save_track_info.py")
			else:
				send_track_info(form["data"].value, self.callbacks["get_track_info"])
			self.send_response(200)
			self.end_headers()
			self.wfile.write(b"OK")
			return
		if self.clean_path() in self.cgi_list:
			self.path = "/cgi-files" + self.path
			CGIHTTPRequestHandler.do_POST(self)
		else:
			self.send_response(501, "Not allowed")
			self.end_headers()


def prepare_php_ini():
	open("php.ini", "w").write("cgi.force_redirect = 0\ndoc_root = " + getcwd())


def prepare_cgi_list():
	# list with files that have to be executed as a cgi, and thus are placed in the cgi folder
	MyServer.cgi_list = []
	for file in os.listdir("cgi-files"):
		MyServer.cgi_list.append(file)
	# print("CGI scripts: ")
	# [print(name) for name in MyServer.cgi_list]


class Webserver:
	callbacks: [] = None
	web_server = None

	def __init__(self):
		file_path = os.path.dirname(os.path.abspath(__file__))
		os.chdir(file_path)
		prepare_php_ini()
		prepare_cgi_list()
		# noinspection HttpUrlsUsage
		print("Server started http://%s:%s" % (hostName, serverPort))

	def run(self, callbacks: []):
		self.callbacks = callbacks
		MyServer.callbacks = self.callbacks
		self.web_server = HTTPServer((hostName, serverPort), MyServer)
		self.web_server.serve_forever()

	def stop(self):
		self.web_server.server_close()


if __name__ == "__main__":
	webserver = Webserver()
	try:
		webserver.run(None)
	except KeyboardInterrupt:
		pass

	webserver.stop()
	print("Server stopped.")

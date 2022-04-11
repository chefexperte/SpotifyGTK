import cgi
import os
from http.server import CGIHTTPRequestHandler, HTTPServer
from os import getcwd

# setting ip and port
hostName = "localhost"
serverPort = 8080

# set the cgi directory
handler = CGIHTTPRequestHandler
handler.cgi_directories.append('/cgi-files')


class MyServer(handler):
    # list with files that have to be executed as a cgi, and thus are placed in the cgi folder
    cgi_list = []
    for file in os.listdir("cgi-files"):
        cgi_list.append(file)

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
        # self.log_message(self.path)
        CGIHTTPRequestHandler.do_GET(self)

        # self.send_response(200)
        # self.send_header("Content-type", "text/html")
        # self.end_headers()
        # valid_files = ["index.html", "script.js", "save_backend.php", "test.php"]
        # if file in valid_files:
        #     self.wfile.write(open("webapp/" + file, "rb").read())

    def do_POST(self):
        if self.clean_path() in self.cgi_list:
            self.path = "/cgi-files" + self.path
            # self.log_message(self.path)
            CGIHTTPRequestHandler.do_POST(self)
        else:
            self.send_response(501, "Not allowed")
            self.end_headers()


def prepare_php_ini():
    open("php.ini", "w").write("cgi.force_redirect = 0\ndoc_root = " + getcwd())


if __name__ == "__main__":
    prepare_php_ini()
    webServer = HTTPServer((hostName, serverPort), MyServer)
    # noinspection HttpUrlsUsage
    print("Server started http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")

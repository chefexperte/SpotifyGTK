from http.server import CGIHTTPRequestHandler, HTTPServer
from os import getcwd

hostName = "localhost"
serverPort = 8080

handler = CGIHTTPRequestHandler
handler.cgi_directories.append('/php-cgi')


class MyServer(handler):

    def do_GET(self):
        file = self.path[1:].split("?")[0].split("#")[0]
        php_handle = ["test.php", "save_backend.php", "post_test.html"]
        if file in php_handle:
            self.path = "/php-cgi" + self.path
        else:
            self.path = "/webapp" + self.path
        self.log_message(self.path)
        CGIHTTPRequestHandler.do_GET(self)

        # self.send_response(200)
        # self.send_header("Content-type", "text/html")
        # self.end_headers()
        # valid_files = ["index.html", "script.js", "save_backend.php", "test.php"]
        # if file in valid_files:
        #     self.wfile.write(open("webapp/" + file, "rb").read())

    def do_POST(self):
        file = self.path[1:].split("?")[0].split("#")[0]
        php_handle = ["test.php", "save_backend.php", "post_test.html"]

        # if file == "save_backend.php":
        #     self.send_response(201, "Everything good wallah")
        #     self.end_headers()
        #     form = cgi.FieldStorage(fp=self.rfile, headers=self.headers,
        #                            environ={'REQUEST_METHOD': 'POST', 'CONTENT_TYPE': self.headers['Content-Type'], })
        #     for item in form.list:
        #         # print(item.name)
        #         # print(item.value)
        #         open("token.txt", "w").write(item.value)
        #
        #     return
        if file in php_handle:
            self.path = "/php-cgi" + self.path
            self.log_message(self.path)
            CGIHTTPRequestHandler.do_POST(self)
        else:
            self.send_response(501, "Not allowed")
            # self.send_header("Content-type", "text/html")
            self.end_headers()
            # valid_files = ["index.html", "script.js", "save_backend.php", "test.php"]
            # file = self.path[1:].split("?")[0].split("#")[0]
            # if file in valid_files:
            #     self.wfile.write(open("webapp/" + file, "rb").read())


def prepare_php_ini():
    open("php.ini", "w").write("cgi.force_redirect = 0\ndoc_root = " + getcwd())


if __name__ == "__main__":
    prepare_php_ini()

    webServer = HTTPServer((hostName, serverPort), MyServer)
    print("Server started http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")

import os
from threading import Thread
from time import sleep

from web_controller import WebController
from main_ui import SpotifyGTK
from server.webserver import Webserver


def run_server(serv: Webserver):
    serv.run()


def run_web_controller(ctrl: WebController):
    ctrl.run_controller(callbacks)


def run_ui(ui: SpotifyGTK):
    ui.run_ui(callbacks)


def toggle_play(d):
    controller.togglePlay(d)


def backend_ready():
    window.backend_ready_callback()


def report_state(position: int, duration: int):
    window.report_state_callback(position, duration)


callbacks = {"backend_ready": backend_ready, "toggle_play": toggle_play, "report_state": report_state}

if __name__ == "__main__":
    path = os.getcwd()
    os.environ["PATH"] += os.pathsep + path
    mail = input("\nEmail: ")
    passw = input("\nPassword: ")
    server = Webserver()
    controller = WebController(mail, passw)
    window = SpotifyGTK()
    srv = Thread(target=run_server, args=[server])
    ctl = Thread(target=run_web_controller, args=[controller])
    uiw = Thread(target=run_ui, args=[window])

    srv.start()
    ctl.start()
    uiw.start()

    while True:
        sleep(0.5)
        if not uiw.is_alive():
            if controller is not None:
                controller.stop()
                del controller
            if server is not None:
                server.web_server.shutdown()
                server.stop()
                del server
            break

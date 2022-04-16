import os
from threading import Thread
from time import sleep

from web_controller import WebController
from main_ui import SpotifyGtkUI
from server.webserver import Webserver


def run_server(serv: Webserver):
    """
    This method starts the webserver, should be run in a thread
    :param serv: A initialized Webserver
    """
    serv.run()


def run_web_controller(ctrl: WebController):
    """
    This method starts the selenium web controller with the callbacks variable
    :param ctrl: A initialized WebController
    """
    ctrl.run_controller(callbacks)


def run_ui(ui: SpotifyGtkUI):
    """
    This method runs the GTK/Libadwaita UI with the callbacks variable
    :param ui: A initialized SpotifyGtkUI
    """
    ui.run_ui(callbacks)


def toggle_play(d):
    """
    This callback is called from the ui, and tells the controller to press play
    :param d: is given by the button connect event
    """
    controller.togglePlay(d)


def backend_ready():
    """
    Is called from the controller, when the webpage finished loading and is ready to play music
    """
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
    window = SpotifyGtkUI()
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
                controller.dead = True
                controller.stop()
                del controller
            if server is not None:
                server.web_server.shutdown()
                server.stop()
                del server
            break

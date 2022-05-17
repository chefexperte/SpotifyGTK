import logging
import os
import threading

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.wait import WebDriverWait

import server.webserver


class AuthController:
    driver: webdriver.Firefox = None
    automatic_login: bool = False

    def __init__(self, automatic_login):
        self.automatic_login = automatic_login

    def stop(self):
        if self.driver:
            self.driver.quit()

    def element_exists(self, by: By, value: str) -> bool:
        try:
            self.driver.find_element(by, value)
        except NoSuchElementException:
            return False
        return True

    def driver_wait(self, secs: float):
        try:
            WebDriverWait(self.driver, secs).until(lambda l: False, "")
        except TimeoutException:
            pass

    def run_controller(self):
        options = Options()
        options.set_preference("media.eme.enabled", True)
        options.set_preference("media.gmp-manager.updateEnabled", True)
        self.driver = webdriver.Firefox(options=options)
        self.driver.get("http://localhost:8080/get_auth.html")
        while True:
            if self.element_exists(By.ID, "initMessage"):
                if self.driver.find_element(By.ID, "initMessage").text == "Login success.":
                    break
            self.driver_wait(0.5)
        self.driver_wait(1)
        self.stop()
        logging.log(logging.INFO, "Login success")


def run_auth():
    path = os.getcwd()
    print(path)
    os.environ["PATH"] += os.pathsep + path
    srv = server.webserver.Webserver()
    threading.Thread(target=srv.run, args=[]).start()
    controller = AuthController(False)
    controller.run_controller()
    if srv is not None:
        srv.web_server.shutdown()
        srv.stop()
        del srv


if __name__ == "__main__":
    run_auth()

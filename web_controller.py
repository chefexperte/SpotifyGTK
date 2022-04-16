import sys
from threading import Thread
from time import sleep

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, TimeoutException


class WebController:
    driver: webdriver.Firefox = None
    callbacks: [()] = None
    dead = False

    def stop(self):
        if self.driver:
            self.driver.quit()

    def __init__(self, user: str, passw: str):
        self.username = user
        self.password = passw

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

    def perform_login(self) -> bool:
        # check if login is in the url
        if self.driver.current_url.lower().count("login") < 1:
            return False
        # check if a login field exists
        if not self.element_exists(By.ID, "login-username"):
            return False
        # type in user and pass
        self.username, self.password = self.callbacks["get_login"]
        self.driver.find_element(by="id", value="login-username").send_keys(self.username)
        self.driver.find_element(by="id", value="login-password").send_keys(self.password)
        # check remember me button
        remember = self.driver.find_element(by="id", value="login-remember").is_selected()
        if not remember:
            self.driver.find_element(by="id", value="login-remember").find_element(by=By.XPATH, value='..'). \
                find_element(by=By.TAG_NAME, value="span").click()
        # login
        self.driver.find_element(by=By.ID, value="login-button").click()
        # wait a little for finishing login
        self.driver_wait(2)
        # check if an error message is displayed
        if self.driver.page_source.lower().count("incorrect username or password") > 0:
            print("Invalid login.")
        else:
            # no error = success
            if self.driver.current_url.count("/authorize") > 0 or self.driver.current_url.count("http://localhost") > 0:
                print("Login successful.")
                return True
            else:
                print("Login not successful.")
        return False

    def perform_auth(self) -> bool:
        success = True
        if not self.driver.current_url.lower().count("login") < 1:
            # log in
            print("Logging in...")
            success = self.perform_login()
        if success:
            # perform auth
            print("Performing auth...")
            # wait if auto-redirecting because auth was already given
            self.driver_wait(2)
            # loop through buttons
            for button in self.driver.find_elements(By.TAG_NAME, "button"):
                # if button is the accept button, click
                testid = button.get_attribute("data-testid")
                if testid is not None and testid == "auth-accept":
                    button.click()
            self.driver_wait(2)
            # if we were redirected to localhost, we have success.
            if self.driver.current_url.count("http://localhost") > 0:
                return True
        return False

    def run_controller(self, callbacks: [()]):
        self.callbacks = callbacks
        options = Options()
        options.set_preference("media.eme.enabled", True)
        options.set_preference("media.gmp-manager.updateEnabled", True)
        options.add_argument('--headless')
        # options.add_argument('--profile')
        # options.add_argument(path + '/firefox-profile')
        # options.add_argument('--P')
        # options.log.level = "trace"
        self.driver = webdriver.Firefox(options=options)
        self.driver.get("http://localhost:8080/")
        self.driver_wait(2)
        ready = True
        if self.driver.current_url.count("spotify.com") > 0:
            if self.perform_auth():
                print("Auth and login success.")
            else:
                print("There has been a problem with login or auth.")
                ready = False
        if ready:
            if self.element_exists(By.ID, "playHere"):
                for i in range(0, 10):
                    if not self.driver.find_element(By.ID, "playHere").is_enabled():
                        self.driver_wait(0.5)
                self.driver.find_element(By.ID, "playHere").click()
                # We have moved playback to the current device, now set player button clickable
                self.callbacks["backend_ready"]()
        loop = Thread(target=self.report_loop, args=[])
        loop.start()

    def report_loop(self):
        sleep(1)
        if not self.driver or self.dead:
            return
        position = int(self.driver.find_element(By.ID, "playbackPosition").text)
        duration = int(self.driver.find_element(By.ID, "trackDuration").text)
        self.callbacks["report_state"](position, duration)
        self.report_loop()

    # noinspection PyUnusedLocal
    def togglePlay(self, d):
        if self.element_exists(By.ID, "togglePlay"):
            self.driver.find_element(By.ID, "togglePlay").click()


if __name__ == "__main__":
    username = ""
    password = ""
    if len(sys.argv) == 3:
        username = sys.argv[1]
        password = sys.argv[2]

    if len(sys.argv) == 2:
        username = sys.argv[1]
        password = input("password: ")
    controller = WebController(username, password)

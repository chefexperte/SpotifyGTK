import sys
from threading import Thread
from time import sleep

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.wait import WebDriverWait

from tools.data_wrapper import PlaybackInfo


class WebController:
    driver: webdriver.Firefox = None
    callbacks: [()] = None
    dead = False

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

    def run_controller(self, callbacks: [()], headless: bool):
        self.callbacks = callbacks
        options = Options()
        options.set_preference("media.eme.enabled", True)
        options.set_preference("media.gmp-manager.updateEnabled", True)
        options.set_preference("browser.cache.check_doc_frequency", 1)
        # options.set_preference("security.sandbox.content.level", 0)
        if headless:
            options.add_argument('--headless')
        options.add_argument('--profile')
        # path = os.path.dirname(os.path.abspath(__file__))
        # options.add_argument(path + '/firefox-profile')
        options.add_argument('/home/aaron/.mozilla/firefox/spotifygtk-profile')

        # options.add_argument('--P')
        # options.log.level = "trace"
        self.driver = webdriver.Firefox(options=options)
        self.driver.get("http://localhost:8080/")
        self.driver_wait(2)
        timer = 0
        if self.element_exists(By.ID, "playHere"):
            while True:
                timer += 1
                if not self.driver.find_element(By.ID, "playHere").is_enabled():
                    self.driver_wait(0.5)
                    if timer > 20:
                        self.callbacks["update_loading_message"]("Taking longer than usual...\nPlease stand by...")
                else:
                    break
            # self.driver.find_element(By.ID, "playHere").click()
            # We have moved playback to the current device, now set player button clickable
            self.callbacks["backend_ready"]()
        loop = Thread(target=self.report_loop, args=[])
        loop.start()

    def report_loop(self):
        while True:
            sleep(1)
            if not self.driver or self.dead:
                return
            if self.element_exists(By.ID, "position"):
                pos = self.driver.find_element(By.ID, "position").text
                if pos is None or pos == "" or pos == "undefined":
                    title = ""
                    position = 0
                    duration = 1
                else:
                    title = self.driver.find_element(By.ID, "trackTitle").text
                    position = int(pos)
                    duration = int(self.driver.find_element(By.ID, "trackDuration").text)
                info = PlaybackInfo(title, position, duration)
                info.playing = self.driver.find_element(By.ID, "isPlaying").text == "true"
                self.callbacks["report_state"](info)
        # self.report_loop()

    # noinspection PyUnusedLocal
    def toggle_play(self, d):
        if self.element_exists(By.ID, "togglePlay"):
            self.driver.find_element(By.ID, "togglePlay").click()

    def play_here(self):
        if self.element_exists(By.ID, "playHere"):
            self.driver.find_element(By.ID, "playHere").click()

    def set_volume(self, volume: int):
        if self.element_exists(By.ID, "volume"):
            self.driver.find_element(By.ID, "volume").clear()
            self.driver.find_element(By.ID, "volume").send_keys(int(volume))
            self.driver.find_element(By.ID, "setVolume").click()

    def set_position(self, position: int):
        if self.element_exists(By.ID, "playbackPosition"):
            self.driver.find_element(By.ID, "playbackPosition").clear()
            self.driver.find_element(By.ID, "playbackPosition").send_keys(int(position))
            self.driver.find_element(By.ID, "setPosition").click()

    def skip_next(self):
        if self.element_exists(By.ID, "skipNext"):
            self.driver.find_element(By.ID, "skipNext").click()

    def skip_previous(self):
        if self.element_exists(By.ID, "skipPrevious"):
            self.driver.find_element(By.ID, "skipPrevious").click()


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

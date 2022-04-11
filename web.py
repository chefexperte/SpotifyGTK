import os
import sys
from threading import Thread
from time import sleep
from pydbus import SessionBus
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.wait import WebDriverWait


def auto_close(d: webdriver, secs: float):
    sleep(secs)
    # d.quit()


if __name__ == "__main__":
    path = os.getcwd()
    os.environ["PATH"] += os.pathsep + path
    username = "test"
    password = "test"
    if len(sys.argv) == 3:
        username = sys.argv[1]
        password = sys.argv[2]

    if len(sys.argv) == 2:
        username = sys.argv[1]
        password = input("password: ")
    options = Options()
    options.set_preference("media.eme.enabled", True)
    options.set_preference("media.gmp-manager.updateEnabled", True)
    # options.add_argument('--headless')
    # options.add_argument('--profile')
    # options.add_argument(path + '/firefox-profile')
    # options.add_argument('--P')
    # options.log.level = "trace"
    driver = webdriver.Firefox(options=options)
    driver.get("https://accounts.spotify.com/en/login/")
    try:
        WebDriverWait(driver, 2).until(lambda l: False, "")
    except TimeoutException:
        pass
    login_success = False
    if driver.current_url.lower().count("login") > 0:
        driver.find_element(by="id", value="login-username").send_keys(username)
        driver.find_element(by="id", value="login-password").send_keys(password)

        remember = driver.find_element(by="id", value="login-remember").is_selected()
        if not remember:
            driver.find_element(by="id", value="login-remember").find_element(by=By.XPATH, value='..').\
                find_element(by=By.TAG_NAME, value="span").click()

        driver.find_element(by=By.ID, value="login-button").click()
        try:
            WebDriverWait(driver, 2).until(lambda l: False, "")
        except TimeoutException:
            pass
        if driver.page_source.lower().count("incorrect username or password") > 0:
            print("Invalid login.")
        else:
            if driver.current_url.count("/status") > 0:
                print("Login successful.")
                login_success = True
            else:
                print("Login not successful.")
    else:
        login_success = True

    if login_success:
        # driver.get(f"file://{os.getcwd()}/test.html")
        driver.get("https://open.spotify.com")
        try:
            WebDriverWait(driver, 2).until(lambda l: False, "")
        except TimeoutException:
            pass
        element = driver.find_element(By.TAG_NAME, "body")
        driver.execute_script("""
        var element = arguments[0];
        element.parentNode.removeChild(element);
        """, element)
        new_element = """
        var scr = document.createElement('iframe');
        scr.src = "https://open.spotify.com/embed/track/TRACK_ID_HERE?utm_source=generator"
        scr.allow = "encrypted-media";
        document.body = document.createElement('body');
        document.body.appendChild(scr);
        """
        driver.execute_script(new_element)
        # start playback

        # audio controls
        bus = SessionBus()
        bus.get('.MediaPlayer2')

    thr = Thread(target=auto_close, args=[driver, 15])
    thr.run()

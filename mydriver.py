import logging
import os
import time
import zipfile

from lxml import html
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver import ChromeOptions
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.remote.remote_connection import LOGGER

# Relative paths to files needed for proxies with authentication.
EXTENSION_ZIP_FILE = 'proxies/temp_extension.zip'
MANIFEST_JSON_FILE = 'proxies/manifest.json'
BACKGROUND_JS_FILE = 'proxies/background.js'


class Driver(webdriver.Chrome):
    """
    This is a modification of the default selenium.webdriver.Chrome. It has a lot of additional features.
    It has headless mode, custom window size, quick mode, custom user agent, proxies, different page load strategies,
    custom execute path to chromedriver. Also have a plenty of useful methods.
    """

    # __init__ - function that starts while an instance creating.
    def __init__(self, headless: bool = False, window_size: list = None, quick_mode=False, log=False,
                 user_agent: str = None, proxies=None, load_strategy='normal', exe_path: str = None):
        if window_size is None:
            window_size = [1366, 768]
        if user_agent is None:
            self.user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, ' \
                              'like Gecko) Chrome/83.0.4103.97 Safari/537.36'
        else:
            self.user_agent = user_agent
        self.script_directory = os.path.dirname(__file__)
        self.caps = DesiredCapabilities().CHROME
        self.caps["pageLoadStrategy"] = load_strategy  # Can be "normal", "eager", "none". It's long, normal, quick.
        self.options_custom = ChromeOptions()
        self.ser_args = []
        if log is False:
            print('Selenium console logging set to False.')
            LOGGER.setLevel(logging.WARNING)
            self.options_custom.add_argument("--log-level=3")
            self.options_custom.add_argument("--disable-logging")
            self.options_custom.add_argument("--silent")
            self.options_custom.add_experimental_option('excludeSwitches', ['enable-logging'])
            self.ser_args = ['--silent']
        self.options_custom.add_argument('--window-size={0},{1}'.format(window_size[0], window_size[1]))
        self.options_custom.add_argument('--user-agent={0}'.format(self.user_agent))
        self.options_custom.add_argument('-lang= en')
        # Deletes "Chrome is being controlled by automated test software" message.
        self.options_custom.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.options_custom.add_experimental_option("useAutomationExtension", False)
        if headless is True:
            self.options_custom.add_argument('--headless')  # enables headless mode

        # Proxies part.
        if proxies is not None:
            # proxies = 'http://142.93.112.205:8080' - example #1 (without authentication)
            # proxies = 'http://user:password@142.93.112.205:8080' - example #2 (with authentication)
            if '@' not in proxies:
                self.options_custom.add_argument('--proxy-server={}'.format(proxies))
            else:
                proxies = proxies[proxies.index("://") + 3:]
                part1, part2 = proxies.split('@')
                username, password = part1.split(':')
                host, port = part2.split(':')

                with open(self.script_directory + '/' + MANIFEST_JSON_FILE, 'r', encoding='utf8') as manifest_file:
                    manifest_json = ''.join([line for line in manifest_file.readlines()])

                with open(self.script_directory + '/' + BACKGROUND_JS_FILE, 'r', encoding='utf8') as background_file:
                    background_js = ''.join([line for line in background_file.readlines()])
                    background_js = background_js % (host, port, username, password)

                with zipfile.ZipFile(self.script_directory + '/' + EXTENSION_ZIP_FILE, 'w') as zp:
                    zp.writestr("manifest.json", manifest_json)
                    zp.writestr("background.js", background_js)
                self.options_custom.add_extension(self.script_directory + '/' + EXTENSION_ZIP_FILE)

        # quick mode helps to load pages faster.
        if quick_mode is True:
            self.options_custom.add_argument('--ignore-certificate-errors')
            self.blink_settings_list = []
            self.disabled_features_list = []
            self.chrome_prefs = dict()
            self.chrome_prefs['profile.default_content_setting_values.notifications'] = 2
            self.chrome_prefs['profile.default_content_setting_values.images'] = 2
            self.blink_settings_list.append('imagesEnabled=false')
            self.blink_settings_list.append('loadsImagesAutomatically=false')
            self.blink_settings_list.append('mediaPlaybackRequiresUserGesture=true')
            self.disabled_features_list.append('PreloadMediaEngagementData')
            self.disabled_features_list.append('AutoplayIgnoreWebAudio')
            self.disabled_features_list.append('MediaEngagementBypassAutoplayPolicies')
            if self.disabled_features_list:
                self.options_custom.add_argument(f"--disable-features={','.join(self.disabled_features_list)}")
            if self.blink_settings_list:
                self.options_custom.add_argument(f"--blink-settings={','.join(self.blink_settings_list)}")
            if self.chrome_prefs:
                self.options_custom.add_experimental_option('prefs', self.chrome_prefs)
            self.options_custom.add_argument('--disable-device-discovery-notifications')
            self.options_custom.add_argument('--disable-dev-shm-usage')
            self.options_custom.add_argument('--no-sandbox')
            self.options_custom.add_argument('--allow-insecure-localhost')

        # Call standard _init__ function with customized options and capabilities.
        # If exe_path is not defined, chromedriver file should be in the same folder with my_driver.py
        try:
            if exe_path:
                webdriver.Chrome.__init__(self, options=self.options_custom, desired_capabilities=self.caps,
                                          executable_path=r'{}'.format(exe_path), service_args=self.ser_args)
            else:
                webdriver.Chrome.__init__(self, options=self.options_custom, desired_capabilities=self.caps,
                                          service_args=self.ser_args)
        except:
            print(os.name)
            print()
            if os.name == 'posix':
                driver_file = 'chromedriver'
            else:
                driver_file = 'chromedriver.exe'
            webdriver.Chrome.__init__(self, options=self.options_custom, desired_capabilities=self.caps,
                                      executable_path=r'{}'.format(os.path.dirname(__file__) + f'/{driver_file}'),
                                      service_args=self.ser_args)

    # Get the current page's html object, to use xpath with it.
    def dom(self):
        page_text = self.page_source
        return html.fromstring(page_text)

    # Find element by XPath.
    def xpath(self, path):
        return self.find_element_by_xpath(path)

    # Find a list of elements by Xpath.
    def xpathes(self, path):
        return self.find_elements_by_xpath(path)

    # Get src code of a page as str value.
    def get_source(self):
        return self.page_source

    # Scroll to a place on a page.
    def scroll(self, h):
        return self.execute_script(f'window.scrollTo(0, {h}); return window.pageYOffset;')

    # Scroll down method.
    def scroll_down(self, h=0):
        return self.scroll(h or 'document.body.scrollHeight')

    # Scroll up method.
    def scroll_up(self, h=0):
        return self.scroll(-h or '-document.body.scrollHeight')

    # Find and clicks element by Xpath.
    def click(self, path):
        element = self.xpath(path)
        element.click()

    def create_window(self):
        self.execute_script("window.open()")

    def right_click(self, path):
        element = self.xpath(path)
        action_chains = ActionChains(self)
        action_chains.context_click(element).perform()

    # It will try to click element until this element gets clickable.
    def force_click(self, path, err_delay=1, post_delay=0):
        '''
        :param path: Xpath address of an element.
        :param err_delay: Delay before trying again.
        :param post_delay: Delay after successful click. It's needed in case if some windows should open.
        '''
        counter = 0
        while True:
            if counter % 10 == 0 and counter != 0:
                print("Try to find element with Xpath: ", path, "...")
            try:
                counter += 1
                self.click(path)
                time.sleep(post_delay)
                break
            except:
                time.sleep(err_delay)
                continue

    def send_keys(self, path, text):
        element = self.xpath(path)
        element.send_keys(text)

    # This function waits until an element appear on a page.
    def wait_until(self, path, delay=0.8, limit=51):
        counter = 1
        while True:
            if counter == limit:
                print('Too many attempts. Return False.')
                return False
            if counter % 10 == 0:
                print('Trying to see element for the {} time. Xpath: {}'.format(counter, path))
            try:
                dom = self.dom()
            except:
                continue
            element = dom.xpath(path)
            if bool(element) is True:
                return True
            else:
                counter += 1
                time.sleep(delay)
                continue

    def cookies_to_header(self, user_agent: str = None) -> dict:
        """
        It takes a list of cookies that .get_cookies() method of Selenium webdriver returns. It processes cookies
        in the way it can be used as a "headers" argument for requests.get() method. Useful for imitating authenticated
        user. Selenium can be used for fetching cookies_list and return of the function may be used in requests.

        :param cookies_list: a list with dicts. This list is produced by .get_cookies() method of Selenium webdriver.
        :param user_agent: a string with User Agent for request header.
        :return: a dictionary with 2 keys: User-Agent (str) and Cookie (str).
        """
        if user_agent is None:
            user_agent = self.user_agent
        header = {'User-Agent': user_agent}
        new_list = []
        for cookie in self.get_cookies():
            new_list.append(cookie['name'] + '=' + str(cookie['value']))
        cookie = '; '.join(new_list)
        header['Cookie'] = cookie

        return header

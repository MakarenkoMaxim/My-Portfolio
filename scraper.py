import time
from typing import List

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys

from inputs.config import *
from source.data_saver import Post, Comment, PostLink
from source.date_fixer import fix_date
from source.mydriver import Driver
from source.tor.tor_network import TorNetwork


class Scraper:
    def __init__(self):
        """
        Prepare WebDriver and TOR network.
        """
        self.tor = TorNetwork()
        self.tor.launch_network()
        self.driver = Driver(proxies="socks5://127.0.0.1:9050")

    def xpath_exists(self, xpath) -> bool:
        """
        Check XPath existing.
        :param xpath: web element XPath.
        :return: boolean variable.
        """
        try:
            self.driver.find_element_by_xpath(xpath)
            exist = True
        except NoSuchElementException:
            exist = False
        return exist

    def login(self, url, email, password) -> None:
        """
        Login to a TikTok account.
        :param url: link to connection with.
        :param email: a string with your email.
        :param password: a string with your email password.
        """
        try:
            self.driver.get(url=url)
            time.sleep(12)

            self.driver.find_element_by_class_name("login-button").click()
            time.sleep(5)

            # switch to iframe
            iframe = self.driver.find_element_by_xpath("//iframe[@class='jsx-2041920090']")
            self.driver.switch_to.frame(iframe)
            time.sleep(5)

            if self.xpath_exists("//div[contains(text(), 'Войти через Facebook')]"):
                self.driver.find_element_by_xpath("//div[contains(text(), 'Войти через Facebook')]").click()
                time.sleep(5)
            if self.xpath_exists("//div[contains(text(), 'Log in with Facebook')]"):
                self.driver.find_element_by_xpath("//div[contains(text(), 'Log in with Facebook')]").click()
                time.sleep(5)

            self.driver.switch_to.window(self.driver.window_handles[1])
            time.sleep(3)

            email_input = self.driver.find_element_by_name("email")
            email_input.clear()
            email_input.send_keys(email)
            time.sleep(3)

            password_input = self.driver.find_element_by_name("pass")
            password_input.clear()
            password_input.send_keys(password, Keys.ENTER)
            time.sleep(15)

            self.driver.switch_to.window(self.driver.window_handles[0])
        except Exception as ex:
            print(ex)

    def get_acc_links(self) -> List[str]:
        """
        Get links to necessary accounts.
        :return: list of account links.
        """
        # get a search results
        search = self.driver.find_element_by_name("q")
        search.send_keys(tag)
        search.send_keys(Keys.ENTER)
        time.sleep(2)

        accounts = self.driver.find_elements_by_xpath("/html/body/div/div/div[2]/div[2]/a")

        # return links to accounts
        accounts_href = []
        for acc in accounts:
            accounts_href.append(acc.get_attribute("href"))
        return accounts_href

    def get_posts_from_acc(self) -> List[PostLink]:
        """
        Get posts links from the account.
        :return: list of post link.
        """
        post_list = []

        # scroll page [scr] times
        for _ in range(scr):
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(6)

        # scrape post links
        for i in range(36 * scr - 1):
            path = "/html/body/div/div/div[2]/div[2]/div/main/div[2]/div[1]/div[{I}]/div[1]/div/div/a".format(
                I=i + 1)

            v_path1 = "/html/body/div/div/div[2]/div[2]/div/main/div[2]/div[1]/div[{I}]/div[2]/div/div/div[2]/div[1]/strong".format(
                I=i + 1)
            v_path2 = "/html/body/div/div/div[2]/div[2]/div/main/div[2]/div[1]/div[{I}]/div[1]/div/div/a/span/div/div/div/div/div/strong".format(
                I=i + 1)

            post_link = None
            if self.xpath_exists(path):
                post_link = self.driver.find_element_by_xpath(path)

            post_views = None
            if self.xpath_exists(v_path1):
                post_views = self.driver.find_element_by_xpath(v_path1).text
            elif self.xpath_exists(v_path2):
                post_views = self.driver.find_element_by_xpath(v_path2).text

            if post_link is not None and post_views is not None:
                post_list.append(PostLink(link=post_link, views=post_views))

        return post_list

    def scrape_comments(self) -> List[Comment]:
        """
        Get information about post comments.
        :return: list with comments.
        """
        comments = []
        for i in range(20):
            comm_text_path1 = "/html/body/div/div/div[2]/div[2]/div/main/div/div[2]/div[2]/div[3]/div/div[{I}]/div[1]/div[1]/p/span".format(
                I=i + 1)
            comm_text_path2 = "/html/body/div[1]/div/div[2]/div[2]/div/main/div/div[2]/div[2]/div[3]/div/div[{I}]/div[1]/div[1]/p/span".format(
                I=i + 1)
            comm_text_path3 = "/html/body/div[1]/div/div[2]/div[2]/div/div/main/div/div[2]/div[2]/div[3]/div/div[{I}]/div[1]/div[1]/p/span".format(
                I=i + 1)
            text = ""
            comm_likes = ""
            if self.xpath_exists(comm_text_path1):
                text = self.driver.find_element_by_xpath(comm_text_path1).text

                comm_likes1 = "/html/body/div[1]/div/div[2]/div[2]/div/main/div/div[2]/div[2]/div[3]/div/div[{I}]/div[1]/div[2]/span".format(
                    I=i + 1)

                comm_likes2 = "/html/body/div[1]/div/div[2]/div[2]/div/div/main/div/div[2]/div[2]/div[3]/div/div[{I}]/div[1]/div[2]/span".format(
                    I=i + 1)

                if self.xpath_exists(comm_likes1):
                    comm_likes = self.driver.find_element_by_xpath(comm_likes1).texxt
                elif self.xpath_exists(comm_likes2):
                    comm_likes = self.driver.find_element_by_xpath(comm_likes2).texxt

            elif self.xpath_exists(comm_text_path2):
                text = self.driver.find_element_by_xpath(comm_text_path2).text
                comm_likes1 = "/html/body/div[1]/div/div[2]/div[2]/div/main/div/div[2]/div[2]/div[3]/div/div[{I}]/div[1]/div[2]/span".format(
                    I=i + 1)

                comm_likes2 = "/html/body/div[1]/div/div[2]/div[2]/div/div/main/div/div[2]/div[2]/div[3]/div/div[{I}]/div[1]/div[2]/span".format(
                    I=i + 1)

                if self.xpath_exists(comm_likes1):
                    comm_likes = self.driver.find_element_by_xpath(comm_likes1).texxt
                elif self.xpath_exists(comm_likes2):
                    comm_likes = self.driver.find_element_by_xpath(comm_likes2).texxt

            elif self.xpath_exists(comm_text_path3):
                text = self.driver.find_element_by_xpath(comm_text_path3).text
                comm_likes1 = "/html/body/div[1]/div/div[2]/div[2]/div/main/div/div[2]/div[2]/div[3]/div/div[{I}]/div[1]/div[2]/span".format(
                    I=i + 1)

                comm_likes2 = "/html/body/div[1]/div/div[2]/div[2]/div/div/main/div/div[2]/div[2]/div[3]/div/div[{I}]/div[1]/div[2]/span".format(
                    I=i + 1)

                if self.xpath_exists(comm_likes1):
                    comm_likes = self.driver.find_element_by_xpath(comm_likes1).text
                elif self.xpath_exists(comm_likes2):
                    comm_likes = self.driver.find_element_by_xpath(comm_likes2).text

            if comm_likes != "" and text != "":
                comments.append(Comment(text=text, likes=comm_likes))
        return comments

    def get_post_links(self, acc_links) -> (List[str], List[str]):
        """
        Get links to posts from necessary accounts.
        :param acc_links: list of account links.
        :return: list of post links.
        """

        posts_href = []
        posts_views = []

        for link in acc_links:
            try:
                self.driver.get(url=link)  # get page with account videos
                post_links = self.get_posts_from_acc()
            except:
                # tor.restart_network()
                self.driver.get(url=link)
                post_links = self.get_posts_from_acc()

            # get post links
            for post in post_links:
                posts_href.append(post.link.get_attribute("href"))
                posts_views.append(post.views)

        return posts_href, posts_views

    def scrape_post(self, link, views) -> Post:
        """
        Get information about TikTok post.
        :param link: a string with link to TikTok video.
        :param views: number of views of the video.
        :return: information about TikTok post.
        """
        self.driver.get(url=link)

        try:
            date_time = self.driver.find_element_by_xpath(
                "/html/body/div/div/div[2]/div[2]/div/div/main/div/div[1]/span/div/div[1]/div[1]/a[2]/h4").text
        except NoSuchElementException:
            self.tor.restart_network()
            time.sleep(5)
            self.driver.get(url=link)
            date_time = self.driver.find_element_by_xpath(
                "/html/body/div/div/div[2]/div[2]/div/div/main/div/div[1]/span/div/div[1]/div[1]/a[2]/h4").text

        date_time = fix_date(date_time)
        try:
            self.driver.find_element_by_xpath(
                "/html/body/div/div/div[2]/div[2]/div/div/main/div/div[1]/span/div/div[1]/div[5]/div[2]/div[2]/div").click()
        except NoSuchElementException:
            self.driver.find_element_by_xpath(
                "/html/body/div/div/div[2]/div[2]/div/div/main/div/div[1]/span/div/div[1]/div[4]/div[2]/div[2]/div").click()
        com_path1 = "/html/body/div/div/div[2]/div[2]/div/main/div/div[2]/div[2]/div[2]/div[1]/div[1]/div[2]/strong"
        com_path2 = "/html/body/div[1]/div/div[2]/div[2]/div/div/main/div/div[2]/div[2]/div[2]/div[1]/div[1]/div[2]/strong"
        com_path3 = "/html/body/div/div/div[2]/div[2]/div/div/main/div/div[2]/div[2]/div[2]/div[1]/div[1]/div[2]/strong"
        comm_num = ''
        if self.xpath_exists(com_path1):
            comm_num = self.driver.find_element_by_xpath(com_path1).text
        elif self.xpath_exists(com_path2):
            comm_num = self.driver.find_element_by_xpath(com_path2).text
        elif self.xpath_exists(com_path3):
            comm_num = self.driver.find_element_by_xpath(com_path3).text

        likes_num = self.driver.find_element_by_xpath(
            "/html/body/div/div/div[2]/div[2]/div/div/main/div/div[2]/div[2]/div[2]/div[1]/div[1]/div[1]/strong").text
        description = self.driver.find_element_by_xpath(
            "/html/body/div/div/div[2]/div[2]/div/div/main/div/div[2]/div[2]/div[2]/h1")
        ds_text = ""
        ds_list = description.find_elements_by_tag_name('strong')
        for ds_el in ds_list:
            ds_text = ds_text + " " + ds_el.text
        description = ds_text

        comments = self.scrape_comments()

        return Post(date=date_time, comm_num=comm_num, likes_num=likes_num, description=description,
                    views_num=views, comments=comments, post_url=link)

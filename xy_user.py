"""
This file stands for a XY Adviser user representation in the code. A user's behavior and attributes. It contain basic
behaviour implement and all the possible attributes. Behaviour may be extended later.
"""
import time

from selenium.webdriver.common.keys import Keys

from source.my_driver import Driver

LOGIN_URL = 'https://www1.xyadviser.com/sign_in'


class Segment:

    def __init__(self, segment_title: str = None, segment_id: int = None):
        """
        Initializing attributes of member segment
        :param segment_title: the name of a post creator's member segment (member category)
        :param segment_id: the ID of a post creator's member segment
        """
        self.title = segment_title
        self.id = segment_id

    def __str__(self):
        """
        Get a segment name
        :return: title of a segment
        """
        return self.title


class XYUser:
    """
    This class represents XY Adviser user with its attributes and behavior.
    """

    def __init__(self, uri: int = None, full_name: str = None, space_id: int = None, email: str = None,
                 password: str = None, description: str = None, introduction: str = None, number_posts: int = None,
                 followers: int = None, following: int = None, personal_links: dict = None, location: str = None,
                 groups: list = None, topics: list = None, profile_img_url: str = None, headless_driver: bool = True,
                 segment: Segment = None):
        """
        Initializing main attributes to fully reflect a user.
        :param uri: number that stands for a member's ID. "https://www1.xyadviser.com/members/2676168" ->  2676168.
        :param full_name: a full name of a user. F.e "Lionele Boce", "Robbie Rae".
        :param space_id: a user's feed id.
        :param email: email for log in to the system.
        :param password: a password to a user's account.
        :param description: a brief description of a user, taken from a member's page.
        :param introduction: Introduction section text of a member.
        :param number_posts: number of posts, made by a user.
        :param followers: number of followers.
        :param following: number of followings.
        :param personal_links: a dictionary where a key is a social network and a value is a URL to a user's page there.
        :param location: a string with a user's location from a member's page.
        :param groups: a list of group IDs, which a user belongs to.
        :param topics: a list of topics IDs, that are listed on a member's page
        :param profile_img_url: URL to a profile's image.
        :param headless_driver: boolean, show a Chrome window or not.
        :param segment: information about member segment.
        """
        self.uri = uri
        self.full_name = full_name
        self.space_id = space_id
        self.email = email
        self.password = password
        self.description = description
        self.introduction = introduction
        self.number_posts = number_posts
        self.followers = followers
        self.following = following
        self.personal_links = personal_links
        self.location = location
        self.groups = groups
        self.topics = topics
        self.profile_img_url = profile_img_url
        self.headless_driver = headless_driver
        self.segment = segment
        self.webdriver = None

    def __str__(self):
        return self.full_name

    def login(self):
        """
        Log in to a user's page. Creates a webdriver and logs in XY Adviser.
        """
        if self.email is None or self.password is None:
            raise ValueError('Email or password has not been set to the object. Cannot log in.')
        self.webdriver = Driver(headless=self.headless_driver)
        self.webdriver.get(LOGIN_URL)
        self.webdriver.send_keys('.//input[@type="email"]', self.email)
        self.webdriver.send_keys('.//input[@type="email"]', Keys.RETURN)
        time.sleep(4)
        self.webdriver.send_keys('.//input[@placeholder="Password"]', self.password)
        self.webdriver.send_keys('.//input[@placeholder="Password"]', Keys.RETURN)
        time.sleep(5)
        if 'incorrect email or password. Try again' in self.webdriver.page_source:
            raise ValueError('Cannot login - incorrect email or password.')

    def scrape_space_id(self) -> int:
        """
        Scrape a space ID (needed feed ID).
        :return: space ID.
        """
        if self.webdriver is None:
            raise ValueError("You haven't login to a user. You need to do it first with .login() method.")
        self.webdriver.get('https://www1.xyadviser.com/feed?sort=created_at')  # Sorting feed by creation date.
        dom = self.webdriver.dom()
        space_id = dom.xpath('.//meta[@property="al:ios:url"]/@content')
        space_id = ''.join(space_id)
        space_id = int(space_id[space_id.rfind('/') + 1:])

        return space_id

    def scrape_assign_space_id(self) -> int:
        """
        Get actual space ID and return it.
        :return: space ID.
        """
        self.space_id = self.scrape_space_id()

        return self.space_id

    def get_cookies(self) -> list:
        """
        Get cookies from webdriver.
        :return: list with cookies as strings.
        """
        cookies = self.webdriver.get_cookies()
        return cookies

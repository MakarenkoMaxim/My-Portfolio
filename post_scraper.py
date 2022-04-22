"""
This script contains a posts scraper class.
"""
import requests

from time import sleep
from typing import List
from json.decoder import JSONDecodeError
from source.entities.content_items import Post
from source.entities.xy_user import XYUser, Segment
from source.logger import Logger
from source.settings import Settings

POST_API_URL = 'https://www1.xyadviser.com/api/web/v1/spaces/{feed_id}/feed?page={page}&per_page={per_page}' \
               '&sort=created_at'
RESULTS_PER_PAGE = 100


class PostScraper:
    """
    A scraper for posts.
    """

    def __init__(self, logger: Logger, settings: Settings, feed_id: int, header: dict):
        """
        Initializing main instance attributes.
        :param logger: a self.logger to log data to a local file and console.
        :param settings: a Settings class object that has start_id and finish_id for posts and scraping delays.
        :param feed_id: an ID of a feed to scrape. Usually, it's a feed of a user from settings.
        :param header: dictionary with request header.
        """
        self.page = 1
        self.no_pages_left = False
        self.logger = logger
        self.settings = settings
        self.space_id = feed_id
        self.posts = []
        self.header = header

    def scrape_pages(self, text_full_processing: bool = None) -> List[Post]:
        """
        Scrape posts self.page by self.page in the feed.
        :param text_full_processing: the type of parsing. True - full processing, False - partial processing.
        :return: a list with Post objects.
        """
        while True:
            print('\n' + '-' * 50)

            if self.no_pages_left is True:
                self.logger.message('No more new items to scrape. All the items have been scraped.')
                return self.__finish_scraping()
            self.logger.message(f'Processing page {self.page}...')
            post_url = POST_API_URL.format(feed_id=self.space_id, page=self.page, per_page=RESULTS_PER_PAGE)
            try:
                posts_json = self._get_posts_list(post_url)
                sleep(self.settings.post_delay)
            except JSONDecodeError:
                print()
                self.logger.message(f'Captcha appeared, cannot scrape. Waiting {self.settings.captcha_delay} seconds '
                                    f'and trying again....')
                sleep(self.settings.captcha_delay)
                posts_json = self._get_posts_list(post_url)
            except:
                posts_json = []
            if len(posts_json) < 2 / 3 * RESULTS_PER_PAGE:
                self.no_pages_left = True
            item_counter = 1

            for item in posts_json:
                # Checking whether a post is from certain needed range.
                try:
                    post_id = int(item['post']['id'])

                except KeyError:
                    item_counter += 1
                    continue
                if post_id > self.settings.finish_id:
                    continue
                if self.page == 1 and item_counter == 1 and post_id < self.settings.start_id:
                    raise ValueError(
                        'The newest post ID is lower than start_id from input settings. Nothing to scrape.')
                if post_id <= self.settings.start_id:
                    print('')
                    self.logger.message('Found a post with finish_id. No more new posts left. Stop scraping...')
                    return self.__finish_scraping()

                self.logger.message(f'Processing item {item_counter}/{len(posts_json)}', one_line=True)
                post = self.raw_item_to_post(item, text_full_processing=text_full_processing)
                self.posts.append(post)
                item_counter += 1
            self.page += 1

    @staticmethod
    def raw_item_to_post(item: dict, text_full_processing: bool = None) -> Post:
        """
        Transform a dictionary that is returned by the API to a Post class object.
        :param item: a dictionary that represents a post.
        :param text_full_processing: the type of parsing. True - full processing, False - partial processing.
        :return: a Post class object with all the needed fields filled.
        """
        post = Post(uri=int(item['post']['id']), text_full_processing=text_full_processing)
        post.save_created_at(date_time=item['created_at'].split('.')[0])
        author = XYUser(uri=item['post']['creator_id'])

        author.segment = Segment()
        author.segment.title = ""

        if "primary_segment" in item["post"]["user"]:
            author.segment.id = item["post"]["user"]["primary_segment"]["id"]
            author.segment.title = item["post"]["user"]["primary_segment"]["title"]
        post.author = author

        if 'description' in item['post']:
            text = item['post']['description']
        elif 'description' in item['post']['sharing_meta']:
            text = item['post']['sharing_meta']['description']
        else:
            text = item['post']['content']['title']
        post.save_text(text=text)

        if item['post']['sharing_meta']['title'] == "Why I'm Here":
            tagged_post = True
        else:
            tagged_post = False

        post.save_tags(raw_tags_list=item['post']['tags'], tagged_post=tagged_post)
        post.likes_number = int(item['post']['cheer_count'])
        post.comments_number = int(item['post']['comment_count'])

        return post

    def _get_posts_list(self, post_url: str) -> list:
        posts_json = requests.get(post_url, headers=self.header)
        return posts_json.json()

    def __finish_scraping(self) -> List[Post]:
        """
        This method is used when posts scraping process has been finished.
        :return: a list with scraped Post objects.
        """
        self.logger.message(f'Done scraping posts! Scraped {len(self.posts)} items.')
        return self.posts

"""
The main (initial) script of the XY Adviser scraping tool. The tool scrapes posts, their comments/replies. It scrapes
several fields with data (author, content, date, etc.). The tool needs a user's credentials to scrape data. A user also
must set range of post IDs to scrape. The tool uses Selenium library and chromedriver. Results are saved to CSV files.
"""

import datetime

from source.data_saver import save_data
from source.entities.xy_user import XYUser
from source.logger import Logger
from source.scrapers.comment_scraper import CommentScraper
from source.scrapers.post_scraper import PostScraper
from source.scrapers.reply_scraper import ReplyScraper
from source.settings import Settings
from source.useful_scripts import run_main_func, create_output_name, cookies_to_header

TOOL_NAME = 'XY Adviser scraper'
TOOL_VERSION = '2021-07-07 16:55 UTC+2'

LOG_FILE = 'outputs/xy_scraping.log'


def main(args: dict = None):
    logger.message('The tool has been launched!', dividing_line=True)

    # Logging to a user and getting the personal Feed ID.
    logger.message('Reading settings...')
    settings = Settings()
    test_settings = settings.get_test_settings(args)

    if test_settings is not None:
        settings = test_settings
    else:
        settings.read_from_file()
        settings.validate_dates()

    logger.message('Logging to a user...')
    xy_account = XYUser(email=settings.email, password=settings.password)
    xy_account.login()
    logger.message('Reading the personal Feed ID')
    xy_account.scrape_assign_space_id()
    header = cookies_to_header(xy_account.get_cookies())
    xy_account.webdriver.close()  # Don't need the webdriver anymore. Can close it.
    logger.done_message()

    # Scraping posts.
    logger.message('Start scraping posts ...')
    post_scraper = PostScraper(logger=logger, settings=settings, feed_id=xy_account.space_id, header=header)
    posts_scraped = post_scraper.scrape_pages(text_full_processing=settings.text_full_processing)
    logger.done_message()

    # Scraping comments.
    logger.message('Start scraping comments ...')
    comment_scraper = CommentScraper(logger=logger, posts=posts_scraped, feed_id=xy_account.space_id, header=header,
                                     settings=settings)
    comments_scraped = comment_scraper.scrape(text_full_processing=settings.text_full_processing)
    logger.done_message()

    # Scraping replies
    logger.message('Start scraping replies ...')
    replies_scraper = ReplyScraper(logger=logger, comments=comments_scraped, feed_id=xy_account.space_id, header=header,
                                   settings=settings)
    replies_scraped = replies_scraper.scrape(text_full_processing=settings.text_full_processing)
    logger.done_message()

    # Saving data to local files.
    logger.message('Saving output files...')
    save_data(posts_scraped, comments_scraped, replies_scraped)
    logger.done_message()
    logger.close()

    # Update local settings
    if len(posts_scraped) != 0:
        settings.start_id = posts_scraped[0].uri
        settings.write_to_file()


# Kind of a wrapper to the tool. run_main_func will print an error, if it occurs.
if __name__ == '__main__':
    current_date_time = datetime.datetime.now()  # date and time of launching the tool.
    date_authenticator = current_date_time.strftime("%Y.%m.%d_%H.%M.%S")
    # Changing a name of the log file.
    log_name = create_output_name(LOG_FILE, '_' + date_authenticator)
    logger = Logger(log_name)  # create a logger which will print data to console and write a log down to a local file.
    tool_information = TOOL_NAME + '. ' + TOOL_VERSION + '.'
    logger.message(tool_information)
    success = run_main_func(main_func=main, printing_function=logger.message)  # a wrapper to a main function.
    logger.close()
    if success is True:
        print('The the tool has successfully finished! Press any key + ENTER to close the window...')
    else:
        print("Unfortunately, the tool didn't manage to finish. Please send the log file to the developer to find "
              "out the issue.")

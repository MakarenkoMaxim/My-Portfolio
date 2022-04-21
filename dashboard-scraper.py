"""
This tool is meant to scrape XY adviser analytics page. The tool requires creds for authentication. It uses Selenium
and Chromedriver for automation.
"""
from datetime import datetime

from source.entities.xy_user import XYUser
from source.logger import Logger
from source.scrapers.member_analytics_scraper import MemberAnalyticsScraper
from source.scrapers.post_analytics_scraper import PostAnalyticsScraper
from source.settings import Settings
from source.useful_scripts import run_main_func, create_output_name

TOOL_NAME = 'XY Adviser dashboard scraper'
LOG_FILE = 'outputs/dasboard_analytics.log'
TOOL_VERSION = '11.05.2020 11:30 UTC+3'
SETTINGS_FILE = 'settings.json'
POSTS_OUTPUT = 'outputs/analytics_posts.csv'
MEMBERS_OUTPUT = 'outputs/analytics_members.csv'
HEADLESS = False  # Selenium browser window mode.


def main(args: dict = None):
    logger.message('The tool has started!')

    # Reading local settings from inputs.settings.json.
    logger.message('Reading settings...')
    settings = Settings()
    test_settings = settings.get_test_settings(args)

    if test_settings is not None:
        settings = test_settings
    else:
        settings.read_from_file()
        settings.validate_dates(analytics_scraping=True)

    posts_fname = create_output_name(POSTS_OUTPUT, '_' + date_authenticator)
    members_fname = create_output_name(MEMBERS_OUTPUT, '_' + date_authenticator)
    logger.done_message()

    # Logging to a user and getting the personal Feed ID.
    logger.message('Logging to a user...')
    xy_account = XYUser(email=settings.email, password=settings.password)
    xy_account.login()
    logger.message('Reading the personal Feed ID')
    xy_account.scrape_assign_space_id()
    logger.done_message()

    # Scraping posts analytics page.
    logger.message('Scraping posts analytics page...')
    post_scraper = PostAnalyticsScraper(user=xy_account)
    post_scraper.scrape_analytics(posts_fname, settings, logger)
    logger.done_message()

    # Scraping members analytics page.
    logger.message('Scraping member page...')
    member_scraper = MemberAnalyticsScraper(user=xy_account)
    member_scraper.scrape_analytics(members_fname, settings, logger)
    logger.done_message()


# Kind of a wrapper to the tool. run_main_func will print an error, if it occurs.
if __name__ == '__main__':
    current_date_time = datetime.now()  # date and time of launching the tool.
    date_authenticator = current_date_time.strftime("%d.%m.%Y_%H.%M.%S")
    # Changing a name of the log file.
    log_name = create_output_name(LOG_FILE, '_' + date_authenticator)
    logger = Logger(log_name)  # create a logger which will print data to console and write a log down to a local file.
    tool_information = TOOL_NAME + '. ' + TOOL_VERSION + '.'
    logger.message(tool_information)
    success = run_main_func(main_func=main, printing_function=logger.message)  # a wrapper to a main function.
    logger.close()
    if success is True:
        input('The the tool has successfully finished! Press any key + ENTER to close the window...')
    else:
        input("Unfortunately, the tool didn't manage to finish. Please send the log file to the developer to find"
              "out the issue. Press any key + ENTER to close the window...")

"""
This tool is meant to download XY adviser member list. The tool needs a user's credentials to scrape data.
It uses Selenium and Chromedriver for automation. Output member list is sent to your email.
"""

import datetime

from source.entities.xy_user import XYUser
from source.logger import Logger
from source.scrapers.member_list_scraper import MemberListScraper
from source.settings import Settings
from source.useful_scripts import run_main_func, create_output_name

TOOL_NAME = 'XY Adviser members loader'
TOOL_VERSION = '2021-05-07 13:00 UTC+2'

LOG_FILE = 'outputs/member_list_loading.log'


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
    xy_account = XYUser(email=settings.email, password=settings.password, headless_driver=True)
    xy_account.login()
    logger.message('Reading the personal Feed ID')
    xy_account.scrape_assign_space_id()
    logger.done_message()

    # Request member list
    member_list_scraper = MemberListScraper(user=xy_account, logger=logger)
    member_list_scraper.scrape()
    logger.done_message()
    xy_account.webdriver.close()


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

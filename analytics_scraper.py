from time import sleep

from source.data_saver import save_analytic_data
from source.entities.xy_user import XYUser
from source.logger import Logger
from source.settings import Settings
from source.useful_scripts import cookies_to_header

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) " \
             "Chrome/89.0.4389.90 Safari/537.36"


class AnalyticsScraper:
    """
    This is a general class that contain methods for scraping.
    It is inherited by MemberAnalyticsScraper, PostAnalyticsScraper.
    """

    def __init__(self, user: XYUser):
        """
        Initializing main instance attributes.
        :param user: an object that contains user account and methods for getting cookies and finding out the space ID.
        """
        cookies = user.get_cookies()
        self.SPACE_ID = user.space_id
        self.HEADER = cookies_to_header(cookies, user_agent=USER_AGENT)

    def scrape_analytics(self, fname: str, settings: Settings, logger: Logger):
        """
        Scrape posts analytic data.
        :param fname: name of outfile with posts analytic data.
        :param settings: object with settings from the local settings.json.
        :param logger: a self.logger to log data to a local file and console.
        """
        logger.message('Start scraping Posts analytics page...')
        while True:
            try:
                items = self.get_analytics(settings.start_date, settings.end_date)
                save_analytic_data(fname=fname, items=items)
                break
            except:
                logger.message("Couldn't scrape items. Trying again in 5 seconds...")
                sleep(5)

    def scrape_analytics_bd(self, fname: str, settings: dict, logger: Logger):
        """
        Scrape posts analytic data.
        :param fname: name of outfile with posts analytic data.
        :param settings: object with settings from the local settings.json.
        :param logger: a self.logger to log data to a local file and console.
        """
        logger.message('Start scraping Posts analytics page...')
        while True:
            try:
                items = self.get_analytics(settings['analytic_range']['start_date'],
                                           settings['analytic_range']['end_date'])
                save_analytic_data(fname=fname, items=items)
                break
            except:
                logger.message("Couldn't scrape items. Trying again in 5 seconds...")
                sleep(5)

    def get_analytics(self, start_date: str, end_date: str):
        """
        Get processed analytic data.
        This method have to be overwrite in derivative class.
        """
        raise NotImplementedError("This method is not implemented yet in this class. Please, declare it.")

    @staticmethod
    def preparing_dates(start_date: str, end_date: str):
        """
        Process dates for using.
        :param start_date: start date of parsing range.
        :param end_date: end date of parsing range.
        :return: processed dates.
        """
        start_dates = start_date.split('/')
        end_dates = end_date.split('/')
        if len(start_dates[0]) == 1:
            start_dates[0] = '0' + start_dates[0]
        if len(end_dates[0]) == 1:
            end_dates[0] = '0' + end_dates[0]
        start_date = '-'.join(start_dates[::-1])
        end_date = '-'.join(end_dates[::-1])
        return start_date, end_date

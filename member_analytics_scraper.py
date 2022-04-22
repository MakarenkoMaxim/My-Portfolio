"""
This script contains class that is using for scraping members analytic data in dashboard-scraper tool.
"""

import requests

from source.scrapers.analytics_scraper import AnalyticsScraper

LOGIN_URL = 'https://www1.xyadviser.com/sign_in'
POSTS_URL = 'https://www1.xyadviser.com/analytics/posts'
ANALYTICS_URL = "https://www1.xyadviser.com/api/web/v1/spaces/{space_id}/analytics/{tab}?page=1&per_page=100000" \
                "&start_at={start_date}T00%3A00%3A00.000Z&end_at={end_date}T23%3A59%3A59.999Z&sort_order=desc"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) " \
             "Chrome/89.0.4389.90 Safari/537.36"


class MemberAnalyticsScraper(AnalyticsScraper):
    """
    A scraper for members analytic data.
    """

    def get_analytics(self, start_date, end_date) -> list:
        """
        Process members in set range.
        :param start_date: start date of parsing range.
        :param end_date: end date of parsing range.
        :return: processed posts as a list of dictionaries.
        """
        start_date, end_date = self.preparing_dates(start_date, end_date)
        members_url = ANALYTICS_URL.format(space_id=self.SPACE_ID, tab="members", start_date=start_date,
                                           end_date=end_date)
        response = requests.get(url=members_url, headers=self.HEADER)
        response = response.json()
        members = []
        for item in response:
            curr_dict = dict()
            curr_dict['start_date'] = start_date
            curr_dict['end_date'] = start_date
            curr_dict['member_id'] = item['user']['id']
            curr_dict['visits'] = item['session_count']
            curr_dict['new_followers'] = item['follower_count']
            curr_dict['engagement'] = str(int(item['engagement']))
            curr_dict['posts'] = item['post_count']
            curr_dict['messages_sent'] = item['message_count']
            members.append(curr_dict)

        return members

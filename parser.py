from source.scraper import Scraper
from source.analyzer import Analyzer
from config import SYMBOLS


def collect_data(test_mode=True):
    scraper_obj = Scraper(print_opt=False, test_mode=test_mode)
    scraper_obj.parse_common()

    for s in SYMBOLS:
        print("-" * 30, s, "-" * 30)
        scraper_obj.set_symbol(s)
        scraper_obj.parse_coin_data()

        info = scraper_obj.info
        print(f"(finished scraping)")

        analyzer_obj = Analyzer(info, test_mode=test_mode)
        analyzer_obj.analyse()
        analyzer_obj.serialize()
        print(f"(finished analysis)")
        print("-" * 61, "\n")


def update_datafiles(test_mode=True):
    scraper_obj = Scraper(print_opt=False, test_mode=test_mode)
    analyzer_obj = Analyzer(info=scraper_obj.info, test_mode=test_mode)

    data = analyzer_obj.deserialize()
    for item in data:
        analyzer_obj.update_datafile(item, scraper_obj)


collect_data(test_mode=False)
update_datafiles(test_mode=False)

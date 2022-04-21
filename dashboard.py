import numpy as np
from source.scraper import Scraper
from source.analyzer import Analyzer
from config import current_symbol


class Dashboard:

    def __init__(self, symbol, test_mode):
        print(f"\n\nDashboard Launched (SYMBOL SET UP AS {symbol})\n")
        self.test_mode = test_mode
        self.scraper_obj = Scraper(symbol=symbol, print_opt=False, test_mode=test_mode)

    def scrape(self):
        self.scraper_obj.parse_common()
        self.scraper_obj.parse_coin_data()
        self.scraper_obj.show_order_book()
        print("\n\n")

    def key_info(self):
        analyzer_obj = Analyzer(self.scraper_obj.info, test_mode=self.test_mode)
        analyzer_obj.analyse()

        ex = "Neutral"
        if analyzer_obj.conclusion["expectation"] < -0.5:
            ex = "Abnormal Negative"
        elif analyzer_obj.conclusion["expectation"] > 0.5:
            ex = "Abnormal Positive"
        elif analyzer_obj.conclusion["expectation"] > 0.1:
            ex = "Positive"
        elif analyzer_obj.conclusion["expectation"] < -0.1:
            ex = "Negative"

        print("EXPECTATION: ", analyzer_obj.conclusion["expectation"], f" ({ex})\n")

        vly = "Normal"
        if analyzer_obj.conclusion["volatility_index"] > 2:
            vly = "High"
        elif analyzer_obj.conclusion["volatility_index"] > 1:
            vly = "Low"

        print("VOLATILITY: ", analyzer_obj.conclusion["volatility_index"], f" ({vly})\n")

        vlm = "Normal"
        if analyzer_obj.conclusion["volume_index"] < 0.8:
            vlm = "Abnormal Reduced"
        elif analyzer_obj.conclusion["volume_index"] < 0.7:
            vlm = "Reduced"

        print("VOLUME: ", analyzer_obj.conclusion["volume_index"], f" ({vlm})\n")

        print("DIFFERENCE (24h)", analyzer_obj.info.diff_24h * 100, "%")
        print("LOW (24h)", analyzer_obj.info.low_24h * 100, "%")
        print("HIGH (24h)", analyzer_obj.info.high_24h * 100, "%\n")

        if analyzer_obj.info.first_extremum:
            print("first day extremum reached - HIGH\n")
        else:
            print("first day extremum reached - LOW\n")

        local_levels = analyzer_obj.define_levels(6, 20)
        global_levels = analyzer_obj.define_levels(3, 10)

        levels = [['(-L) local ', local_levels], ['(-G) global ', global_levels]]

        for group in levels:
            group_levels = [['resistance level ', group[1][0]], ['support level ', group[1][1]]]
            for subgroup in group_levels:
                for level in subgroup[1]:
                    print(group[0] + subgroup[0] + str(level) + " USDT")
                print()
            print("\n")

        self.scraper_obj.show_historical_quotes(np.concatenate((local_levels, global_levels), axis=None), (12, 6))


dashboard_obj = Dashboard(current_symbol, False)

while True:
    dashboard_obj.scrape()
    dashboard_obj.key_info()

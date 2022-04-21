import time

from source.scraper import Scraper
from source.analyzer import Analyzer
from source.analyzer import get_date_time

from binance.client import Client
from binance.enums import *
from config import api_key, secret_key

import numpy as np
from config import current_symbol


class Bot:
    def __init__(self, symbol, test_mode):
        self.client = Client(api_key, secret_key)

        self.test_mode = test_mode
        self.symbol = symbol

        self.scraper_obj = Scraper(symbol=symbol, print_opt=False, test_mode=test_mode)

        self.scraper_obj.parse_common()
        self.scraper_obj.parse_coin_data()

        print("[INFO] from Bot.__init__: scraping finished")

        self.analyzer_obj = Analyzer(self.scraper_obj.info, test_mode=self.test_mode)
        self.analyzer_obj.analyse()

        print("[INFO] from Bot.__init__: analyse finished")

        self.deal = 0.0

        self.target = 0.01
        self.stop = 0.01

        self.quantity = 10

        self.expectation_coefficient = 2500
        self.diff_24h_coefficient = 1000
        self.low_24h_coefficient = 2000
        self.high_24h_coefficient = 2000

        self.ann_coefficient = 3000

    @staticmethod
    def get_last_ann_signal():
        with open("prediction_reports.txt", mode="r") as file:
            result = file.read()
            result = result.split('\n')[-2]
            return float(result.split(';')[0])

    def prepare_deal(self):

        print("[INFO] from Bot.prepare_deal: start preparing")

        self.deal += pow(self.analyzer_obj.conclusion["expectation"], 3) * self.expectation_coefficient
        self.deal += pow(self.analyzer_obj.info.diff_24h, 3) * 1000 * self.diff_24h_coefficient
        self.deal += pow(self.analyzer_obj.info.low_24h, 3) * 1000 * self.low_24h_coefficient
        self.deal += pow(self.analyzer_obj.info.high_24h, 3) * 1000 * self.high_24h_coefficient
        self.deal += self.get_last_ann_signal() * self.ann_coefficient

    def get_account(self):
        info = self.client.get_account()
        balance = info["balances"]
        for currency in balance:
            if float(currency["free"]) > 0:
                print(currency)

    def come_in_deal(self):
        if self.deal == 0:
            return
        elif self.deal > 0:
            side = SIDE_BUY
            close_side = SIDE_SELL
        else:
            side = SIDE_SELL
            close_side = SIDE_BUY

        exchange_info = self.client.futures_exchange_info()
        precision = 1

        for i in exchange_info['symbols']:
            if i['symbol'] == self.symbol:
                precision = i['quantityPrecision']
                break

        usd_quantity = 15
        quantity = np.round(usd_quantity / self.scraper_obj.info.course, precision)

        if quantity == 0:
            quantity = 1 / pow(10, precision)

        if side == SIDE_BUY:
            stop_price = np.round(self.scraper_obj.info.course * (1 - self.stop), precision)
            target_price = np.round(self.scraper_obj.info.course * (1 + self.target), precision)
        else:
            stop_price = np.round(self.scraper_obj.info.course * (1 + self.stop), precision)
            target_price = np.round(self.scraper_obj.info.course * (1 - self.target), precision)

        info = f"{self.symbol};{quantity};{stop_price};{target_price};{get_date_time()}\n"
        print(info)

        print(f"side: {side}")
        print(f"deal: {self.deal}")
        print(f"quantity: {quantity}")
        print(f"stop price: {stop_price}")
        print(f"target price: {target_price}")

        with open("deal_reports.txt", mode="a") as file:
            file.write(info)

        # main order to come in deal
        self.client.futures_create_order(
            symbol=self.symbol,
            side=side,
            type=ORDER_TYPE_MARKET,
            quantity=quantity,
        )

        print("\nTHE MAIN ORDER CREATED\n")
        time.sleep(2)
        precision_st = precision
        precision_tp = precision

        while True:
            try:

                # stop loss order
                self.client.futures_create_order(
                    symbol=self.symbol,
                    side=close_side,
                    type=FUTURE_ORDER_TYPE_STOP_MARKET,
                    quantity=quantity,
                    stopPrice=stop_price
                )
                break


            except Exception as ex_:

                print(ex_)

                if precision_st < 1:
                    break
                precision_st -= 1
                if side == SIDE_BUY:
                    stop_price = np.round(self.scraper_obj.info.course * (1 - self.stop), precision_st)
                else:
                    stop_price = np.round(self.scraper_obj.info.course * (1 + self.stop), precision_st)

        print("\nTHE STOP LOSS ORDER CREATED\n")
        time.sleep(2)

        while True:
            try:
                # take profit order
                self.client.futures_create_order(
                    symbol=self.symbol,
                    side=close_side,
                    type=FUTURE_ORDER_TYPE_LIMIT,
                    timeInForce=TIME_IN_FORCE_GTC,
                    quantity=quantity,
                    price=target_price
                )
                break

            except Exception as ex_:

                print(ex_)

                if precision_tp < 1:
                    break
                precision_tp -= 1

                if side == SIDE_BUY:
                    target_price = np.round(self.scraper_obj.info.course * (1 + self.target), precision_tp)
                else:
                    target_price = np.round(self.scraper_obj.info.course * (1 - self.target), precision_tp)

        print("\nTHE CLOSE ORDER CREATED\n")

bot_obj = Bot(current_symbol, True)
bot_obj.prepare_deal()

print(bot_obj.deal)

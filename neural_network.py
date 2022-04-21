import datetime

import numpy as np
from numpy import array, zeros
from numpy import expand_dims
from matplotlib import pyplot as plt
from source.analyzer import Analyzer
from source.scraper import Scraper
from source.import_file import keras
from config import model_repository_path


class NeuralNetwork:
    def __init__(self, ticker, mode, model_struct, time_frame, limitation_ps=1, limitation_pr=60, show_plots=False,
                 test_mode=False):

        self.show_plots = show_plots

        self.x, self.y, self.cri = self.extract_sample(ticker, time_frame, mode, limitation_ps=limitation_ps,
                                                       limitation_pr=limitation_pr, test_mode=test_mode)
        self.ticker = ticker
        self.mode = mode

        self.prediction = None
        self.normal_output = None

        act_f = keras.activations.tanh

        if mode != 'full':
            input_shape = 20
        else:
            input_shape = 123

        if model_struct == 1:
            self.model = keras.Sequential([
                keras.layers.Dense(units=600, input_shape=(input_shape,), activation=act_f),
                keras.layers.Dense(units=900, activation=act_f),
                keras.layers.Dense(units=700, activation=act_f),
                keras.layers.Dense(units=500, activation=act_f),
                keras.layers.Dense(units=400, activation=act_f),
                keras.layers.Dense(units=300, activation=act_f),
                keras.layers.Dense(units=200, activation=act_f),
                keras.layers.Dense(units=100, activation=act_f),
                keras.layers.Dense(units=80, activation=act_f),
                keras.layers.Dense(units=60, activation=act_f),
                keras.layers.Dense(units=30, activation=act_f),
                keras.layers.Dense(units=4, activation=act_f)
            ])

            self.model.compile(
                optimizer=keras.optimizers.Adam(0.000000025),
                loss='mae',
                metrics=['mape']
            )

        elif model_struct == 2:
            self.model = keras.Sequential([
                keras.layers.Dense(units=800, input_shape=(input_shape,), activation=act_f),
                keras.layers.Dense(units=1200, activation=act_f),
                keras.layers.Dense(units=1000, activation=act_f),
                keras.layers.Dense(units=900, activation=act_f),
                keras.layers.Dense(units=800, activation=act_f),
                keras.layers.Dense(units=700, activation=act_f),
                keras.layers.Dense(units=500, activation=act_f),
                keras.layers.Dense(units=300, activation=act_f),
                keras.layers.Dense(units=150, activation=act_f),
                keras.layers.Dense(units=70, activation=act_f),
                keras.layers.Dense(units=30, activation=act_f),
                keras.layers.Dense(units=4, activation=act_f)
            ])

            self.model.compile(
                optimizer=keras.optimizers.SGD(0.00075),
                loss='mse',
                metrics=['mape']
            )

        elif model_struct == 3:

            self.model = keras.Sequential([
                keras.layers.Dense(units=3000, input_shape=(input_shape,), activation=act_f),
                keras.layers.Dense(units=2800, activation=act_f),
                keras.layers.Dense(units=2500, activation=act_f),
                keras.layers.Dense(units=2200, activation=act_f),
                keras.layers.Dense(units=1800, activation=act_f),
                keras.layers.Dense(units=1500, activation=act_f),
                keras.layers.Dense(units=1200, activation=act_f),
                keras.layers.Dense(units=1000, activation=act_f),
                keras.layers.Dense(units=800, activation=act_f),
                keras.layers.Dense(units=600, activation=act_f),
                keras.layers.Dense(units=400, activation=act_f),
                keras.layers.Dense(units=200, activation=act_f),
                keras.layers.Dense(units=100, activation=act_f),
                keras.layers.Dense(units=50, activation=act_f),
                keras.layers.Dense(units=4, activation=act_f)
            ])

            self.model.compile(
                optimizer=keras.optimizers.Adam(0.0000007),
                loss='huber',
                metrics=['mape']
            )

        elif model_struct == 4:

            self.model = keras.Sequential([
                keras.layers.Dense(units=2100, input_shape=(input_shape,), activation=act_f),
                keras.layers.Dense(units=1800, activation=act_f),
                keras.layers.Dense(units=1500, activation=act_f),
                keras.layers.Dense(units=1200, activation=act_f),
                keras.layers.Dense(units=800, activation=act_f),
                keras.layers.Dense(units=500, activation=act_f),
                keras.layers.Dense(units=400, activation=act_f),
                keras.layers.Dense(units=300, activation=act_f),
                keras.layers.Dense(units=250, activation=act_f),
                keras.layers.Dense(units=200, activation=act_f),
                keras.layers.Dense(units=150, activation=act_f),
                keras.layers.Dense(units=100, activation=act_f),
                keras.layers.Dense(units=50, activation=act_f),
                keras.layers.Dense(units=30, activation=act_f),
                keras.layers.Dense(units=4, activation=act_f)
            ])

            self.model.compile(
                optimizer=keras.optimizers.Adam(0.0000000175),
                loss='mse',
                metrics=['mape']
            )

        elif model_struct == 5:
            act_f_s = keras.activations.relu
            act_f_m = keras.activations.selu
            act_f_f = keras.activations.tanh
            self.model = keras.Sequential([
                keras.layers.Dense(units=2000, input_shape=(input_shape,), activation=act_f_s),
                keras.layers.Dense(units=1800, activation=act_f_s),
                keras.layers.Dense(units=1600, activation=act_f_s),
                keras.layers.Dense(units=1400, activation=act_f_s),
                keras.layers.Dense(units=1200, activation=act_f_s),
                keras.layers.Dense(units=1000, activation=act_f_s),
                keras.layers.Dense(units=800, activation=act_f_s),
                keras.layers.Dense(units=600, activation=act_f_s),
                keras.layers.Dense(units=400, activation=act_f_s),
                keras.layers.Dense(units=200, activation=act_f_s),
                keras.layers.Dense(units=200, activation=act_f_m),
                keras.layers.Dense(units=200, activation=act_f_m),
                keras.layers.Dense(units=200, activation=act_f_m),
                keras.layers.Dense(units=200, activation=act_f_m),
                keras.layers.Dense(units=200, activation=act_f_m),
                keras.layers.Dense(units=200, activation=act_f_m),
                keras.layers.Dense(units=200, activation=act_f_m),
                keras.layers.Dense(units=200, activation=act_f_m),
                keras.layers.Dense(units=200, activation=act_f_m),
                keras.layers.Dense(units=200, activation=act_f_m),
                keras.layers.Dense(units=128, activation=act_f_f),
                keras.layers.Dense(units=64, activation=act_f_f),
                keras.layers.Dense(units=32, activation=act_f_f),
                keras.layers.Dense(units=16, activation=act_f_f),
                keras.layers.Dense(units=8, activation=act_f_f),
                keras.layers.Dense(units=4, activation=act_f_f),
            ])

            self.model.compile(
                optimizer=keras.optimizers.Adam(0.00001),
                loss='huber',
                metrics=['mape']
            )

    @staticmethod
    def extract_sample(ticker, time_frame, mode, limitation_ps, limitation_pr, test_mode=False):
        analyzer_obj = Analyzer(test_mode=test_mode)

        des = analyzer_obj.deserialize()
        data = []

        if ticker != 'all':
            for item in des:
                if item['Information']['Ticker'] == ticker:
                    data.append(item)

            indexes = []
            sorted_data = []

            for item in data:
                test = 0
                if 'test' in item['Information']['Datafile_index']:
                    test = 1
                dfx = item['Information']['Datafile_index'].split('.')
                indexes.append(int(dfx[0 + test]) * 365 + int(dfx[1 + test]))

            min_idx = min(indexes)

            for i in range(len(data) + 1):
                try:
                    idx = indexes.index(min_idx + i)
                except ValueError:
                    continue
                sorted_data.append(data[idx])
        else:
            sorted_data = data

        if mode == 'base':
            path = 'Model_input_base'
        else:
            path = "Model_input_full"

        input_values = []
        output_values = []
        current_input = sorted_data[-1][path]
        for item in sorted_data:
            if item['Result'][time_frame] is not None:
                input_values.append(item[path])
                output_values.append(item['Result'][time_frame])

        input_values, output_values, current_input = array(input_values), array(output_values, dtype='float64'), array(
            current_input, dtype='float64')

        if limitation_ps < len(input_values):
            input_values = input_values[len(input_values) - limitation_pr:]
            output_values = output_values[len(output_values) - limitation_pr:]

        if limitation_ps > 1:
            current_input = input_values[-limitation_ps]
            input_values = input_values[0:-limitation_ps]
            output_values = output_values[0:-limitation_ps]

        return input_values, output_values, current_input

    def fit(self, epochs, validation_split=0.2):
        hist = self.model.fit(self.x, self.y, epochs=epochs, validation_split=validation_split).history

        if self.show_plots:
            if 'val_mape' in hist:
                plt.plot(hist['val_mape'], 'g--')
            plt.plot(np.log(hist['mape']), 'b')
            plt.show()

        if validation_split != 0:
            return hist['val_mape'][-1]
        else:
            return hist['mape'][-1]

    def save_model(self):
        self.model.save(model_repository_path + str(datetime.datetime.now().date()))

    def load_model(self, name):
        self.model = keras.models.load_model(model_repository_path + name)

    def fit_special(self, min_ep=20, max_ep=2000, block=40, target=None, validation_split=0.2):

        hist = self.model.fit(self.x, self.y, epochs=3 * block + 1, validation_split=validation_split).history

        for i in range(100):
            if i * block > max_ep:
                break

            no_target_reached = (target is not None and hist['val_mape'][-1] > target)

            no_min_epochs_done = (target is None and len(hist['mape']) < min_ep)
            no_samples_divergence = (no_min_epochs_done and (
                    hist['val_mape'][-1] < hist['val_mape'][-(2 * block)]) and (
                                             hist['mape'][-1] < hist['mape'][-(2 * block)]))

            if no_target_reached or no_min_epochs_done or no_samples_divergence:
                next_epoch = self.model.fit(self.x, self.y, epochs=block, validation_split=validation_split).history
                hist['val_mape'] += next_epoch['val_mape']
                hist['mape'] += next_epoch['mape']

        if self.show_plots:
            if 'val_mape' in hist:
                plt.plot(hist['val_mape'], 'g--')
            plt.plot(hist['mape'], 'b')
            plt.show()

        if validation_split != 0:
            return hist['val_mape'][-1]
        else:
            return hist['mape'][-1]

    def predict(self, model_input=None):
        if model_input is None:
            model_input = self.cri
        self.prediction = self.model.predict(expand_dims(model_input, axis=0))[0]

        if self.prediction[2] > self.prediction[0] > self.prediction[1]:
            self.normal_output = True
        else:
            self.normal_output = False
            sorted_pr = np.sort(self.prediction[:-1])
            self.prediction = [sorted_pr[1], sorted_pr[0], sorted_pr[2], self.prediction[-1]]

        return self.prediction

    def get_signal(self, test_mode):

        if self.ticker == 'all':
            self.ticker = "BTC"

        if self.prediction[0] > 0:
            signal = 1
        else:
            signal = -1

        print(f" [INFO] PREDICTION [TOTAL] {self.prediction[0] * 100} %")
        print(f" [INFO] PREDICTION [MIN] {self.prediction[1] * 100} %")
        print(f" [INFO] PREDICTION [MAX] {self.prediction[2] * 100} %")
        print(f" [INFO] PREDICTION [FIRST-EXTREMUM] {self.prediction[3]}\n\n")

        analyzer_obj = Analyzer(test_mode=test_mode)
        data = analyzer_obj.deserialize()

        necessary_data = []

        for item in data:
            if item['Information']['Ticker'] == self.ticker:
                necessary_data.append(item)

        last_item = necessary_data[-1]['Conclusion']

        if last_item['RSI'] > 60 and last_item['CCI20'] > 90 and signal < 0:
            signal -= 1
        elif last_item['RSI'] < 40 and last_item['CCI20'] < -90 and signal > 0:
            signal += 1

        if last_item['RSI'] > 60 and last_item['Stoch.K'] > 70 and signal < 0:
            signal -= 1
        elif last_item['RSI'] < 40 and last_item['Stoch.K'] < 30 and signal > 0:
            signal += 1

        if last_item['Mom'] > 0 and last_item['MACD.macd'] > 0 and -signal > 0:
            signal -= 1
        elif last_item['Mom'] < 0 and last_item['MACD.macd'] < 0 and -signal < 0:
            signal += 1

        if last_item['P.SAR'] > 1 and last_item['HullMA9'] > 1 and signal < 0:
            signal -= 1
        elif last_item['P.SAR'] < 1 and last_item['HullMA9'] < 1 and signal > 0:
            signal += 1

        if last_item['BB.upper'] > 1 and last_item['Ichimoku.BLine'] > 1 and signal < 0:
            signal -= 1
        elif last_item['BB.lower'] < 1 and last_item['Ichimoku.BLine'] < 1 and signal > 0:
            signal += 1

        if last_item["expectation"] < 0 and signal < 0:
            signal -= 1
        elif last_item["expectation"] > 0 and signal > 0:
            signal += 1

        if last_item["tw_summary"] < 0 and signal < 0:
            signal -= 1
        elif last_item["tw_summary"] > 0 and signal > 0:
            signal += 1

        scraper_obj = Scraper(test_mode=test_mode)
        scraper_obj.parse_course(symbol=self.ticker + "USDT")

        if self.prediction[3] > 0.5:
            print(f"\n\n [INFO] RECOMMENDATION [SHORT] FROM {scraper_obj.info.course * (1 + self.prediction[2])}")
            print(f" [INFO] WITH TARGET {scraper_obj.info.course * (1 + self.prediction[1])}")
        else:
            print(f" [INFO] RECOMMENDATION [LONG] FROM {scraper_obj.info.course * (1 + self.prediction[1])}")
            print(f" [INFO] WITH TARGET {scraper_obj.info.course * (1 + self.prediction[2])}\n\n")

        if signal >= 3 and self.prediction[0] > 0.03:
            return "confirmed signal (POSITIVE)", signal
        elif signal <= -3 and self.prediction[0] < -0.03:
            return "confirmed signal (NEGATIVE)", signal
        elif signal >= 2:
            return "little confirmed signal (POSITIVE)", signal
        elif signal <= -2:
            return "little confirmed signal (NEGATIVE)", signal
        else:
            return "too weak signal (or signal didn't confirm)", signal

    def show_fit_results(self):
        length = len(self.y)

        plt.plot([100 * i[0] for i in self.y], "b")
        plt.plot(zeros(length), 'b--')

        for i in range(length):
            self.predict(self.x[i])

            if self.prediction[0] > 0:
                color = "green"
            else:
                color = "red"

            plt.scatter(i, 100 * self.prediction[0], color=color)

        plt.scatter(length, 100 * self.predict()[0], color="orange")
        plt.plot(zeros(length) + (100 * self.prediction[2]), 'g--')
        plt.plot(zeros(length) + (100 * self.prediction[1]), 'r--')
        plt.show()

import numpy as np
from datetime import datetime
from source.analyzer import get_date_time
from source.neural_network import NeuralNetwork
from config import current_symbol

EPOCHS = 4500
LIMITATION = 30


def write_prediction_report(signal_to_report, epochs_num_used, limitation_used):
    with open("prediction_reports.txt", mode="a") as file:
        file.write(f"{signal_to_report};{epochs_num_used};{limitation_used};{get_date_time()}\n")


def fit(time_frame, test_mode):
    model = NeuralNetwork(ticker=current_symbol.replace("USDT", ""), mode="full", model_struct=3, time_frame=time_frame,
                          limitation_ps=1, limitation_pr=LIMITATION, show_plots=False, test_mode=test_mode)
    model.fit(EPOCHS, 0)
    print("\n", model.predict(), "\n")
    model.show_fit_results()
    return model


time_start = datetime.now()

result = fit(time_frame='Difference_1D', test_mode=False)
signal, strength = result.get_signal(test_mode=False)

print(f"{signal} ({strength})")
write_prediction_report(np.round(result.prediction[0], 4), EPOCHS, LIMITATION)

time_finish = datetime.now()

execution_time = time_finish - time_start
print(f"execution time: {execution_time} (s)")

import pickle
import pandas as pd
import numpy as np

def load_model():
    with open('xgboost_model_amz_right.pkl', 'rb') as file:
        model = pickle.load(file)
    return model

def preprocess_data(data, window_size=5):
    df = pd.read_csv(data)
    close_prices = df['Close'].values[-window_size:]
    return np.array(close_prices)


def predict_future(data, num_predictions=20, window_size=5):
    model = load_model()
    current_values = preprocess_data(data, window_size)

    predictions = []

    for _ in range(num_predictions):
        next_value = model.predict(current_values.reshape(1, -1))
        predictions.append(float(next_value[0]))
        current_values = np.roll(current_values, -1)
        current_values[-1] = next_value[0]
    return predictions



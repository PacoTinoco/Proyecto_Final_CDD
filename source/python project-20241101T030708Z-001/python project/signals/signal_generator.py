# signal_generator.py
import pandas as pd


def generate_fake_data():
    # Simulación de datos históricos falsos
    data = {
        'Open': [1.1000, 1.1010, 1.0995, 1.1020],
        'Close': [1.1020, 1.1005, 1.1010, 1.1000],
        'High': [1.1030, 1.1025, 1.1015, 1.1035],
        'Low': [1.0990, 1.0985, 1.0990, 1.0975],
    }
    return pd.DataFrame(data)


def signal_generator(df):
    open_price = df['Open'].iloc[-1]
    close_price = df['Close'].iloc[-1]
    previous_open = df['Open'].iloc[-2]
    previous_close = df['Close'].iloc[-2]

    # Patrón bajista
    if open_price > close_price and previous_open < previous_close and close_price < previous_open:
        return "Vender"

    # Patrón alcista
    elif open_price < close_price and previous_open > previous_close and close_price > previous_open:
        return "Comprar"

    # Ningún patrón claro
    return "Mantener"

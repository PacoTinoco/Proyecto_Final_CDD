import yfinance as yf
import pandas as pd
import xgboost as xgb
import numpy as np
from sklearn.metrics import mean_squared_error, mean_absolute_error
import math


def train_stock_model(stock_data, window_size=5):
    """
    Entrena el modelo XGBoost con los datos históricos.

    Args:
        stock_data (array-like): Array de precios históricos de cierre
        window_size (int): Tamaño de la ventana de datos para predicción

    Returns:
        model: Modelo XGBoost entrenado
    """
    # Crear las ventanas deslizantes (X) y los valores objetivo (y)
    X = []
    y = []

    prices = np.array(stock_data).flatten()

    for i in range(len(prices) - window_size):
        window = prices[i:(i + window_size)]
        target = prices[i + window_size]
        X.append(window)
        y.append(target)

    X = np.array(X)
    y = np.array(y)

    # Convertir a DataFrame y Serie
    X_train = pd.DataFrame(X, columns=[f'day_{i + 1}' for i in range(window_size)])
    y_train = pd.Series(y, name='target')

    # Entrenar el modelo
    model = xgb.XGBRegressor(
        n_estimators=100,
        learning_rate=0.1,
        max_depth=5,
        random_state=42
    )
    model.fit(X_train, y_train)

    return model


def predict_future_prices(model, last_known_prices, n_days=20, window_size=5):
    """
    Predice precios futuros basándose en los últimos precios conocidos.

    Args:
        model: Modelo XGBoost entrenado
        last_known_prices (array-like): Últimos precios conocidos (al menos window_size elementos)
        n_days (int): Número de días futuros para predecir
        window_size (int): Tamaño de la ventana utilizada en el entrenamiento

    Returns:
        DataFrame con las predicciones y fechas
    """
    # Asegurarse de que tenemos suficientes precios iniciales
    if len(last_known_prices) < window_size:
        raise ValueError(f"Se necesitan al menos {window_size} precios para hacer predicciones")

    # Convertir a numpy array y tomar los últimos window_size elementos
    current_window = np.array(last_known_prices[-window_size:])
    predictions = []

    # Generar predicciones para los próximos n_days
    for _ in range(n_days):
        # Reshape para la predicción
        window_reshaped = current_window.reshape(1, -1)

        # Hacer la predicción
        next_pred = model.predict(window_reshaped)[0]
        predictions.append(next_pred)

        # Actualizar la ventana para la siguiente predicción
        current_window = np.roll(current_window, -1)
        current_window[-1] = next_pred

    # Crear DataFrame con los resultados
    future_dates = pd.date_range(start=pd.Timestamp.today(), periods=n_days)
    predictions_df = pd.DataFrame({
        'Fecha': future_dates,
        'Precio_Predicho': predictions,
        'Cambio_Porcentual': [np.nan] + [
            ((predictions[i] - predictions[i - 1]) / predictions[i - 1] * 100)
            for i in range(1, len(predictions))
        ]
    })

    return predictions_df


# Ejemplo de uso
if __name__ == "__main__":
    # Descargar datos históricos
    stock_data = yf.download('GOOGL', start='2020-01-01', end='2024-01-01')['Close']
    input_data_amz = 'C:/Users/almen/Documents/dev/samsara/pythonProject/app/tmp/GOOGL_yfinance_daily_2023-11-03_to_2024-11-02.csv'
    df_data = pd.read_csv(input_data_amz)
    df_data_real = df_data['Close']

    # Entrenar el modelo
    model = train_stock_model(stock_data)

    # Obtener predicciones para los próximos 20 días
    last_known_prices = df_data_real.values[-10:]  # Últimos 10 precios conocidos
    predictions = predict_future_prices(model, last_known_prices, n_days=20)

    # Mostrar resultados
    print("\nPredicciones para los próximos 20 días:")
    print(predictions.to_string(index=False))

    # Mostrar estadísticas
    print("\nEstadísticas de las predicciones:")
    print(f"Precio inicial: ${predictions['Precio_Predicho'].iloc[0]:.2f}")
    print(f"Precio final: ${predictions['Precio_Predicho'].iloc[-1]:.2f}")
    print(
        f"Cambio total: {((predictions['Precio_Predicho'].iloc[-1] / predictions['Precio_Predicho'].iloc[0] - 1) * 100):.2f}%")
    print(f"Precio máximo: ${predictions['Precio_Predicho'].max():.2f}")
    print(f"Precio mínimo: ${predictions['Precio_Predicho'].min():.2f}")

    import joblib
    joblib.dump(model, 'xgboost_model_googl_right.pkl')
    print("Modelo guardado como 'xgboost_model_googl_right.pkl'")
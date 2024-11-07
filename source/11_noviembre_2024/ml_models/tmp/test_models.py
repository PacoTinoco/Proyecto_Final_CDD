import pandas as pd
from pythonProject.ml_models.ml_model_api_amazon import predict_future as predict_amz
from pythonProject.ml_models.ml_model_api_google import predict_future as predict_googl

# Rutas a los archivos CSV
input_data_amz = 'C:/Users/almen/Documents/dev/samsara/pythonProject/app/tmp/AMZN_yfinance_daily_2023-11-03_to_2024-11-02.csv'

# Hacer la predicción para Amazon
predictions_amz = predict_googl(input_data_amz)
print("Predicciones para Amazon:", predictions_amz)

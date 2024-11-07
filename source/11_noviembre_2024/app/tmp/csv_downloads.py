import yfinance as yf
from datetime import datetime, timedelta

# Define el símbolo de las acciones
tickers = ['AMZN', 'GOOGL']

# Calcula la fecha de finalización (hoy)
end_date = datetime.now()  # Usa la fecha actual
# Calcula la fecha de inicio (hace un año)
start_date = end_date - timedelta(days=365)

# Formatea las fechas como cadenas
start_date_str = start_date.strftime('%Y-%m-%d')
end_date_str = end_date.strftime('%Y-%m-%d')

# Descargar los datos en intervalos diarios
data = yf.download(
    tickers=tickers,
    start=start_date_str,
    end=end_date_str,
    interval="1d",  # Intervalo diario
    group_by="ticker"
)

# Guardar los datos de cada ticker en un archivo CSV
for ticker in tickers:
    if ticker in data:
        data[ticker].to_csv(f'{ticker}_yfinance_daily_{start_date_str}_to_{end_date_str}.csv')
    else:
        print(f"No hay datos disponibles para {ticker} en este rango de fechas.")

print("Datos descargados y guardados en archivos CSV.")

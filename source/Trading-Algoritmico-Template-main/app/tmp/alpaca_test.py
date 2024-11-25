import requests
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

API_KEY = "AKUT67Y6X42H2ZO5L1EV"
SECRET_KEY = "LensZPkzWeHQ0cwDCcnJZcUDJhLvWasrk05qVbmC"
BASE_URL = "https://api.alpaca.markets"

trading_client = TradingClient(API_KEY,SECRET_KEY,paper=True)
url = "https://paper-api.alpaca.markets/v2/account"

headers = {
    "accept": "application/json",
    "APCA-API-KEY-ID": API_KEY,
    "APCA-API-SECRET-KEY": SECRET_KEY
}

response = requests.get(BASE_URL, headers=headers)
print(response.text)
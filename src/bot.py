from binance.client import Client
from src.config import API_KEY, SECRET_KEY, SYMBOL

def get_client():
    return Client(API_KEY, SECRET_KEY)

def get_btc_price():
    client = get_client()
    ticker = client.get_symbol_ticker(symbol=SYMBOL)
    return float(ticker["price"])

def get_balance():
    client = get_client()
    account = client.get_account()
    balances = {b["asset"]: float(b["free"]) for b in account["balances"] if float(b["free"]) > 0}
    return balances

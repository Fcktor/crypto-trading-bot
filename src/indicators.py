import pandas as pd
import pandas_ta as ta
from src.bot import get_client
from src.config import SYMBOL, RSI_PERIOD, RSI_INTERVAL

def get_candles(limit=100):
    client = get_client()
    raw = client.get_klines(symbol=SYMBOL, interval=RSI_INTERVAL, limit=limit)
    df = pd.DataFrame(raw, columns=[
        "timestamp", "open", "high", "low", "close", "volume",
        "close_time", "quote_volume", "trades",
        "taker_buy_base", "taker_buy_quote", "ignore"
    ])
    df["close"] = df["close"].astype(float)
    return df

def get_rsi():
    df = get_candles()
    rsi_series = ta.rsi(df["close"], length=RSI_PERIOD)
    return round(float(rsi_series.iloc[-1]), 2)

def get_moving_averages():
    df = get_candles()
    ma20 = ta.sma(df["close"], length=20).iloc[-1]
    ma50 = ta.sma(df["close"], length=50).iloc[-1]
    return round(float(ma20), 2), round(float(ma50), 2)

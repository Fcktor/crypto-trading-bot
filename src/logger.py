import json
import os
from datetime import datetime

LOG_FILE = "trades.json"

def log_trade(mode, price, usdt_spent, btc_bought, rsi=None):
    trade = {
        "timestamp": datetime.now().isoformat(),
        "mode": mode,
        "price": price,
        "usdt_spent": usdt_spent,
        "btc_bought": btc_bought,
        "rsi": rsi,
    }

    trades = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            trades = json.load(f)

    trades.append(trade)

    with open(LOG_FILE, "w") as f:
        json.dump(trades, f, indent=2)

    return trade

def get_trades():
    if not os.path.exists(LOG_FILE):
        return []
    with open(LOG_FILE, "r") as f:
        return json.load(f)

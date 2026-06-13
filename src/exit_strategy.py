from src.config import TAKE_PROFIT_PCT, TRAILING_STOP_PCT, SYMBOL, PAPER_TRADING
from src.stop_loss import get_avg_buy_price
from src.state import get_highest_price, update_highest_price, reset_highest_price
from src.logger import get_trades
from src.notifier import send_email

def _sell_all(reason):
    from src.bot import get_client, get_balance
    if PAPER_TRADING:
        print(f"[SIMULACION] Venta por {reason}")
        send_email(f"[Bot DCA] Venta simulada — {reason}", f"Se vendería todo el BTC. Motivo: {reason}")
        reset_highest_price()
        return True

    client = get_client()
    from src.bot import get_balance
    balances = get_balance()
    btc = balances.get("BTC", 0)
    if btc > 0.000001:
        client.order_market_sell(symbol=SYMBOL, quantity=round(btc, 6))
        print(f"[REAL] Vendidos {btc:.8f} BTC — {reason}")
        send_email(f"[Bot DCA] Venta ejecutada — {reason}", f"Se vendieron {btc:.8f} BTC. Motivo: {reason}")
        reset_highest_price()
        return True
    return False

def check_take_profit(current_price):
    trades = get_trades()
    if not trades:
        return False

    avg_price = get_avg_buy_price()
    if not avg_price:
        return False

    target = avg_price * (1 + TAKE_PROFIT_PCT / 100)

    if current_price >= target:
        gain_pct = ((current_price - avg_price) / avg_price) * 100
        msg = (
            f"TAKE PROFIT ALCANZADO\n"
            f"Precio promedio de compra: ${avg_price:,.2f}\n"
            f"Precio actual: ${current_price:,.2f}\n"
            f"Ganancia: +{gain_pct:.2f}%\n"
            f"Objetivo era: +{TAKE_PROFIT_PCT}%"
        )
        print(f"[TAKE PROFIT] {msg}")
        return _sell_all(f"Take Profit +{gain_pct:.2f}%")

    return False

def check_trailing_stop(current_price):
    highest = update_highest_price(current_price)
    floor = highest * (1 - TRAILING_STOP_PCT / 100)

    print(f"Trailing Stop — Máximo: ${highest:,.2f} | Piso: ${floor:,.2f} | Actual: ${current_price:,.2f}")

    if current_price <= floor and highest != current_price:
        drop_pct = ((highest - current_price) / highest) * 100
        msg = (
            f"TRAILING STOP ACTIVADO\n"
            f"Precio máximo registrado: ${highest:,.2f}\n"
            f"Precio actual: ${current_price:,.2f}\n"
            f"Caída desde máximo: -{drop_pct:.2f}% (límite: -{TRAILING_STOP_PCT}%)"
        )
        print(f"[TRAILING STOP] {msg}")
        return _sell_all(f"Trailing Stop -{drop_pct:.2f}%")

    return False

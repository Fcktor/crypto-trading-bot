from src.config import STOP_LOSS_PCT, SELL_ON_STOP, SYMBOL, PAPER_TRADING
from src.logger import get_trades
from src.notifier import send_email

def get_avg_buy_price():
    trades = get_trades()
    if not trades:
        return None
    total_usdt = sum(t["usdt_spent"] for t in trades)
    total_btc = sum(t["btc_bought"] for t in trades)
    return total_usdt / total_btc if total_btc > 0 else None

def check_stop_loss(current_price):
    avg_price = get_avg_buy_price()
    if avg_price is None:
        return False

    drop_pct = ((avg_price - current_price) / avg_price) * 100

    if drop_pct >= STOP_LOSS_PCT:
        msg = (
            f"STOP-LOSS ACTIVADO\n"
            f"Precio promedio de compra: ${avg_price:,.2f}\n"
            f"Precio actual: ${current_price:,.2f}\n"
            f"Caída: {drop_pct:.2f}% (límite: {STOP_LOSS_PCT}%)\n"
            f"El bot ha pausado las compras."
        )
        print(f"[STOP-LOSS] {msg}")
        send_email("[Bot DCA] STOP-LOSS ACTIVADO", msg)

        if SELL_ON_STOP and not PAPER_TRADING:
            _sell_all()

        return True

    return False

def _sell_all():
    from src.bot import get_client, get_balance
    client = get_client()
    balances = get_balance()
    btc = balances.get("BTC", 0)
    if btc > 0:
        client.order_market_sell(symbol=SYMBOL, quantity=round(btc, 6))
        print(f"[STOP-LOSS] Vendidos {btc:.8f} BTC")
        send_email("[Bot DCA] Venta ejecutada por stop-loss", f"Se vendieron {btc:.8f} BTC al precio actual.")

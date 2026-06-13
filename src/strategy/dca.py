from src.config import SYMBOL, PAPER_TRADING, RSI_BUY
from src.bot import get_client, get_btc_price, get_balance
from src.logger import log_trade
from src.notifier import notify_trade
from src.indicators import get_rsi
from src.risk import get_trade_amount

def run_dca():
    price = get_btc_price()
    rsi = get_rsi()
    amount = get_trade_amount(price)

    print(f"RSI actual: {rsi} (compra si RSI < {RSI_BUY})")

    if rsi >= RSI_BUY:
        print(f"RSI alto ({rsi}) — esperando mejor momento para comprar")
        return None

    btc_to_buy = amount / price

    if PAPER_TRADING:
        trade = log_trade(
            mode="SIMULACION",
            price=price,
            usdt_spent=amount,
            btc_bought=btc_to_buy,
            rsi=rsi,
        )
        print(f"[SIMULACION] RSI={rsi} ✓ Compra ${amount:.2f} a ${price:,.2f} → {btc_to_buy:.8f} BTC")
        notify_trade(trade)
        return trade

    balances = get_balance()
    usdt_available = balances.get("USDT", 0)

    if usdt_available < amount:
        print(f"Saldo insuficiente: tienes ${usdt_available:.2f} USDT, necesitas ${amount:.2f}")
        return None

    client = get_client()
    order = client.order_market_buy(
        symbol=SYMBOL,
        quoteOrderQty=amount,
    )

    trade = log_trade(
        mode="REAL",
        price=price,
        usdt_spent=amount,
        btc_bought=float(order["executedQty"]),
        rsi=rsi,
    )
    print(f"[REAL] RSI={rsi} ✓ Compra ${amount:.2f} → {trade['btc_bought']:.8f} BTC a ${price:,.2f}")
    notify_trade(trade)
    return trade

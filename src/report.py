from src.logger import get_trades
from src.bot import get_btc_price

def print_report():
    trades = get_trades()

    if not trades:
        print("No hay trades registrados aún.")
        return

    total_usdt = sum(t["usdt_spent"] for t in trades)
    total_btc = sum(t["btc_bought"] for t in trades)
    avg_price = total_usdt / total_btc
    current_price = get_btc_price()
    current_value = total_btc * current_price
    pnl = current_value - total_usdt
    pnl_pct = (pnl / total_usdt) * 100

    print("=" * 40)
    print("       RESUMEN DE RENDIMIENTO DCA")
    print("=" * 40)
    print(f"  Trades ejecutados : {len(trades)}")
    print(f"  USDT invertidos   : ${total_usdt:.2f}")
    print(f"  BTC acumulado     : {total_btc:.8f}")
    print(f"  Precio promedio   : ${avg_price:,.2f}")
    print(f"  Precio actual     : ${current_price:,.2f}")
    print(f"  Valor actual      : ${current_value:.4f}")
    print(f"  P&L               : ${pnl:.4f} ({pnl_pct:+.2f}%)")
    print("=" * 40)

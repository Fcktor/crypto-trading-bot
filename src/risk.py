from datetime import datetime, date
from src.config import RISK_PER_TRADE_PCT, DAILY_LOSS_LIMIT_PCT, PAPER_TRADING, PAPER_BALANCE_USDT
from src.logger import get_trades
from src.notifier import send_email

def get_trade_amount(current_price):
    """Calcula cuánto USDT usar en el próximo trade según % de capital disponible."""
    if PAPER_TRADING:
        usdt = PAPER_BALANCE_USDT
    else:
        from src.bot import get_balance
        usdt = get_balance().get("USDT", 0)

    amount = round(usdt * (RISK_PER_TRADE_PCT / 100), 2)
    # Binance requiere mínimo $5 en spot BTC — avisamos si no alcanza
    if amount < 5:
        print(f"Aviso: monto calculado (${amount}) es bajo. Binance requiere mínimo ~$5 por orden.")
    print(f"Capital disponible: ${usdt:.2f} | Riesgo {RISK_PER_TRADE_PCT}% = ${amount:.2f} por trade")
    return amount

def get_daily_pnl(current_price):
    """Calcula el P&L solo de los trades de hoy."""
    trades = get_trades()
    today = date.today().isoformat()
    today_trades = [t for t in trades if t["timestamp"].startswith(today)]

    if not today_trades:
        return 0.0, 0.0

    usdt_spent = sum(t["usdt_spent"] for t in today_trades)
    btc_bought = sum(t["btc_bought"] for t in today_trades)
    current_value = btc_bought * current_price
    pnl = current_value - usdt_spent
    pnl_pct = (pnl / usdt_spent * 100) if usdt_spent > 0 else 0
    return pnl, pnl_pct

def check_daily_loss_limit(current_price):
    """Devuelve True si se superó el límite de pérdida diaria."""
    pnl, pnl_pct = get_daily_pnl(current_price)

    if pnl_pct < -DAILY_LOSS_LIMIT_PCT:
        msg = (
            f"LÍMITE DIARIO DE PÉRDIDAS ALCANZADO\n"
            f"P&L hoy: {pnl_pct:.2f}% (${pnl:.4f})\n"
            f"Límite: -{DAILY_LOSS_LIMIT_PCT}%\n"
            f"El bot pausará operaciones hasta mañana."
        )
        print(f"[RIESGO] {msg}")
        send_email("[Bot DCA] Límite diario de pérdidas", msg)
        return True

    print(f"P&L hoy: {pnl_pct:+.2f}% (${pnl:+.4f}) — dentro del límite diario")
    return False

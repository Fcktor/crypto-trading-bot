from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("BINANCE_API_KEY")
SECRET_KEY = os.getenv("BINANCE_SECRET_KEY")

SYMBOL = "BTCUSDT"
TRADE_AMOUNT_USDT = 1.0     # cuánto USDT comprar por cada operación
INTERVAL_HOURS = 1           # cada cuántas horas compra el bot
PAPER_TRADING = True         # True = simulación, False = dinero real

EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")

STOP_LOSS_PCT = 10.0    # pausa compras si BTC cae más de 10% bajo el precio promedio
SELL_ON_STOP  = False   # True = vende todo al activarse el stop-loss

RSI_PERIOD    = 14      # período estándar del RSI
RSI_BUY       = 45     # compra si RSI está por debajo de este valor (conservador)
RSI_INTERVAL  = "1h"   # velas de 1 hora para calcular el RSI

TAKE_PROFIT_PCT    = 5.0   # vende si BTC sube 5% sobre el precio promedio de compra
TRAILING_STOP_PCT  = 3.0   # vende si BTC cae 3% desde su precio máximo reciente

RISK_PER_TRADE_PCT  = 10.0  # % del balance USDT disponible a usar por trade
DAILY_LOSS_LIMIT_PCT = 5.0  # pausa el día si el P&L diario cae más de este %
PAPER_BALANCE_USDT  = 10.0  # balance virtual para simulación

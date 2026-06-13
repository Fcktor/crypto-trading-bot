import time
from src.config import INTERVAL_HOURS, PAPER_TRADING, STOP_LOSS_PCT, TAKE_PROFIT_PCT, TRAILING_STOP_PCT, DAILY_LOSS_LIMIT_PCT, RISK_PER_TRADE_PCT
from src.strategy.dca import run_dca
from src.bot import get_btc_price
from src.stop_loss import check_stop_loss
from src.exit_strategy import check_take_profit, check_trailing_stop
from src.risk import check_daily_loss_limit

def main():
    modo = "SIMULACION" if PAPER_TRADING else "REAL"
    print(f"Bot DCA iniciado en modo {modo}")
    print(f"Intervalo: {INTERVAL_HOURS}h | Riesgo/trade: {RISK_PER_TRADE_PCT}% | Stop-Loss: {STOP_LOSS_PCT}%")
    print(f"TP: +{TAKE_PROFIT_PCT}% | Trailing: -{TRAILING_STOP_PCT}% | Límite diario: -{DAILY_LOSS_LIMIT_PCT}%\n")

    while True:
        print("=" * 50)
        price = get_btc_price()
        print(f"Precio BTC: ${price:,.2f}")

        # 1. Verificar salidas primero
        if check_take_profit(price):
            print("Take Profit ejecutado. Reiniciando ciclo.\n")
            time.sleep(INTERVAL_HOURS * 3600)
            continue

        if check_trailing_stop(price):
            print("Trailing Stop ejecutado. Reiniciando ciclo.\n")
            time.sleep(INTERVAL_HOURS * 3600)
            continue

        # 2. Verificar límites de riesgo
        if check_daily_loss_limit(price):
            print(f"Operaciones pausadas por límite diario. Revisando en {INTERVAL_HOURS}h\n")
            time.sleep(INTERVAL_HOURS * 3600)
            continue

        if check_stop_loss(price):
            print(f"Compras pausadas por Stop-Loss. Revisando en {INTERVAL_HOURS}h\n")
            time.sleep(INTERVAL_HOURS * 3600)
            continue

        # 3. Ejecutar DCA
        run_dca()
        print(f"Próxima revisión en {INTERVAL_HOURS}h\n")
        time.sleep(INTERVAL_HOURS * 3600)

if __name__ == "__main__":
    main()

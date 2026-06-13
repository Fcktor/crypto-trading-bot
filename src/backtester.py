import pandas as pd
import pandas_ta as ta
from src.bot import get_client
from src.config import (
    SYMBOL, RSI_PERIOD, RSI_BUY,
    TAKE_PROFIT_PCT, TRAILING_STOP_PCT,
    STOP_LOSS_PCT, RISK_PER_TRADE_PCT
)

def download_historical(start: str, end: str, interval="1h"):
    client = get_client()
    print(f"Descargando datos {interval} desde {start} hasta {end}...")
    raw = client.get_historical_klines(SYMBOL, interval, start, end)
    df = pd.DataFrame(raw, columns=[
        "timestamp", "open", "high", "low", "close", "volume",
        "close_time", "quote_volume", "trades",
        "taker_buy_base", "taker_buy_quote", "ignore"
    ])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df["close"] = df["close"].astype(float)
    print(f"  {len(df)} velas descargadas.")
    return df

def run_backtest(df: pd.DataFrame, initial_balance=10.0):
    df = df.copy()
    df["rsi"] = ta.rsi(df["close"], length=RSI_PERIOD)
    df = df.dropna(subset=["rsi"]).reset_index(drop=True)

    usdt     = initial_balance
    btc      = 0.0
    highest  = None
    history  = []          # historial completo de operaciones

    # Posición actual (se resetea tras cada venta)
    position_usdt = 0.0   # cuánto USDT llevamos invertido en la posición actual
    position_btc  = 0.0   # cuánto BTC tenemos en la posición actual

    for _, row in df.iterrows():
        price = row["close"]
        rsi   = row["rsi"]
        ts    = row["timestamp"]

        # Actualizar precio máximo
        if position_btc > 0:
            highest = price if highest is None else max(highest, price)

        # --- SALIDAS (solo si tenemos posición abierta) ---
        if position_btc > 0:
            avg_price = position_usdt / position_btc

            # Take Profit
            if price >= avg_price * (1 + TAKE_PROFIT_PCT / 100):
                gain_pct = (price - avg_price) / avg_price * 100
                proceeds = position_btc * price
                usdt += proceeds
                history.append({
                    "type": "SELL", "reason": "TP",
                    "price": price, "btc": position_btc,
                    "usdt": proceeds, "timestamp": ts,
                    "gain_pct": gain_pct, "avg_buy": avg_price
                })
                position_btc = 0.0
                position_usdt = 0.0
                btc = 0.0
                highest = None
                continue

            # Trailing Stop
            if highest:
                floor = highest * (1 - TRAILING_STOP_PCT / 100)
                if price <= floor:
                    drop_pct = (highest - price) / highest * 100
                    gain_pct = (price - avg_price) / avg_price * 100
                    proceeds = position_btc * price
                    usdt += proceeds
                    history.append({
                        "type": "SELL", "reason": "TrailingStop",
                        "price": price, "btc": position_btc,
                        "usdt": proceeds, "timestamp": ts,
                        "gain_pct": gain_pct, "avg_buy": avg_price
                    })
                    position_btc = 0.0
                    position_usdt = 0.0
                    btc = 0.0
                    highest = None
                    continue

            # Stop Loss — pausa compras si precio cae 10% bajo promedio
            if price < avg_price * (1 - STOP_LOSS_PCT / 100):
                continue

        # --- ENTRADA ---
        if rsi < RSI_BUY and usdt > 1.0:
            amount = round(usdt * (RISK_PER_TRADE_PCT / 100), 4)
            if amount < 0.5:
                continue
            btc_bought = amount / price
            usdt -= amount
            btc  += btc_bought
            position_usdt += amount
            position_btc  += btc_bought
            history.append({
                "type": "BUY", "price": price,
                "btc": btc_bought, "usdt": amount,
                "timestamp": ts, "rsi": rsi
            })

    final_price = df["close"].iloc[-1]
    final_value = usdt + btc * final_price

    return {
        "history": history,
        "initial_balance": initial_balance,
        "final_value": final_value,
        "final_price": final_price,
        "df": df,
    }

def print_report(result):
    history  = result["history"]
    initial  = result["initial_balance"]
    final    = result["final_value"]
    buys     = [t for t in history if t["type"] == "BUY"]
    sells    = [t for t in history if t["type"] == "SELL"]
    wins     = [t for t in sells if t.get("gain_pct", 0) > 0]
    losses   = [t for t in sells if t.get("gain_pct", 0) <= 0]

    total_return  = ((final - initial) / initial) * 100
    win_rate      = (len(wins) / len(sells) * 100) if sells else 0
    avg_win       = sum(t["gain_pct"] for t in wins) / len(wins) if wins else 0
    avg_loss      = sum(t["gain_pct"] for t in losses) / len(losses) if losses else 0
    gross_gain    = sum(t["usdt"] - t["btc"] * t["avg_buy"] for t in wins) if wins else 0
    gross_loss    = abs(sum(t["usdt"] - t["btc"] * t["avg_buy"] for t in losses)) if losses else 0
    profit_factor = (gross_gain / gross_loss) if gross_loss > 0 else float("inf")

    # Max Drawdown
    equity = [initial]
    bal = initial
    pos_usdt, pos_btc = 0.0, 0.0
    for t in history:
        if t["type"] == "BUY":
            bal -= t["usdt"]
            pos_usdt += t["usdt"]
            pos_btc  += t["btc"]
        else:
            bal += t["usdt"]
            pos_usdt, pos_btc = 0.0, 0.0
        equity.append(bal + pos_btc * t["price"])
    equity_s = pd.Series(equity)
    drawdown = ((equity_s - equity_s.cummax()) / equity_s.cummax() * 100).min()

    print("\n" + "=" * 50)
    print("         REPORTE DE BACKTESTING")
    print("=" * 50)
    print(f"  Capital inicial    : ${initial:.2f}")
    print(f"  Capital final      : ${final:.4f}")
    print(f"  Retorno total      : {total_return:+.2f}%")
    print(f"  Trades de compra   : {len(buys)}")
    print(f"  Trades de venta    : {len(sells)}")
    print(f"    - Ganadores (TP)      : {len(wins)}")
    print(f"    - Perdedores          : {len(losses)}")
    print(f"  Win Rate           : {win_rate:.1f}%")
    print(f"  Ganancia promedio  : {avg_win:+.2f}%")
    print(f"  Pérdida promedio   : {avg_loss:+.2f}%")
    print(f"  Profit Factor      : {profit_factor:.2f}")
    print(f"  Max Drawdown       : {drawdown:.2f}%")
    print(f"  Precio BTC final   : ${result['final_price']:,.2f}")
    print("=" * 50)

    if sells:
        print(f"\n  Últimas 10 ventas:")
        for s in sells[-10:]:
            print(f"    {s['timestamp'].strftime('%Y-%m-%d')} | {s['reason']:13} | "
                  f"${s['price']:,.0f} | {s.get('gain_pct', 0):+.2f}%")

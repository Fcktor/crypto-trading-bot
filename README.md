# Crypto Trading Bot

An automated BTC accumulation bot built around dollar-cost averaging, with the risk controls that DCA normally lacks: emergency stop-loss, daily loss limits, position sizing, and optional take-profit and trailing-stop exits.

**Paper trading is on by default.** The bot simulates against a virtual balance until you explicitly turn it off.

## Strategy

The core loop runs every `INTERVAL_HOURS` and buys a fixed USDT amount, filtered by RSI so it accumulates into weakness rather than blindly on a timer.

Two modes:

- **Pure DCA** (`PURE_DCA = True`) — accumulate only, never sell. Exits are disabled.
- **DCA with exits** (`PURE_DCA = False`) — adds take-profit at +20% and a trailing stop at 8% off the high.

Protections run in both modes:

| Control | Default | Behavior |
|---|---|---|
| Emergency stop-loss | 10% | Pauses buying when price falls 10% below average entry |
| Daily loss limit | 5% | Pauses for the day when P&L breaches the threshold |
| Risk per trade | 10% | Caps the share of available balance used per trade |
| RSI filter | buy below 35 | Only buys when 1h RSI signals oversold |

## Stack

| Technology | Role |
|---|---|
| Python 3 | Language |
| python-binance | Market data and order execution |
| Flask | Local monitoring dashboard |
| SMTP / Telegram | Trade notifications |

## Project structure

```
main.py               # Main loop: price → exits → protections → strategy
backtest.py           # Run the strategy over historical data
dashboard.py          # Flask dashboard, auto-refreshing chart of trades
report.py             # P&L reporting

src/
├── config.py         # All tunable parameters
├── bot.py            # Binance client and price fetching
├── strategy/dca.py   # DCA entry logic
├── indicators.py     # RSI
├── stop_loss.py      # Emergency stop-loss
├── exit_strategy.py  # Take-profit and trailing stop
├── risk.py           # Position sizing and daily loss limit
├── backtester.py     # Backtest engine
├── state.py          # Persisted bot state
├── logger.py         # Trade log
└── notifier.py       # Email and Telegram alerts
```

## Running

```bash
pip install -r requirements.txt
cp .env.example .env       # add your API keys

python main.py             # start the bot
python backtest.py         # backtest the strategy
python dashboard.py        # dashboard at localhost:5000
python report.py           # print P&L summary
```

## Environment variables

```env
BINANCE_API_KEY=
BINANCE_SECRET_KEY=
EMAIL_SENDER=
EMAIL_PASSWORD=
EMAIL_RECEIVER=
TELEGRAM_TOKEN=
TELEGRAM_CHAT_ID=
```

## Disclaimer

This is a personal project for learning algorithmic trading, not financial advice. Backtested results do not predict future returns. Run it in paper mode and read the code before flipping `PAPER_TRADING` to `False` — at that point it moves real money.

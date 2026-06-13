from src.backtester import download_historical, run_backtest, print_report

print("Backtesting BTC/USDT 2022-2024\n")

df = download_historical("2022-01-01", "2024-12-31", interval="1h")
result = run_backtest(df, initial_balance=10.0)
print_report(result)

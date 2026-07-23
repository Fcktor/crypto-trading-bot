# Crypto Trading Bot

Bot automatizado de acumulación de BTC construido alrededor de dollar-cost averaging, con los controles de riesgo que al DCA normalmente le faltan: stop-loss de emergencia, límite de pérdida diaria, dimensionamiento de posición y salidas opcionales por take-profit y trailing stop.

**El modo simulación viene activado por defecto.** El bot opera contra un balance virtual hasta que lo desactives explícitamente.

## Estrategia

El loop principal corre cada `INTERVAL_HOURS` y compra un monto fijo en USDT, filtrado por RSI para acumular en debilidad en lugar de comprar a ciegas por temporizador.

Dos modos:

- **DCA puro** (`PURE_DCA = True`) — solo acumula, nunca vende. Las salidas quedan desactivadas.
- **DCA con salidas** (`PURE_DCA = False`) — agrega take-profit en +20% y trailing stop a 8% del máximo.

Las protecciones corren en ambos modos:

| Control | Valor por defecto | Comportamiento |
|---|---|---|
| Stop-loss de emergencia | 10% | Pausa las compras si el precio cae 10% bajo el precio promedio de entrada |
| Límite de pérdida diaria | 5% | Pausa el día cuando el P&L supera el umbral |
| Riesgo por operación | 10% | Limita la porción del balance disponible que se usa por operación |
| Filtro RSI | compra bajo 35 | Solo compra cuando el RSI de 1h indica sobreventa |

## Stack

| Tecnología | Rol |
|---|---|
| Python 3 | Lenguaje |
| python-binance | Datos de mercado y ejecución de órdenes |
| Flask | Dashboard local de monitoreo |
| SMTP / Telegram | Notificaciones de operaciones |

## Estructura

```
main.py               # Loop principal: precio → salidas → protecciones → estrategia
backtest.py           # Corre la estrategia sobre datos históricos
dashboard.py          # Dashboard Flask con gráfico de operaciones autorrefrescante
report.py             # Reporte de P&L

src/
├── config.py         # Todos los parámetros configurables
├── bot.py            # Cliente de Binance y consulta de precio
├── strategy/dca.py   # Lógica de entrada DCA
├── indicators.py     # RSI
├── stop_loss.py      # Stop-loss de emergencia
├── exit_strategy.py  # Take-profit y trailing stop
├── risk.py           # Dimensionamiento y límite de pérdida diaria
├── backtester.py     # Motor de backtesting
├── state.py          # Estado persistido del bot
├── logger.py         # Registro de operaciones
└── notifier.py       # Alertas por correo y Telegram
```

## Ejecutar

```bash
pip install -r requirements.txt
cp .env.example .env       # agrega tus API keys

python main.py             # inicia el bot
python backtest.py         # backtest de la estrategia
python dashboard.py        # dashboard en localhost:5000
python report.py           # resumen de P&L
```

## Variables de entorno

```env
BINANCE_API_KEY=
BINANCE_SECRET_KEY=
EMAIL_SENDER=
EMAIL_PASSWORD=
EMAIL_RECEIVER=
TELEGRAM_TOKEN=
TELEGRAM_CHAT_ID=
```

## Advertencia

Este es un proyecto personal para aprender trading algorítmico, no asesoría financiera. Los resultados de un backtest no predicen rendimientos futuros. Córrelo en modo simulación y lee el código antes de poner `PAPER_TRADING` en `False`: a partir de ahí mueve dinero real.

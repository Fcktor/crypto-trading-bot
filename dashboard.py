from flask import Flask, render_template_string, jsonify
from src.logger import get_trades
from src.bot import get_btc_price

app = Flask(__name__)

TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta http-equiv="refresh" content="30">
  <title>Bot DCA - Dashboard</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <style>
    body { font-family: monospace; background: #0d1117; color: #c9d1d9; padding: 2rem; margin: 0; }
    h1 { color: #f0b90b; margin-bottom: 1.5rem; }
    .card { background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 1.5rem; margin-bottom: 1.5rem; }
    .stats { display: flex; flex-wrap: wrap; gap: 2rem; }
    .stat .value { font-size: 1.4rem; font-weight: bold; color: #58a6ff; }
    .stat .label { font-size: 0.8rem; color: #8b949e; margin-top: 4px; }
    .positive { color: #3fb950 !important; }
    .negative { color: #f85149 !important; }
    table { width: 100%; border-collapse: collapse; }
    th { text-align: left; padding: 0.5rem; border-bottom: 1px solid #30363d; color: #8b949e; font-size: 0.85rem; }
    td { padding: 0.5rem; border-bottom: 1px solid #21262d; font-size: 0.9rem; }
    .badge { padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; }
    .sim { background: #1f4068; color: #58a6ff; }
    .real { background: #1a3a1a; color: #3fb950; }
    canvas { max-height: 300px; }
    h3 { margin-top: 0; color: #c9d1d9; }
    footer { color: #8b949e; font-size: 0.8rem; margin-top: 1rem; }
  </style>
</head>
<body>
  <h1>Bot DCA — BTC/USDT</h1>

  <div class="card">
    {% if trades %}
    <div class="stats">
      <div class="stat">
        <div class="value">${{ "{:,.2f}".format(current_price) }}</div>
        <div class="label">Precio actual BTC</div>
      </div>
      <div class="stat">
        <div class="value">{{ trades|length }}</div>
        <div class="label">Trades ejecutados</div>
      </div>
      <div class="stat">
        <div class="value">${{ "%.2f"|format(total_usdt) }}</div>
        <div class="label">USDT invertidos</div>
      </div>
      <div class="stat">
        <div class="value">{{ "%.8f"|format(total_btc) }} BTC</div>
        <div class="label">BTC acumulado</div>
      </div>
      <div class="stat">
        <div class="value">${{ "{:,.2f}".format(avg_price) }}</div>
        <div class="label">Precio promedio compra</div>
      </div>
      <div class="stat">
        <div class="value {{ 'positive' if pnl >= 0 else 'negative' }}">${{ "%.4f"|format(pnl) }} ({{ "%+.2f"|format(pnl_pct) }}%)</div>
        <div class="label">P&L</div>
      </div>
    </div>
    {% else %}
    <p>No hay trades aún.</p>
    {% endif %}
  </div>

  {% if trades %}
  <div class="card">
    <h3>Precio de compra por trade</h3>
    <canvas id="chart"></canvas>
  </div>
  {% endif %}

  <div class="card">
    <h3>Historial de trades</h3>
    <table>
      <thead>
        <tr>
          <th>Fecha</th>
          <th>Modo</th>
          <th>Precio BTC</th>
          <th>USDT</th>
          <th>BTC</th>
        </tr>
      </thead>
      <tbody>
        {% for t in trades|reverse %}
        <tr>
          <td>{{ t.timestamp[:19].replace("T", " ") }}</td>
          <td><span class="badge {{ 'sim' if t.mode == 'SIMULACION' else 'real' }}">{{ t.mode }}</span></td>
          <td>${{ "{:,.2f}".format(t.price) }}</td>
          <td>${{ "%.2f"|format(t.usdt_spent) }}</td>
          <td>{{ "%.8f"|format(t.btc_bought) }}</td>
        </tr>
        {% endfor %}
      </tbody>
    </table>
  </div>

  <footer>Actualiza automáticamente cada 30 segundos</footer>

  {% if trades %}
  <script>
    const labels = {{ labels | tojson }};
    const prices = {{ prices | tojson }};
    const avgPrice = {{ avg_price }};

    const ctx = document.getElementById("chart").getContext("2d");
    new Chart(ctx, {
      type: "line",
      data: {
        labels: labels,
        datasets: [
          {
            label: "Precio de compra",
            data: prices,
            borderColor: "#f0b90b",
            backgroundColor: "rgba(240,185,11,0.1)",
            pointBackgroundColor: "#f0b90b",
            pointRadius: 5,
            tension: 0.3,
          },
          {
            label: "Precio promedio",
            data: Array(labels.length).fill(avgPrice),
            borderColor: "#3fb950",
            borderDash: [6, 3],
            pointRadius: 0,
            tension: 0,
          }
        ]
      },
      options: {
        responsive: true,
        plugins: {
          legend: { labels: { color: "#c9d1d9" } }
        },
        scales: {
          x: { ticks: { color: "#8b949e" }, grid: { color: "#21262d" } },
          y: {
            ticks: {
              color: "#8b949e",
              callback: v => "$" + v.toLocaleString()
            },
            grid: { color: "#21262d" }
          }
        }
      }
    });
  </script>
  {% endif %}
</body>
</html>
"""

@app.route("/")
def index():
    trades = get_trades()
    current_price = get_btc_price()

    total_usdt = sum(t["usdt_spent"] for t in trades)
    total_btc = sum(t["btc_bought"] for t in trades)
    avg_price = total_usdt / total_btc if total_btc > 0 else 0
    current_value = total_btc * current_price
    pnl = current_value - total_usdt
    pnl_pct = (pnl / total_usdt * 100) if total_usdt > 0 else 0

    labels = [t["timestamp"][11:16] for t in trades]
    prices = [t["price"] for t in trades]

    return render_template_string(
        TEMPLATE,
        trades=trades,
        current_price=current_price,
        total_usdt=total_usdt,
        total_btc=total_btc,
        avg_price=avg_price,
        pnl=pnl,
        pnl_pct=pnl_pct,
        labels=labels,
        prices=prices,
    )

if __name__ == "__main__":
    app.run(debug=False, port=5000)

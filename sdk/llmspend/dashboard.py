"""Local web dashboard — serves a single-page cost dashboard from SQLite.

Usage:
    llmspend dashboard              # opens localhost:8888
    llmspend dashboard --port 9000  # custom port
"""

import json
import os
import sqlite3
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs


def get_db_path() -> str:
    return os.environ.get("LLMSPEND_DB", os.path.expanduser("~/.llmspend/events.db"))


def _query(sql: str, params: tuple = ()) -> list[dict]:
    db_path = get_db_path()
    if not os.path.exists(db_path):
        return []
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(sql, params).fetchall()
    result = [dict(r) for r in rows]
    conn.close()
    return result


def _api_summary(period: str) -> dict:
    """Return full dashboard data."""
    interval_map = {"1h": "1 hour", "24h": "24 hours", "7d": "7 days", "30d": "30 days"}
    interval = interval_map.get(period, "24 hours")

    total = _query(f"""
        SELECT COUNT(*) as calls, SUM(cost_usd) as total_cost,
               SUM(tokens_in) as total_in, SUM(tokens_out) as total_out,
               AVG(latency_ms) as avg_latency
        FROM events WHERE timestamp >= datetime('now', '-{interval}')
    """)

    by_feature = _query(f"""
        SELECT feature as name, COUNT(*) as calls, SUM(cost_usd) as cost,
               SUM(tokens_in + tokens_out) as tokens, AVG(latency_ms) as avg_latency
        FROM events WHERE timestamp >= datetime('now', '-{interval}')
        GROUP BY feature ORDER BY cost DESC
    """)

    by_model = _query(f"""
        SELECT model as name, COUNT(*) as calls, SUM(cost_usd) as cost,
               SUM(tokens_in + tokens_out) as tokens, AVG(latency_ms) as avg_latency
        FROM events WHERE timestamp >= datetime('now', '-{interval}')
        GROUP BY model ORDER BY cost DESC
    """)

    by_user = _query(f"""
        SELECT user_id as name, COUNT(*) as calls, SUM(cost_usd) as cost,
               SUM(tokens_in + tokens_out) as tokens, AVG(latency_ms) as avg_latency
        FROM events WHERE timestamp >= datetime('now', '-{interval}')
        GROUP BY user_id ORDER BY cost DESC LIMIT 20
    """)

    # Time series (hourly for <2d, daily for longer)
    if period in ("1h", "24h"):
        time_series = _query(f"""
            SELECT strftime('%Y-%m-%d %H:00', timestamp) as bucket,
                   COUNT(*) as calls, SUM(cost_usd) as cost
            FROM events WHERE timestamp >= datetime('now', '-{interval}')
            GROUP BY bucket ORDER BY bucket
        """)
    else:
        time_series = _query(f"""
            SELECT strftime('%Y-%m-%d', timestamp) as bucket,
                   COUNT(*) as calls, SUM(cost_usd) as cost
            FROM events WHERE timestamp >= datetime('now', '-{interval}')
            GROUP BY bucket ORDER BY bucket
        """)

    top_calls = _query(f"""
        SELECT timestamp, model, tokens_in, tokens_out, cost_usd, latency_ms,
               feature, user_id, project
        FROM events WHERE timestamp >= datetime('now', '-{interval}')
        ORDER BY cost_usd DESC LIMIT 20
    """)

    t = total[0] if total else {}
    return {
        "period": period,
        "total_calls": t.get("calls", 0),
        "total_cost": round(t.get("total_cost") or 0, 6),
        "total_tokens_in": t.get("total_in") or 0,
        "total_tokens_out": t.get("total_out") or 0,
        "avg_latency_ms": int(t.get("avg_latency") or 0),
        "by_feature": by_feature,
        "by_model": by_model,
        "by_user": by_user,
        "time_series": time_series,
        "top_calls": top_calls,
    }


DASHBOARD_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>LLMSpend Dashboard</title>
<style>
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
:root {
  --bg: #0a0a0a; --card: #111113; --border: #1e1e22;
  --text: #fafafa; --text2: #a1a1aa; --text3: #71717a;
  --accent: #6366f1; --green: #22c55e; --amber: #f59e0b; --red: #ef4444;
  --mono: 'Menlo', 'Consolas', 'Monaco', monospace;
  --sans: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}
html { font-size: 14px; -webkit-font-smoothing: antialiased; }
body { font-family: var(--sans); background: var(--bg); color: var(--text); padding: 24px; max-width: 1100px; margin: 0 auto; }

.header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 28px; }
.logo { font-size: 16px; font-weight: 600; display: flex; align-items: center; gap: 8px; }
.logo-icon { width: 24px; height: 24px; background: var(--accent); border-radius: 5px; display: flex; align-items: center; justify-content: center; font-family: var(--mono); font-size: 14px; font-weight: 700; color: white; }
.period-tabs { display: flex; gap: 4px; }
.period-tab { font-size: 12px; font-weight: 500; padding: 5px 12px; background: transparent; color: var(--text3); border: 1px solid var(--border); border-radius: 6px; cursor: pointer; }
.period-tab.active { background: var(--accent); color: white; border-color: var(--accent); }
.period-tab:hover:not(.active) { border-color: var(--text3); color: var(--text2); }

.summary { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 24px; }
.stat-card { background: var(--card); border: 1px solid var(--border); border-radius: 10px; padding: 18px 20px; }
.stat-label { font-size: 11px; color: var(--text3); text-transform: uppercase; letter-spacing: 1px; margin-bottom: 6px; }
.stat-value { font-size: 24px; font-weight: 700; font-family: var(--mono); }
.stat-value.cost { color: var(--amber); }

.grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 24px; }
.panel { background: var(--card); border: 1px solid var(--border); border-radius: 10px; padding: 20px; }
.panel-title { font-size: 12px; font-weight: 600; color: var(--text2); text-transform: uppercase; letter-spacing: 1px; margin-bottom: 14px; }

.bar-row { display: flex; align-items: center; gap: 10px; margin-bottom: 10px; }
.bar-label { font-size: 12px; color: var(--text2); width: 140px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; font-family: var(--mono); }
.bar-track { flex: 1; height: 22px; background: var(--border); border-radius: 4px; overflow: hidden; position: relative; }
.bar-fill { height: 100%; background: var(--accent); border-radius: 4px; min-width: 2px; transition: width 0.3s; }
.bar-val { font-size: 11px; color: var(--text3); width: 70px; text-align: right; font-family: var(--mono); }

.chart-area { width: 100%; height: 140px; margin-bottom: 24px; background: var(--card); border: 1px solid var(--border); border-radius: 10px; padding: 20px; }
.chart-title { font-size: 12px; font-weight: 600; color: var(--text2); text-transform: uppercase; letter-spacing: 1px; margin-bottom: 12px; }
.chart-bars { display: flex; align-items: flex-end; gap: 3px; height: 90px; }
.chart-col { flex: 1; display: flex; flex-direction: column; align-items: center; gap: 4px; }
.chart-bar { width: 100%; background: var(--accent); border-radius: 2px 2px 0 0; min-height: 1px; transition: height 0.3s; }
.chart-lbl { font-size: 9px; color: var(--text3); font-family: var(--mono); }

table { width: 100%; border-collapse: collapse; }
th { font-size: 11px; color: var(--text3); text-transform: uppercase; letter-spacing: 0.5px; text-align: left; padding: 8px 12px; border-bottom: 1px solid var(--border); }
td { font-size: 12px; color: var(--text2); padding: 8px 12px; border-bottom: 1px solid rgba(30,30,34,0.5); font-family: var(--mono); }
tr:hover td { color: var(--text); }
.cost-cell { color: var(--amber); }

.full-panel { background: var(--card); border: 1px solid var(--border); border-radius: 10px; padding: 20px; overflow-x: auto; }
.empty { color: var(--text3); text-align: center; padding: 40px; font-size: 13px; }
@media (max-width: 768px) { .summary { grid-template-columns: repeat(2, 1fr); } .grid-2 { grid-template-columns: 1fr; } }
</style>
</head>
<body>
<div class="header">
  <div class="logo"><span class="logo-icon">$</span> LLMSpend</div>
  <div class="period-tabs">
    <button class="period-tab" data-p="1h">1H</button>
    <button class="period-tab active" data-p="24h">24H</button>
    <button class="period-tab" data-p="7d">7D</button>
    <button class="period-tab" data-p="30d">30D</button>
  </div>
</div>
<div id="app"><div class="empty">Loading...</div></div>
<script>
let currentPeriod = '24h';

document.querySelectorAll('.period-tab').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.period-tab').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    currentPeriod = btn.dataset.p;
    load();
  });
});

async function load() {
  const r = await fetch('/api/data?period=' + currentPeriod);
  const d = await r.json();
  render(d);
}

function fmt(n) { return n == null ? '$0.00' : '$' + n.toFixed(4); }
function fmtK(n) { return n >= 1000 ? (n/1000).toFixed(1) + 'K' : n.toString(); }

function barChart(items, maxCost) {
  if (!items.length) return '<div class="empty">No data</div>';
  const max = maxCost || Math.max(...items.map(i => i.cost || 0)) || 1;
  return items.map(i => {
    const pct = ((i.cost || 0) / max * 100).toFixed(1);
    const label = i.name || '(none)';
    return `<div class="bar-row">
      <div class="bar-label" title="${label}">${label}</div>
      <div class="bar-track"><div class="bar-fill" style="width:${pct}%"></div></div>
      <div class="bar-val">${fmt(i.cost)}</div>
    </div>`;
  }).join('');
}

function timeChart(series) {
  if (!series.length) return '';
  const max = Math.max(...series.map(s => s.cost || 0)) || 1;
  const bars = series.map(s => {
    const h = Math.max(1, ((s.cost || 0) / max * 80));
    const lbl = s.bucket ? s.bucket.slice(-5) : '';
    return `<div class="chart-col">
      <div class="chart-bar" style="height:${h}px" title="${fmt(s.cost)}"></div>
      <div class="chart-lbl">${lbl}</div>
    </div>`;
  }).join('');
  return `<div class="chart-area"><div class="chart-title">Cost Over Time</div><div class="chart-bars">${bars}</div></div>`;
}

function render(d) {
  const app = document.getElementById('app');
  if (!d.total_calls) {
    app.innerHTML = '<div class="empty">No API calls recorded in this period.<br>Make some API calls and refresh.</div>';
    return;
  }
  const topRows = (d.top_calls || []).slice(0, 10).map(c =>
    `<tr>
      <td>${(c.timestamp||'').slice(11,19)}</td>
      <td>${(c.model||'').slice(0,28)}</td>
      <td>${fmtK(c.tokens_in||0)}/${fmtK(c.tokens_out||0)}</td>
      <td class="cost-cell">${fmt(c.cost_usd)}</td>
      <td>${c.latency_ms||0}ms</td>
      <td>${c.feature||'-'}</td>
      <td>${c.user_id||'-'}</td>
    </tr>`
  ).join('');

  app.innerHTML = `
    <div class="summary">
      <div class="stat-card"><div class="stat-label">Total Cost</div><div class="stat-value cost">${fmt(d.total_cost)}</div></div>
      <div class="stat-card"><div class="stat-label">API Calls</div><div class="stat-value">${d.total_calls.toLocaleString()}</div></div>
      <div class="stat-card"><div class="stat-label">Tokens</div><div class="stat-value">${fmtK(d.total_tokens_in + d.total_tokens_out)}</div></div>
      <div class="stat-card"><div class="stat-label">Avg Latency</div><div class="stat-value">${d.avg_latency_ms}ms</div></div>
    </div>
    ${timeChart(d.time_series || [])}
    <div class="grid-2">
      <div class="panel"><div class="panel-title">Cost by Feature</div>${barChart(d.by_feature || [])}</div>
      <div class="panel"><div class="panel-title">Cost by Model</div>${barChart(d.by_model || [])}</div>
    </div>
    <div class="grid-2">
      <div class="panel"><div class="panel-title">Cost by User</div>${barChart(d.by_user || [])}</div>
      <div class="panel"><div class="panel-title">Summary</div>
        <div style="font-size:12px;color:var(--text2);line-height:1.8">
          <div>Input tokens: <span style="color:var(--text)">${fmtK(d.total_tokens_in)}</span></div>
          <div>Output tokens: <span style="color:var(--text)">${fmtK(d.total_tokens_out)}</span></div>
          <div>Period: <span style="color:var(--text)">${d.period}</span></div>
          <div>DB: <span style="color:var(--text3)">~/.llmspend/events.db</span></div>
        </div>
      </div>
    </div>
    <div class="full-panel" style="margin-top:16px">
      <div class="panel-title">Most Expensive Calls</div>
      <table>
        <thead><tr><th>Time</th><th>Model</th><th>In/Out</th><th>Cost</th><th>Latency</th><th>Feature</th><th>User</th></tr></thead>
        <tbody>${topRows || '<tr><td colspan="7" class="empty">No calls</td></tr>'}</tbody>
      </table>
    </div>
  `;
}

load();
setInterval(load, 10000);
</script>
</body>
</html>"""


class DashboardHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/data":
            qs = parse_qs(parsed.query)
            period = qs.get("period", ["24h"])[0]
            data = _api_summary(period)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(data).encode())
        else:
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(DASHBOARD_HTML.encode())

    def log_message(self, format, *args):
        pass  # Silence request logs


def serve(port: int = 8888):
    """Start the local dashboard server."""
    server = HTTPServer(("127.0.0.1", port), DashboardHandler)
    url = f"http://localhost:{port}"
    print(f"\n  LLMSpend Dashboard → {url}")
    print(f"  Press Ctrl+C to stop\n")
    try:
        webbrowser.open(url)
    except Exception:
        pass
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Dashboard stopped.")
        server.server_close()

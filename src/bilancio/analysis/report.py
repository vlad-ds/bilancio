"""Simple reporting helpers for analytics outputs (CSV/JSON/HTML optional).

Outputs are intentionally minimal and stdlib-only.
"""

from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from decimal import Decimal
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


def _to_json(val: Any):
    if isinstance(val, Decimal):
        # avoid lossy float conversion; write as number if integer, else string
        n = val.normalize()
        if n == n.to_integral_value():
            return int(n)
        return str(n)
    if isinstance(val, dict):
        return {k: _to_json(v) for k, v in val.items()}
    if isinstance(val, (list, tuple)):
        return [ _to_json(x) for x in val ]
    return val


def write_day_metrics_csv(path: Path | str, rows: List[Dict[str, Any]]) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        # still create an empty file with headers day only
        with p.open("w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["day"])
            writer.writeheader()
        return
    # All keys across rows
    keys: List[str] = sorted({k for r in rows for k in r.keys()})
    with p.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        for r in rows:
            row = {}
            for k in keys:
                v = r.get(k)
                if isinstance(v, Decimal):
                    n = v.normalize()
                    row[k] = int(n) if n == n.to_integral_value() else float(n)
                elif v is None:
                    row[k] = ""
                else:
                    row[k] = v
            writer.writerow(row)


def write_day_metrics_json(path: Path | str, rows: List[Dict[str, Any]]) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w") as f:
        json.dump([_to_json(r) for r in rows], f, indent=2)


def write_debtor_shares_csv(path: Path | str, rows: List[Dict[str, Any]]) -> None:
    write_day_metrics_csv(path, rows)


def write_intraday_csv(path: Path | str, rows: List[Dict[str, Any]]) -> None:
    write_day_metrics_csv(path, rows)


def _fmt_num(val: Any) -> str:
    if val is None:
        return "—"
    if isinstance(val, Decimal):
        n = val.normalize()
        try:
            if n == n.to_integral_value():
                return f"{int(n)}"
        except Exception:
            pass
        # Limit to 6 decimal places when not integral
        return f"{float(n):.6f}".rstrip('0').rstrip('.')
    return str(val)


def _group_by(rows: List[Dict[str, Any]], key: str) -> Dict[Any, List[Dict[str, Any]]]:
    out: Dict[Any, List[Dict[str, Any]]] = {}
    for r in rows:
        out.setdefault(r.get(key), []).append(r)
    return out


def write_metrics_html(
    path: Path | str,
    day_metrics: List[Dict[str, Any]],
    debtor_shares: List[Dict[str, Any]],
    intraday: List[Dict[str, Any]],
    title: Optional[str] = None,
    subtitle: Optional[str] = None,
) -> None:
    """Write a single, self-contained HTML report for analytics.

    - Day-by-day metrics in a table.
    - Debtor shortfall shares (long-form or pivot) in a table.
    - Intraday prefix liquidity plots as tiny inline SVGs (per day).
    - Brief explanations for each metric.
    """
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)

    # Aggregate summary across days
    def _dec(x):
        return x if isinstance(x, Decimal) else Decimal(str(x)) if x is not None else Decimal("0")

    S_total = sum((_dec(r.get("S_t")) for r in day_metrics), start=Decimal("0"))
    gross_total = sum((_dec(r.get("gross_settled_t")) for r in day_metrics), start=Decimal("0"))
    Mpeak_max = max((_dec(r.get("Mpeak_t")) for r in day_metrics), default=Decimal("0"))
    v_vals = [r.get("v_t") for r in day_metrics if r.get("v_t") is not None]
    v_avg = (sum((_dec(v) for v in v_vals), start=Decimal("0")) / Decimal(len(v_vals))) if v_vals else None
    # Weighted on-time settlement ratio
    phi_weighted_num = Decimal("0")
    if S_total > 0:
        for r in day_metrics:
            S = r.get("S_t")
            phi = r.get("phi_t")
            if S is not None and phi is not None:
                phi_weighted_num += _dec(S) * _dec(phi)
        phi_weighted = phi_weighted_num / S_total if S_total != 0 else None
    else:
        phi_weighted = None

    # Build intraday SVGs per-day
    intraday_by_day = _group_by(intraday, "day")

    def _svg_for_day(day: Any, rows: List[Dict[str, Any]], width: int = 520, height: int = 140) -> str:
        if not rows:
            return ""
        # Sort by step
        rows = sorted(rows, key=lambda r: int(r.get("step", 0)))
        steps = [int(r.get("step", 0)) for r in rows]
        vals = [float(Decimal(str(r.get("P_prefix", 0)))) for r in rows]
        max_step = max(steps) if steps else 1
        max_val = max(vals) if vals else 1.0
        # Margins
        l, r, t, b = 35, 10, 10, 25
        w = width - l - r
        h = height - t - b
        def sx(s):
            return l + (0 if max_step <= 1 else (s - 1) * (w / (max_step - 1)))
        def sy(v):
            return t + (0 if max_val <= 0 else h - (v * h / max_val))
        pts = " ".join(f"{sx(s):.1f},{sy(v):.1f}" for s, v in zip(steps, vals))
        # Axes ticks (simple)
        y0 = t + h
        x0 = l
        x1 = l + w
        # Labels
        max_val_lbl = f"{max_val:.2f}".rstrip('0').rstrip('.')
        return f"""
<svg width=\"{width}\" height=\"{height}\" viewBox=\"0 0 {width} {height}\" xmlns=\"http://www.w3.org/2000/svg\">
  <rect x=\"0\" y=\"0\" width=\"{width}\" height=\"{height}\" fill=\"#fff\"/>
  <line x1=\"{x0}\" y1=\"{y0}\" x2=\"{x1}\" y2=\"{y0}\" stroke=\"#999\" stroke-width=\"1\"/>
  <line x1=\"{x0}\" y1=\"{t}\" x2=\"{x0}\" y2=\"{y0}\" stroke=\"#999\" stroke-width=\"1\"/>
  <text x=\"{x0}\" y=\"{t-2}\" font-size=\"10\" fill=\"#555\">P_prefix</text>
  <text x=\"{x1}\" y=\"{y0+14}\" font-size=\"10\" fill=\"#555\" text-anchor=\"end\">step</text>
  <text x=\"{x0-6}\" y=\"{t+8}\" font-size=\"10\" fill=\"#555\" text-anchor=\"end\">{max_val_lbl}</text>
  <polyline fill=\"none\" stroke=\"#2a7\" stroke-width=\"2\" points=\"{pts}\" />
</svg>
"""

    # Simple, readable HTML with minimal CSS
    html_title = title or "Bilancio Analytics Report"
    html_sub = subtitle or ""

    def _row(k, v):
        return f"<tr><th scope=\"row\">{k}</th><td>{v}</td></tr>"

    # Build day table
    day_cols = [
        ("day", "Day"),
        ("S_t", "Total dues S_t"),
        ("Mbar_t", "Min net liquidity \u0305M_t"),
        ("M_t", "Start-of-day money M_t"),
        ("G_t", "Liquidity gap G_t"),
        ("alpha_t", "Netting potential \u03B1_t"),
        ("Mpeak_t", "Operational peak M^peak_t"),
        ("gross_settled_t", "Gross settled"),
        ("v_t", "Intraday velocity v_t"),
        ("phi_t", "On-time settlement \u03C6_t"),
        ("delta_t", "Deferral/default \u03B4_t"),
        ("n_debtors", "# debtors"),
        ("n_creditors", "# creditors"),
        ("HHIplus_t", "Creditor HHI^+"),
        ("notes", "Notes"),
    ]

    day_table_head = "".join(f"<th>{label}</th>" for _, label in day_cols)
    day_table_rows = []
    for r in sorted(day_metrics, key=lambda x: int(x.get("day", 0))):
        tds = []
        for key, _ in day_cols:
            tds.append(f"<td>{_fmt_num(r.get(key))}</td>")
        day_table_rows.append("<tr>" + "".join(tds) + "</tr>")

    # Debtor shares table
    ds_by_day = _group_by(debtor_shares, "day")
    ds_sections = []
    for d, rows in sorted(ds_by_day.items(), key=lambda kv: int(kv[0])):
        # Gather unique agents for a pivot-like table
        agents = sorted({str(r.get("agent")) for r in rows})
        shares = {str(r.get("agent")): r.get("DS_t") for r in rows}
        ths = "".join(f"<th>{a}</th>" for a in agents)
        tds = "".join(f"<td>{_fmt_num(shares.get(a))}</td>" for a in agents)
        ds_sections.append(
            f"<h4>Day {d}</h4><table class=\"grid\"><thead><tr><th>Agent</th>{ths}</tr></thead>"
            f"<tbody><tr><th>DS_t</th>{tds}</tr></tbody></table>"
        )

    # Intraday SVGs per day
    intraday_sections = []
    for d, rows in sorted(intraday_by_day.items(), key=lambda kv: int(kv[0])):
        svg = _svg_for_day(d, rows)
        intraday_sections.append(f"<h4>Day {d}</h4>" + svg)

    explanations = """
<dl>
  <dt>Total dues S_t</dt>
  <dd>Sum of payment obligations maturing on day t.</dd>
  <dt>Min net liquidity \u0305M_t</dt>
  <dd>Minimum system net liquidity needed if obligations are perfectly offset; equals sum of debtor shortfalls max(0, F_i - I_i).</dd>
  <dt>Start-of-day money M_t</dt>
  <dd>System means-of-payment available at the start of day t (cash, deposits, reserves).</dd>
  <dt>Liquidity gap G_t</dt>
  <dd>Shortfall at the start of the day: max(0, \u0305M_t - M_t).</dd>
  <dt>Netting potential \u03B1_t</dt>
  <dd>Share of dues that can be cleared by circulation/netting: 1 - \u0305M_t / S_t.</dd>
  <dt>Operational peak M^peak_t</dt>
  <dd>Peak amount of money simultaneously out in circuit when replaying realized settlement sequence.</dd>
  <dt>Gross settled</dt>
  <dd>Total value actually settled on day t.</dd>
  <dt>Intraday velocity v_t</dt>
  <dd>How intensively money is reused intraday: gross settled / operational peak.</dd>
  <dt>On-time settlement \u03C6_t</dt>
  <dd>Share of dues with due_day=t that settle on day t.</dd>
  <dt>Deferral/default \u03B4_t</dt>
  <dd>1 - \u03C6_t (portion not settled on time; may reflect deferrals or defaults).</dd>
  <dt>Creditor HHI^+</dt>
  <dd>Concentration of net creditor positions among those with n_i > 0.</dd>
  <dt>Debtor shortfall shares DS_t(i)</dt>
  <dd>Each net debtor's share of \u0305M_t, indicating who needs liquidity.</dd>
</dl>
"""

    html = f"""
<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>{html_title}</title>
  <style>
    body {{ font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif; margin: 24px; color: #222; }}
    h1 {{ margin: 0 0 4px; font-size: 22px; }}
    h2 {{ margin-top: 28px; font-size: 18px; }}
    h3 {{ margin-top: 18px; font-size: 16px; }}
    h4 {{ margin-top: 12px; font-size: 14px; }}
    p.small {{ color: #555; margin-top: 4px; }}
    table.grid {{ border-collapse: collapse; width: 100%; margin-top: 8px; }}
    table.grid th, table.grid td {{ border: 1px solid #ddd; padding: 6px 8px; font-size: 13px; }}
    table.grid thead th {{ background: #f8f8f8; text-align: left; }}
    .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 8px; margin-top: 8px; }}
    .card {{ border: 1px solid #eee; padding: 10px; border-radius: 6px; background: #fcfcfc; }}
    .muted {{ color: #666; }}
    dl {{ display: grid; grid-template-columns: max-content 1fr; grid-gap: 4px 16px; font-size: 13px; }}
    dt {{ font-weight: 600; }}
    dd {{ margin: 0 0 8px 0; color: #333; }}
  </style>
  <meta name=\"generator\" content=\"Bilancio Analytics\" />
  <meta name=\"description\" content=\"Kalecki-style payment microstructure metrics\" />
  <meta name=\"robots\" content=\"noindex\" />
</head>
<body>
  <header>
    <h1>{html_title}</h1>
    {f'<p class="small muted">{html_sub}</p>' if html_sub else ''}
  </header>

  <section>
    <h2>Summary Across Days</h2>
    <div class=\"summary\">
      <div class=\"card\"><div class=\"muted\">Days analyzed</div><div><strong>{len(day_metrics)}</strong></div></div>
      <div class=\"card\"><div class=\"muted\">Total dues \u2211 S_t</div><div><strong>{_fmt_num(S_total)}</strong></div></div>
      <div class=\"card\"><div class=\"muted\">Gross settled total</div><div><strong>{_fmt_num(gross_total)}</strong></div></div>
      <div class=\"card\"><div class=\"muted\">Max operational peak</div><div><strong>{_fmt_num(Mpeak_max)}</strong></div></div>
      <div class=\"card\"><div class=\"muted\">Avg velocity</div><div><strong>{_fmt_num(v_avg)}</strong></div></div>
      <div class=\"card\"><div class=\"muted\">Weighted on-time \u03C6</div><div><strong>{_fmt_num(phi_weighted)}</strong></div></div>
    </div>
  </section>

  <section>
    <h2>Day-by-Day Metrics</h2>
    <table class=\"grid\">
      <thead>
        <tr>{day_table_head}</tr>
      </thead>
      <tbody>
        {''.join(day_table_rows)}
      </tbody>
    </table>
  </section>

  <section>
    <h2>Debtor Shortfall Shares DS_t(i)</h2>
    {''.join(ds_sections) if ds_sections else '<p class="muted">No net debtors on analyzed days.</p>'}
  </section>

  <section>
    <h2>Intraday Diagnostics: Prefix Liquidity P(s)</h2>
    <p class=\"small muted\">For each settlement sequence on day t, P(s) = \u2211_i max(0, \u0394_i(s)) and M^peak_t = max_s P(s).</p>
    {''.join(intraday_sections) if intraday_sections else '<p class="muted">No settlement steps found.</p>'}
  </section>

  <section>
    <h2>Metric Explanations</h2>
    {explanations}
  </section>
</body>
</html>
"""

    with p.open("w") as f:
        f.write(html)

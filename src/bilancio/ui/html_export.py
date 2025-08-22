"""Semantic HTML export for Bilancio runs (readable, non-monospace).

Generates a light-themed, spreadsheet-style HTML report inspired by temp/demo_correct.html,
without changing simulation logic.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from bilancio.engines.system import System
from bilancio.analysis.visualization import build_t_account_rows
from bilancio.analysis.balances import AgentBalance


CSS = """
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,'Helvetica Neue',Arial,sans-serif;line-height:1.6;color:#333;background:#f5f5f5}
.container{max-width:1400px;margin:0 auto;padding:20px}
header{background:#fff;border-radius:8px;padding:24px;margin-bottom:24px;box-shadow:0 2px 4px rgba(0,0,0,0.1)}
h1{color:#2563eb;font-size:28px;margin-bottom:8px}
h2{color:#475569;font-size:20px;margin-bottom:16px}
h3{color:#334155;font-size:18px;margin-bottom:12px}
h4{color:#475569;font-size:16px;margin:8px 0;font-weight:600}
.description{color:#64748b;font-style:italic;margin-bottom:16px}
.meta{display:flex;gap:24px;color:#64748b;font-size:14px}
.meta span{display:inline-block}
.t-account{background:#fff;border-radius:8px;padding:20px;margin-bottom:20px;box-shadow:0 2px 4px rgba(0,0,0,0.1)}
.t-account .grid{display:grid;grid-template-columns:1fr 1fr;gap:20px}
.t-account table.side{width:100%;border-collapse:collapse;font-size:14px}
.t-account th,.t-account td{border-bottom:1px solid #e5e7eb;border-right:1px solid #eef2f7;padding:8px;text-align:left}
.t-account th:last-child,.t-account td:last-child{border-right:none}
.t-account tbody tr:nth-child(even){background:#fafafa}
.t-account th{background:#f9fafb;font-weight:600;color:#374151}
.t-account td.qty,.t-account td.val,.t-account td.mat{text-align:right;white-space:nowrap}
.t-account td.name{font-weight:500}
.t-account td.empty{text-align:center;color:#9ca3af}
.assets-side h4{color:#16a34a}
.liabilities-side h4{color:#dc2626}
.events-table{background:#fff;border-radius:8px;padding:20px;margin-bottom:24px;box-shadow:0 2px 4px rgba(0,0,0,0.1)}
.events-table table{width:100%;border-collapse:collapse;font-size:14px}
.events-table th,.events-table td{border-bottom:1px solid #e5e7eb;border-right:1px solid #eef2f7;padding:8px;text-align:left}
.events-table th:last-child,.events-table td:last-child{border-right:none}
.events-table tbody tr:nth-child(even){background:#f7f9fc}
.events-table th{background:#f9fafb;font-weight:600;color:#374151}
.events-table td.qty,.events-table td.amount{text-align:center;white-space:nowrap}
.events-table td.event-kind{font-weight:500;color:#3b82f6}
.events-table td.notes{font-size:13px;color:#64748b}
.agents>h2{margin-bottom:20px;padding:0 20px}
.day-section{margin-bottom:40px;padding-bottom:40px;border-bottom:2px solid #e5e7eb}
.day-section:last-child{border-bottom:none}
.day-header{color:#1f2937;font-size:24px;margin-bottom:24px;padding:12px 0;border-bottom:1px solid #e5e7eb}
.events-section{margin-bottom:24px}
.balances-section{margin-top:24px}
.balances-section>h3{margin-bottom:20px;color:#374151;font-size:20px}
footer{text-align:center;color:#9ca3af;font-size:14px;margin-top:40px;padding:20px}
@media (max-width:768px){.t-account .grid{grid-template-columns:1fr}.meta{flex-direction:column;gap:8px}}
"""


def _html_escape(s: Any) -> str:
    return ("" if s is None else str(s)).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _format_amount(v: Any) -> str:
    if v in (None, "—", "-"):
        return "—"
    try:
        return f"{int(v):,}"
    except Exception:
        try:
            return f"{float(v):,.0f}"
        except Exception:
            return _html_escape(v)


def _render_t_account_from_rows(title: str, assets_rows: List[dict], liabs_rows: List[dict]) -> str:
    def tr(row: Optional[dict]) -> str:
        if not row:
            return "<tr><td class=\"empty\" colspan=\"5\">—</td></tr>"
        qty = row.get('quantity')
        val = row.get('value_minor')
        cpty = row.get('counterparty_name') or "—"
        mat = row.get('maturity') or "—"
        qty_s = "—" if qty in (None, "") else f"{int(qty):,}"
        val_s = "—" if val in (None, "") else f"{int(val):,}"
        return (
            f"<tr>"
            f"<td class=\"name\">{_html_escape(row.get('name',''))}</td>"
            f"<td class=\"qty\">{qty_s}</td>"
            f"<td class=\"val\">{val_s}</td>"
            f"<td class=\"cpty\">{_html_escape(cpty)}</td>"
            f"<td class=\"mat\">{_html_escape(mat)}</td>"
            f"</tr>"
        )

    assets_html = "".join(tr(r) for r in assets_rows) or tr(None)
    liabs_html = "".join(tr(r) for r in liabs_rows) or tr(None)

    return f"""
<section class="t-account">
  <h3>{_html_escape(title)}</h3>
  <div class="grid">
    <div class="assets-side">
      <h4>Assets</h4>
      <table class="side">
        <thead><tr><th>Name</th><th>Qty</th><th>Value</th><th>Counterparty</th><th>Maturity</th></tr></thead>
        <tbody>{assets_html}</tbody>
      </table>
    </div>
    <div class="liabilities-side">
      <h4>Liabilities</h4>
      <table class="side">
        <thead><tr><th>Name</th><th>Qty</th><th>Value</th><th>Counterparty</th><th>Maturity</th></tr></thead>
        <tbody>{liabs_html}</tbody>
      </table>
    </div>
  </div>
</section>
"""


def _render_t_account(system: System, agent_id: str) -> str:
    acct = build_t_account_rows(system, agent_id)
    agent = system.state.agents[agent_id]
    title = f"{agent.name or agent_id} [{agent_id}] ({agent.kind})"
    # Convert to dict rows for the row renderer
    def to_row(r):
        return {
            'name': getattr(r, 'name', ''),
            'quantity': getattr(r, 'quantity', None),
            'value_minor': getattr(r, 'value_minor', None),
            'counterparty_name': getattr(r, 'counterparty_name', None),
            'maturity': getattr(r, 'maturity', None),
        }
    assets_rows = [to_row(r) for r in acct.assets]
    liabs_rows = [to_row(r) for r in acct.liabilities]
    return _render_t_account_from_rows(title, assets_rows, liabs_rows)


def _build_rows_from_balance(balance: AgentBalance) -> (List[dict], List[dict]):
    assets: List[dict] = []
    liabs: List[dict] = []

    # Inventory (stocks owned)
    for sku, data in balance.inventory_by_sku.items():
        qty = data.get('quantity', 0)
        val = data.get('value', 0)
        try:
            val_i = int(val)
        except Exception:
            val_i = int(float(val)) if val is not None else None
        if qty and qty > 0:
            assets.append({'name': str(sku), 'quantity': int(qty), 'value_minor': val_i, 'counterparty_name': '—', 'maturity': '—'})

    # Non-financial assets receivable
    for sku, data in balance.nonfinancial_assets_by_kind.items():
        qty = data.get('quantity', 0)
        val = data.get('value', 0)
        try:
            val_i = int(val)
        except Exception:
            val_i = int(float(val)) if val is not None else None
        if qty and qty > 0:
            assets.append({'name': f"{sku} receivable", 'quantity': int(qty), 'value_minor': val_i, 'counterparty_name': '—', 'maturity': '—'})

    # Financial assets by kind (skip non-financial kinds)
    for kind, amount in balance.assets_by_kind.items():
        if kind == 'delivery_obligation':
            continue
        if amount and amount > 0:
            assets.append({'name': kind, 'quantity': None, 'value_minor': int(amount), 'counterparty_name': '—', 'maturity': 'on-demand' if kind in ('cash','bank_deposit','reserve_deposit') else '—'})

    # Non-financial liabilities
    for sku, data in balance.nonfinancial_liabilities_by_kind.items():
        qty = data.get('quantity', 0)
        val = data.get('value', 0)
        try:
            val_i = int(val)
        except Exception:
            val_i = int(float(val)) if val is not None else None
        if qty and qty > 0:
            liabs.append({'name': f"{sku} obligation", 'quantity': int(qty), 'value_minor': val_i, 'counterparty_name': '—', 'maturity': '—'})

    # Financial liabilities
    for kind, amount in balance.liabilities_by_kind.items():
        if kind == 'delivery_obligation':
            continue
        if amount and amount > 0:
            liabs.append({'name': kind, 'quantity': None, 'value_minor': int(amount), 'counterparty_name': '—', 'maturity': 'on-demand' if kind in ('cash','bank_deposit','reserve_deposit') else '—'})

    # Ordering similar to render layer
    def asset_key(row):
        name = row['name']
        # inventory rows have quantity and cpty/maturity '—'
        if row['quantity'] is not None and row.get('counterparty_name') == '—':
            return (0, name)
        if name.endswith('receivable'):
            return (1, name)
        order = {'cash':0,'bank_deposit':1,'reserve_deposit':2,'payable':3}
        return (2, order.get(name, 99), name)

    def liab_key(row):
        name = row['name']
        if name.endswith('obligation'):
            return (0, name)
        order = {'payable':0,'bank_deposit':1,'reserve_deposit':2,'cash':3}
        return (1, order.get(name, 99), name)

    assets.sort(key=asset_key)
    liabs.sort(key=liab_key)
    return assets, liabs


def _map_event_fields(e: Dict[str, Any]) -> Dict[str, str]:
    kind = str(e.get("kind", ""))
    if kind in ("CashDeposited", "CashWithdrawn"):
        frm = e.get("customer") if kind == "CashDeposited" else e.get("bank")
        to = e.get("bank") if kind == "CashDeposited" else e.get("customer")
    elif kind in ("ClientPayment", "IntraBankPayment", "CashPayment"):
        frm = e.get("payer"); to = e.get("payee")
    elif kind in ("InterbankCleared", "InterbankOvernightCreated"):
        frm = e.get("debtor_bank"); to = e.get("creditor_bank")
    elif kind == "StockCreated":
        frm = e.get("owner"); to = None
    else:
        frm = e.get("frm") or e.get("from") or e.get("debtor") or e.get("payer")
        to  = e.get("to") or e.get("creditor") or e.get("payee")
    sku = e.get("sku") or e.get("instr_id") or e.get("stock_id") or "—"
    qty = e.get("qty") or e.get("quantity") or "—"
    amt = e.get("amount") or "—"
    notes = ""
    if kind == "ClientPayment":
        notes = f"{e.get('payer_bank','?')} → {e.get('payee_bank','?')}"
    elif kind in ("InterbankCleared", "InterbankOvernightCreated"):
        notes = f"{e.get('debtor_bank','?')} → {e.get('creditor_bank','?')}"
        if 'due_day' in e:
            notes += f"; due {e.get('due_day')}"
    return {
        "kind": kind,
        "from": _html_escape(frm or "—"),
        "to": _html_escape(to or "—"),
        "sku": _html_escape(sku),
        "qty": _html_escape(qty),
        "amount": _format_amount(amt),
        "notes": _html_escape(notes),
    }


def _render_events_table(title: str, events: List[Dict[str, Any]]) -> str:
    # Exclude marker rows
    events = [e for e in events if e.get("kind") not in ("PhaseA","PhaseB","PhaseC")]
    rows_html = []
    for e in events:
        m = _map_event_fields(e)
        rows_html.append(
            f"<tr>"
            f"<td class=\"event-kind\">{m['kind']}</td>"
            f"<td>{m['from']}</td><td>{m['to']}</td>"
            f"<td>{m['sku']}</td><td class=\"qty\">{m['qty']}</td>"
            f"<td class=\"amount\">{m['amount']}</td><td class=\"notes\">{m['notes']}</td>"
            f"</tr>"
        )
    if not rows_html:
        rows_html.append("<tr><td colspan=\"7\" class=\"notes\">No events</td></tr>")
    return f"""
<section class="events-table">
  <h4>{_html_escape(title)}</h4>
  <table>
    <thead>
      <tr><th>Kind</th><th>From</th><th>To</th><th>SKU/Instr</th><th>Qty</th><th>Amount</th><th>Notes</th></tr>
    </thead>
    <tbody>
      {''.join(rows_html)}
    </tbody>
  </table>
</section>
"""


def _split_by_phases(day_events: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    buckets = {"A": [], "B": [], "C": []}
    current = "A"
    for e in day_events:
        k = e.get("kind")
        if k == "PhaseA":
            current = "A"; continue
        if k == "PhaseB":
            current = "B"; continue
        if k == "PhaseC":
            current = "C"; continue
        buckets[current].append(e)
    return buckets


def export_pretty_html(
    system: System,
    out_path: Path,
    scenario_name: str,
    description: Optional[str],
    agent_ids: Optional[List[str]],
    initial_balances: Optional[Dict[str, Any]],
    days_data: List[Dict[str, Any]],
    *,
    max_days: Optional[int] = None,
    quiet_days: Optional[int] = None,
    initial_rows: Optional[Dict[str, Dict[str, List[dict]]]] = None,
) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Meta
    final_day = system.state.day
    total_events = len(system.state.events)
    active_agents = len(system.state.agents)
    active_contracts = len(system.state.contracts)

    # Determine convergence robustly: check tail quiet days and open obligations
    def _has_open_obligations() -> bool:
        try:
            return any(c.kind in ("payable", "delivery_obligation") for c in system.state.contracts.values())
        except Exception:
            return False
    has_open = _has_open_obligations()
    tail_quiet_ok = False
    end_day = None
    if days_data:
        end_day = days_data[-1].get('day')
        if quiet_days is not None and len(days_data) >= quiet_days:
            tail = [d.get('quiet') for d in days_data[-quiet_days:]]
            tail_quiet_ok = all(bool(x) for x in tail)

    html_parts: List[str] = []
    html_parts.append("<!DOCTYPE html><html lang=\"en\"><head><meta charset=\"UTF-8\">")
    html_parts.append("<meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">")
    html_parts.append(f"<title>Bilancio Simulation - { _html_escape(scenario_name) }</title>")
    html_parts.append(f"<style>{CSS}</style></head><body>")
    html_parts.append("<div class=\"container\">")
    html_parts.append("<header>")
    html_parts.append("<h1>Bilancio Simulation</h1>")
    html_parts.append(f"<h2>{_html_escape(scenario_name)}</h2>")
    if description:
        html_parts.append(f"<p class=\"description\">{_html_escape(description)}</p>")
    # Status line (converged or not)
    converged = (tail_quiet_ok and not has_open)
    status_text = "Converged" if converged else "Stopped without convergence"
    if converged and end_day is not None:
        status_text = f"Converged on day {end_day}"
    elif (not converged) and max_days is not None:
        status_text = f"Stopped without convergence (max_days = {max_days})"
    html_parts.append(
        f"<div class=\"meta\"><span>Final Day: {final_day}</span>"
        f"<span>Total Events: {total_events}</span>"
        f"<span>Active Agents: {active_agents}</span>"
        f"<span>Active Contracts: {active_contracts}</span>"
        f"<span>Status: {status_text}</span></div>"
    )
    html_parts.append("</header><main>")

    # Agents table
    html_parts.append("<section class=\"agents\"><h2>Agents</h2>")
    html_parts.append("<section class=\"events-table\"><table><thead><tr><th>ID</th><th>Name</th><th>Type</th></tr></thead><tbody>")
    for aid, agent in system.state.agents.items():
        name = _html_escape(agent.name or aid)
        kind = _html_escape(agent.kind)
        html_parts.append(f"<tr><td>{_html_escape(aid)}</td><td>{name}</td><td>{kind}</td></tr>")
    html_parts.append("</tbody></table></section></section>")

    # Day 0 (Setup)
    html_parts.append("<section class=\"day-section\"><h2 class=\"day-header\">📅 Day 0 (Setup)</h2>")
    setup_events = [e for e in system.state.events if e.get("phase") == "setup"]
    html_parts.append("<div class=\"events-section\"><h3>Setup Events</h3>")
    html_parts.append(_render_events_table("Setup", setup_events))
    html_parts.append("</div>")
    if agent_ids and initial_balances:
        html_parts.append("<div class=\"balances-section\"><h3>Balances</h3>")
        for aid in agent_ids:
            # Prefer captured initial_rows for detailed counterparties
            if initial_rows and aid in initial_rows:
                ag = system.state.agents[aid]
                title = f"{ag.name or aid} [{aid}] ({ag.kind})"
                rows = initial_rows[aid]
                html_parts.append(_render_t_account_from_rows(title, rows.get('assets', []), rows.get('liabs', [])))
            else:
                bal = initial_balances.get(aid)
                if isinstance(bal, AgentBalance):
                    assets_rows, liabs_rows = _build_rows_from_balance(bal)
                    ag = system.state.agents[aid]
                    title = f"{ag.name or aid} [{aid}] ({ag.kind})"
                    html_parts.append(_render_t_account_from_rows(title, assets_rows, liabs_rows))
                else:
                    html_parts.append(_render_t_account(system, aid))
        html_parts.append("</div>")
    html_parts.append("</section>")

    # Subsequent days from days_data (already chronological)
    for d in days_data:
        day_num = d.get('day')
        html_parts.append(f"<section class=\"day-section\"><h2 class=\"day-header\">📅 Day {day_num}</h2>")
        ev = d.get('events', [])
        buckets = _split_by_phases(ev)
        html_parts.append("<div class=\"events-section\">")
        html_parts.append(_render_events_table("Phase B — Settlement", buckets.get("B", [])))
        html_parts.append(_render_events_table("Phase C — Clearing", buckets.get("C", [])))
        html_parts.append("</div>")
        if agent_ids:
            html_parts.append("<div class=\"balances-section\"><h3>Balances</h3>")
            day_balances = d.get('balances') or {}
            day_rows = d.get('rows') or {}
            for aid in agent_ids:
                # Prefer captured rows with counterparties for this day
                if aid in day_rows:
                    rows = day_rows[aid]
                    ag = system.state.agents[aid]
                    title = f"{ag.name or aid} [{aid}] ({ag.kind})"
                    html_parts.append(_render_t_account_from_rows(title, rows.get('assets', []), rows.get('liabs', [])))
                else:
                    bal = day_balances.get(aid)
                    if isinstance(bal, AgentBalance):
                        assets_rows, liabs_rows = _build_rows_from_balance(bal)
                        ag = system.state.agents[aid]
                        title = f"{ag.name or aid} [{aid}] ({ag.kind})"
                        html_parts.append(_render_t_account_from_rows(title, assets_rows, liabs_rows))
                    else:
                        html_parts.append(_render_t_account(system, aid))
            html_parts.append("</div>")
        html_parts.append("</section>")

    # Conclusion section with termination reason
    html_parts.append("<section class=\"events-table\">")
    html_parts.append("<h3>Simulation End</h3>")
    if converged and end_day is not None:
        qtxt = f" after {quiet_days} quiet days" if quiet_days is not None else ""
        html_parts.append(
            f"<p>The system converged on day <strong>{end_day}</strong>{qtxt}: no impactful events and no open obligations.</p>"
        )
    else:
        mtxt = f" (max_days = {max_days})" if max_days is not None else ""
        html_parts.append(
            f"<p>Stopped without convergence{mtxt}. Consider increasing max days or reviewing outstanding obligations.</p>"
        )
    html_parts.append("</section>")

    html_parts.append("</main><footer>Generated by Bilancio</footer></div></body></html>")

    out_path.write_text("".join(html_parts), encoding="utf-8")

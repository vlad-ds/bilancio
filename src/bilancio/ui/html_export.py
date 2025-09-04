"""Semantic HTML export for Bilancio runs (readable, non-monospace).

Generates a light-themed, spreadsheet-style HTML report inspired by temp/demo_correct.html,
without changing simulation logic.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional
import math
from decimal import Decimal
import html as _html

from bilancio.engines.system import System
from bilancio.analysis.visualization import build_t_account_rows
from bilancio.analysis.balances import AgentBalance


def _load_css() -> str:
    """Load export CSS from assets with a safe inline fallback.

    Keeps styling out of Python while remaining robust if the file is missing.
    """
    asset_path = Path(__file__).with_name("assets").joinpath("export.css")
    try:
        return asset_path.read_text(encoding="utf-8")
    except Exception:
        # Minimal fallback to keep the page readable if asset is missing.
        return "body{font-family:system-ui,Arial,sans-serif;padding:16px;background:#f5f5f5;color:#333}table{border-collapse:collapse;width:100%}th,td{border:1px solid #e5e7eb;padding:6px}tbody tr:nth-child(even){background:#fafafa}h1,h2,h3{margin:.5rem 0}"


def _html_escape(value: Any) -> str:
    """Escape text for safe HTML display, including quotes.

    Uses stdlib html.escape and additionally escapes single quotes.
    """
    if value is None:
        return ""
    text = str(value)
    # html.escape handles & < > and ", then we also escape single quotes
    return _html.escape(text, quote=True).replace("'", "&#x27;")


def _safe_int_conversion(value: Any) -> Optional[int]:
    """Safely convert value to int.

    - Accepts int, float, Decimal, and stringified digits
    - Returns None for None
    - Raises ValueError for invalid values
    """
    if value is None:
        return None
    # Fast path for ints
    if isinstance(value, int):
        return value
    # Floats/Decimals lose precision but we accept truncation for display
    if isinstance(value, (float, Decimal)):
        # Guard against NaN/Inf
        if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
            raise ValueError("Invalid numeric value: NaN/Inf")
        return int(value)
    # Strings: allow simple digit strings and formatted numbers with commas
    if isinstance(value, str):
        s = value.strip().replace(",", "")
        if s == "":
            return None
        try:
            return int(s)
        except Exception as e:
            raise ValueError(f"Invalid numeric value: {value}") from e
    # Objects with __int__
    if hasattr(value, "__int__"):
        try:
            return int(value)  # type: ignore[arg-type]
        except Exception as e:
            raise ValueError(f"Invalid numeric value: {value}") from e
    raise ValueError(f"Cannot convert {type(value)} to int")


def _format_amount(v: Any) -> str:
    if v in (None, "—", "-"):
        return "—"
    try:
        iv = _safe_int_conversion(v)
        if iv is None:
            return "—"
        return f"{iv:,}"
    except ValueError:
        # As a last resort, try float -> int formatting without erroring
        try:
            return f"{int(float(v)):,}"
        except Exception:
            return _html_escape(v)


def _render_t_account_from_rows(title: str, assets_rows: List[dict], liabs_rows: List[dict]) -> str:
    def tr(row: Optional[dict]) -> str:
        if not row:
            return "<tr><td class=\"empty\" colspan=\"6\">—</td></tr>"
        qty = row.get('quantity')
        val = row.get('value_minor')
        cpty = row.get('counterparty_name') or "—"
        mat = row.get('maturity') or "—"
        id_or_alias = row.get('id_or_alias') or "—"
        # Robust numeric formatting with safe conversion
        try:
            qiv = _safe_int_conversion(qty)
        except ValueError:
            qiv = None
        try:
            viv = _safe_int_conversion(val)
        except ValueError:
            viv = None
        qty_s = "—" if qiv in (None, "") else f"{qiv:,}"
        val_s = "—" if viv in (None, "") else f"{viv:,}"
        return (
            f"<tr>"
            f"<td class=\"name\">{_html_escape(row.get('name',''))}</td>"
            f"<td class=\"id\">{_html_escape(id_or_alias)}</td>"
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
        <thead><tr><th>Name</th><th>ID/Alias</th><th>Qty</th><th>Value</th><th>Counterparty</th><th>Maturity</th></tr></thead>
        <tbody>{assets_html}</tbody>
      </table>
    </div>
    <div class="liabilities-side">
      <h4>Liabilities</h4>
      <table class="side">
        <thead><tr><th>Name</th><th>ID/Alias</th><th>Qty</th><th>Value</th><th>Counterparty</th><th>Maturity</th></tr></thead>
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
            'id_or_alias': getattr(r, 'id_or_alias', None),
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
            val_i = _safe_int_conversion(val)
        except ValueError:
            val_i = None
        try:
            qty_i = _safe_int_conversion(qty)
        except ValueError:
            qty_i = None
        if qty_i and qty_i > 0:
            assets.append({'name': str(sku), 'quantity': qty_i, 'value_minor': val_i, 'counterparty_name': '—', 'maturity': '—'})

    # Non-financial assets receivable
    for sku, data in balance.nonfinancial_assets_by_kind.items():
        qty = data.get('quantity', 0)
        val = data.get('value', 0)
        try:
            val_i = _safe_int_conversion(val)
        except ValueError:
            val_i = None
        try:
            qty_i = _safe_int_conversion(qty)
        except ValueError:
            qty_i = None
        if qty_i and qty_i > 0:
            assets.append({'name': f"{sku} receivable", 'quantity': qty_i, 'value_minor': val_i, 'counterparty_name': '—', 'maturity': '—'})

    # Financial assets by kind (skip non-financial kinds)
    for kind, amount in balance.assets_by_kind.items():
        if kind == 'delivery_obligation':
            continue
        try:
            amount_i = _safe_int_conversion(amount)
        except ValueError:
            amount_i = None
        if amount_i and amount_i > 0:
            assets.append({'name': kind, 'quantity': None, 'value_minor': amount_i, 'counterparty_name': '—', 'maturity': 'on-demand' if kind in ('cash','bank_deposit','reserve_deposit') else '—'})

    # Non-financial liabilities
    for sku, data in balance.nonfinancial_liabilities_by_kind.items():
        qty = data.get('quantity', 0)
        val = data.get('value', 0)
        try:
            val_i = _safe_int_conversion(val)
        except ValueError:
            val_i = None
        try:
            qty_i = _safe_int_conversion(qty)
        except ValueError:
            qty_i = None
        if qty_i and qty_i > 0:
            liabs.append({'name': f"{sku} obligation", 'quantity': qty_i, 'value_minor': val_i, 'counterparty_name': '—', 'maturity': '—'})

    # Financial liabilities
    for kind, amount in balance.liabilities_by_kind.items():
        if kind == 'delivery_obligation':
            continue
        try:
            amount_i = _safe_int_conversion(amount)
        except ValueError:
            amount_i = None
        if amount_i and amount_i > 0:
            liabs.append({'name': kind, 'quantity': None, 'value_minor': amount_i, 'counterparty_name': '—', 'maturity': 'on-demand' if kind in ('cash','bank_deposit','reserve_deposit') else '—'})

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
    # Identifier column prefers alias, then contract/instrument IDs
    id_or_alias = (
        e.get("alias")
        or e.get("contract_id")
        or e.get("payable_id")
        or e.get("id")
        or e.get("instr_id")
        or e.get("stock_id")
        or "—"
    )
    # SKU/Instr column should show SKU (for stock/delivery events) when available
    # Otherwise leave blank/dash
    sku = e.get("sku") or "—"
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
        "id_or_alias": _html_escape(id_or_alias),
        "sku": _html_escape(sku),
        "qty": _html_escape(qty),
        "amount": _format_amount(amt),
        "notes": _html_escape(notes),
    }


def _render_events_table(title: str, events: List[Dict[str, Any]]) -> str:
    # Exclude marker rows
    events = [e for e in events if e.get("kind") not in ("PhaseA","PhaseB","PhaseC","SubphaseB1","SubphaseB2")]
    rows_html = []
    for e in events:
        m = _map_event_fields(e)
        rows_html.append(
            f"<tr>"
            f"<td class=\"event-kind\">{m['kind']}</td>"
            f"<td class=\"event-id\">{m['id_or_alias']}</td>"
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
      <tr><th>Kind</th><th>ID/Alias</th><th>From</th><th>To</th><th>SKU/Instr</th><th>Qty</th><th>Amount</th><th>Notes</th></tr>
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

def _split_phase_b_into_subphases(events_b: List[Dict[str, Any]]) -> (List[Dict[str, Any]], List[Dict[str, Any]]):
    """Split Phase B events into B1 (scheduled) and B2 (settlements) using subphase markers.

    Excludes Subphase markers from returned lists.
    """
    b1: List[Dict[str, Any]] = []
    b2: List[Dict[str, Any]] = []
    in_b2 = False
    for e in events_b:
        k = e.get("kind")
        if k == "SubphaseB1":
            # begin B1 (marker only)
            in_b2 = False
            continue
        if k == "SubphaseB2":
            # switch to B2 (marker only)
            in_b2 = True
            continue
        if in_b2:
            b2.append(e)
        else:
            b1.append(e)
    return b1, b2


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
    html_parts.append(f"<style>{_load_css()}</style></head><body>")
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
        b1, b2 = _split_phase_b_into_subphases(buckets.get("B", []))
        html_parts.append(_render_events_table("Phase B1 — Scheduled Actions", b1))
        html_parts.append(_render_events_table("Phase B2 — Settlement", b2))
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

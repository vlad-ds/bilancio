"""Command-line interface for Bilancio."""

import click
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Optional
import sys

from click.core import ParameterSource

from rich.console import Console
from rich.panel import Panel

from .run import run_scenario
from .wizard import create_scenario_wizard
from bilancio.analysis.loaders import read_events_jsonl, read_balances_csv
from bilancio.analysis.report import (
    write_day_metrics_csv,
    write_day_metrics_json,
    write_debtor_shares_csv,
    write_intraday_csv,
    write_metrics_html,
    compute_day_metrics,
    parse_day_ranges,
    aggregate_runs,
    render_dashboard,
)
from bilancio.experiments.ring import (
    RingSweepRunner,
    RingSweepConfig,
    load_ring_sweep_config,
    _decimal_list,
)
# Comparison imports deferred to avoid circular import
# from bilancio.experiments.comparison import ComparisonSweepRunner, ComparisonSweepConfig


console = Console()


def _as_decimal_list(value):
    if isinstance(value, (list, tuple)):
        return [Decimal(str(item)) for item in value]
    return _decimal_list(value)


@click.group()
def cli():
    """Bilancio - Economic simulation framework."""
    pass


@cli.group()
def sweep():
    """Experiment sweeps."""
    pass


@sweep.command("ring")
@click.option('--config', type=click.Path(path_type=Path), default=None, help='Path to sweep config YAML')
@click.option('--out-dir', type=click.Path(path_type=Path), default=None, help='Base output directory')
@click.option('--grid/--no-grid', default=True, help='Run coarse grid sweep')
@click.option('--kappas', type=str, default="0.25,0.5,1,2,4", help='Comma list for grid kappa values')
@click.option('--concentrations', type=str, default="0.2,0.5,1,2,5", help='Comma list for grid Dirichlet concentrations')
@click.option('--mus', type=str, default="0,0.25,0.5,0.75,1", help='Comma list for grid mu values')
@click.option('--monotonicities', type=str, default="0", help='Comma list for grid monotonicity values')
@click.option('--lhs', 'lhs_count', type=int, default=0, help='Latin Hypercube samples to draw')
@click.option('--kappa-min', type=float, default=0.2, help='LHS min kappa')
@click.option('--kappa-max', type=float, default=5.0, help='LHS max kappa')
@click.option('--c-min', type=float, default=0.2, help='LHS min concentration')
@click.option('--c-max', type=float, default=5.0, help='LHS max concentration')
@click.option('--mu-min', type=float, default=0.0, help='LHS min mu')
@click.option('--mu-max', type=float, default=1.0, help='LHS max mu')
@click.option('--monotonicity-min', type=float, default=0.0, help='LHS min monotonicity')
@click.option('--monotonicity-max', type=float, default=0.0, help='LHS max monotonicity')
@click.option('--frontier/--no-frontier', default=False, help='Run frontier search')
@click.option('--frontier-low', type=float, default=0.1, help='Frontier lower bound for kappa')
@click.option('--frontier-high', type=float, default=4.0, help='Initial frontier upper bound for kappa')
@click.option('--frontier-tolerance', type=float, default=0.02, help='Frontier tolerance on delta_total')
@click.option('--frontier-iterations', type=int, default=6, help='Max bisection iterations per cell')
@click.option('--n-agents', type=int, default=5, help='Ring size')
@click.option('--maturity-days', type=int, default=3, help='Due day horizon for generator')
@click.option('--q-total', type=float, default=500.0, help='Total dues S1 for generation')
@click.option('--liquidity-mode', type=click.Choice(['single_at', 'uniform']), default='single_at', help='Liquidity allocation mode')
@click.option('--liquidity-agent', type=str, default='H1', help='Target for single_at liquidity allocation')
@click.option('--base-seed', type=int, default=42, help='Base PRNG seed')
@click.option('--name-prefix', type=str, default='Kalecki Ring Sweep', help='Scenario name prefix')
@click.option('--default-handling', type=click.Choice(['fail-fast', 'expel-agent']), default='fail-fast', help='Default handling mode for runs')
@click.pass_context
def sweep_ring(
    ctx,
    config: Optional[Path],
    out_dir: Optional[Path],
    grid: bool,
    kappas: str,
    concentrations: str,
    mus: str,
    monotonicities: str,
    lhs_count: int,
    kappa_min: float,
    kappa_max: float,
    c_min: float,
    c_max: float,
    mu_min: float,
    mu_max: float,
    monotonicity_min: float,
    monotonicity_max: float,
    frontier: bool,
    frontier_low: float,
    frontier_high: float,
    frontier_tolerance: float,
    frontier_iterations: int,
    n_agents: int,
    maturity_days: int,
    q_total: float,
    liquidity_mode: str,
    liquidity_agent: str,
    base_seed: int,
    name_prefix: str,
    default_handling: str,
):
    """Run the Kalecki ring experiment sweep."""
    sweep_config: Optional[RingSweepConfig] = None
    if config is not None:
        sweep_config = load_ring_sweep_config(config)

    def _using_default(param_name: str) -> bool:
        source = ctx.get_parameter_source(param_name)
        return source in (ParameterSource.DEFAULT, ParameterSource.DEFAULT_MAP)

    if sweep_config is not None and sweep_config.out_dir and _using_default("out_dir"):
        out_dir = Path(sweep_config.out_dir)

    dealer_enabled = False
    dealer_config = None
    if sweep_config is not None and sweep_config.runner is not None:
        runner_cfg = sweep_config.runner
        if runner_cfg.n_agents is not None and _using_default("n_agents"):
            n_agents = runner_cfg.n_agents
        if runner_cfg.maturity_days is not None and _using_default("maturity_days"):
            maturity_days = runner_cfg.maturity_days
        if runner_cfg.q_total is not None and _using_default("q_total"):
            q_total = float(runner_cfg.q_total)
        if runner_cfg.liquidity_mode is not None and _using_default("liquidity_mode"):
            liquidity_mode = runner_cfg.liquidity_mode
        if runner_cfg.liquidity_agent is not None and _using_default("liquidity_agent"):
            liquidity_agent = runner_cfg.liquidity_agent
        if runner_cfg.base_seed is not None and _using_default("base_seed"):
            base_seed = runner_cfg.base_seed
        if runner_cfg.name_prefix is not None and _using_default("name_prefix"):
            name_prefix = runner_cfg.name_prefix
        if runner_cfg.default_handling is not None and _using_default("default_handling"):
            default_handling = runner_cfg.default_handling
        dealer_enabled = runner_cfg.dealer_enabled
        dealer_config = runner_cfg.dealer_config

    if sweep_config is not None and sweep_config.grid is not None:
        grid_cfg = sweep_config.grid
        if _using_default("grid"):
            grid = grid_cfg.enabled
        if grid_cfg.kappas and _using_default("kappas"):
            kappas = grid_cfg.kappas
        if grid_cfg.concentrations and _using_default("concentrations"):
            concentrations = grid_cfg.concentrations
        if grid_cfg.mus and _using_default("mus"):
            mus = grid_cfg.mus
        if grid_cfg.monotonicities and _using_default("monotonicities"):
            monotonicities = grid_cfg.monotonicities

    if sweep_config is not None and sweep_config.lhs is not None:
        lhs_cfg = sweep_config.lhs
        if _using_default("lhs_count"):
            lhs_count = lhs_cfg.count
        if lhs_cfg.kappa_range is not None:
            if _using_default("kappa_min"):
                kappa_min = float(lhs_cfg.kappa_range[0])
            if _using_default("kappa_max"):
                kappa_max = float(lhs_cfg.kappa_range[1])
        if lhs_cfg.concentration_range is not None:
            if _using_default("c_min"):
                c_min = float(lhs_cfg.concentration_range[0])
            if _using_default("c_max"):
                c_max = float(lhs_cfg.concentration_range[1])
        if lhs_cfg.mu_range is not None:
            if _using_default("mu_min"):
                mu_min = float(lhs_cfg.mu_range[0])
            if _using_default("mu_max"):
                mu_max = float(lhs_cfg.mu_range[1])
        if lhs_cfg.monotonicity_range is not None:
            if _using_default("monotonicity_min"):
                monotonicity_min = float(lhs_cfg.monotonicity_range[0])
            if _using_default("monotonicity_max"):
                monotonicity_max = float(lhs_cfg.monotonicity_range[1])

    if sweep_config is not None and sweep_config.frontier is not None:
        frontier_cfg = sweep_config.frontier
        if _using_default("frontier"):
            frontier = frontier_cfg.enabled
        if frontier_cfg.enabled:
            if frontier_cfg.kappa_low is not None and _using_default("frontier_low"):
                frontier_low = float(frontier_cfg.kappa_low)
            if frontier_cfg.kappa_high is not None and _using_default("frontier_high"):
                frontier_high = float(frontier_cfg.kappa_high)
            if frontier_cfg.tolerance is not None and _using_default("frontier_tolerance"):
                frontier_tolerance = float(frontier_cfg.tolerance)
            if frontier_cfg.max_iterations is not None and _using_default("frontier_iterations"):
                frontier_iterations = frontier_cfg.max_iterations

    if out_dir is not None and not isinstance(out_dir, Path):
        out_dir = Path(out_dir)

    if out_dir is None:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_dir = Path("out") / "experiments" / f"{ts}_ring"

    out_dir.mkdir(parents=True, exist_ok=True)

    q_total_dec = Decimal(str(q_total))
    runner = RingSweepRunner(
        out_dir,
        name_prefix=name_prefix,
        n_agents=n_agents,
        maturity_days=maturity_days,
        Q_total=q_total_dec,
        liquidity_mode=liquidity_mode,
        liquidity_agent=liquidity_agent,
        base_seed=base_seed,
        default_handling=default_handling,
        dealer_enabled=dealer_enabled,
        dealer_config=dealer_config,
    )

    console.print(f"[dim]Output directory: {out_dir}[/dim]")

    grid_kappas = _as_decimal_list(kappas)
    grid_concentrations = _as_decimal_list(concentrations)
    grid_mus = _as_decimal_list(mus)
    grid_monotonicities = _as_decimal_list(monotonicities)

    if grid:
        total_runs = len(grid_kappas) * len(grid_concentrations) * len(grid_mus) * len(grid_monotonicities)
        console.print(f"[dim]Running grid sweep: {total_runs} runs[/dim]")
        runner.run_grid(grid_kappas, grid_concentrations, grid_mus, grid_monotonicities)

    if lhs_count > 0:
        console.print(f"[dim]Running Latin Hypercube ({lhs_count})[/dim]")
        runner.run_lhs(
            lhs_count,
            kappa_range=(Decimal(str(kappa_min)), Decimal(str(kappa_max))),
            concentration_range=(Decimal(str(c_min)), Decimal(str(c_max))),
            mu_range=(Decimal(str(mu_min)), Decimal(str(mu_max))),
            monotonicity_range=(Decimal(str(monotonicity_min)), Decimal(str(monotonicity_max))),
        )

    if frontier:
        console.print(f"[dim]Running frontier search across {len(grid_concentrations) * len(grid_mus) * len(grid_monotonicities)} cells[/dim]")
        runner.run_frontier(
            grid_concentrations,
            grid_mus,
            grid_monotonicities,
            kappa_low=Decimal(str(frontier_low)),
            kappa_high=Decimal(str(frontier_high)),
            tolerance=Decimal(str(frontier_tolerance)),
            max_iterations=frontier_iterations,
        )

    registry_csv = runner.registry_dir / "experiments.csv"
    results_csv = runner.aggregate_dir / "results.csv"
    dashboard_html = runner.aggregate_dir / "dashboard.html"

    aggregate_runs(registry_csv, results_csv)
    render_dashboard(results_csv, dashboard_html)

    console.print(f"[green]Sweep complete.[/green] Registry: {registry_csv}")
    console.print(f"[green]Aggregated results: {results_csv}")
    console.print(f"[green]Dashboard: {dashboard_html}")


@sweep.command("comparison")
@click.option('--out-dir', type=click.Path(path_type=Path), required=True, help='Output directory for results')
@click.option('--n-agents', type=int, default=100, help='Ring size (default: 100)')
@click.option('--maturity-days', type=int, default=10, help='Maturity horizon in days (default: 10)')
@click.option('--q-total', type=float, default=10000.0, help='Total debt amount (default: 10000)')
@click.option('--kappas', type=str, default="0.25,0.5,1,2,4", help='Comma list for kappa values')
@click.option('--concentrations', type=str, default="0.2,0.5,1,2,5", help='Comma list for Dirichlet concentrations')
@click.option('--mus', type=str, default="0,0.25,0.5,0.75,1", help='Comma list for mu values')
@click.option('--monotonicities', type=str, default="0", help='Comma list for monotonicity values')
@click.option('--base-seed', type=int, default=42, help='Base PRNG seed')
@click.option('--default-handling', type=click.Choice(['fail-fast', 'expel-agent']), default='fail-fast', help='Default handling mode')
@click.option('--dealer-ticket-size', type=float, default=1.0, help='Ticket size for dealer')
@click.option('--dealer-share', type=float, default=0.25, help='Dealer capital as fraction of system cash (NEW outside money)')
@click.option('--vbt-share', type=float, default=0.50, help='VBT capital as fraction of system cash (NEW outside money)')
@click.option('--liquidity-mode', type=click.Choice(['single_at', 'uniform']), default='uniform', help='Liquidity allocation mode')
@click.option('--liquidity-agent', type=str, default=None, help='Target agent for single_at mode')
@click.option('--name-prefix', type=str, default='Dealer Comparison', help='Scenario name prefix')
def sweep_comparison(
    out_dir: Path,
    n_agents: int,
    maturity_days: int,
    q_total: float,
    kappas: str,
    concentrations: str,
    mus: str,
    monotonicities: str,
    base_seed: int,
    default_handling: str,
    dealer_ticket_size: float,
    dealer_share: float,
    vbt_share: float,
    liquidity_mode: str,
    liquidity_agent: Optional[str],
    name_prefix: str,
):
    """
    Run dealer comparison experiments.

    For each parameter combination (κ, c, μ), runs:
    1. Control: No dealer (baseline)
    2. Treatment: With dealer

    Outputs comparison metrics showing the delta in defaults between conditions.
    """
    import logging
    logging.basicConfig(level=logging.INFO, format='%(message)s')

    # Deferred import to avoid circular import
    from bilancio.experiments.comparison import ComparisonSweepRunner, ComparisonSweepConfig

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    grid_kappas = _as_decimal_list(kappas)
    grid_concentrations = _as_decimal_list(concentrations)
    grid_mus = _as_decimal_list(mus)
    grid_monotonicities = _as_decimal_list(monotonicities)

    total_pairs = len(grid_kappas) * len(grid_concentrations) * len(grid_mus) * len(grid_monotonicities)
    console.print(f"[dim]Output directory: {out_dir}[/dim]")
    console.print(f"[dim]Running comparison sweep: {total_pairs} parameter combinations × 2 conditions = {total_pairs * 2} runs[/dim]")

    config = ComparisonSweepConfig(
        n_agents=n_agents,
        maturity_days=maturity_days,
        Q_total=Decimal(str(q_total)),
        kappas=grid_kappas,
        concentrations=grid_concentrations,
        mus=grid_mus,
        monotonicities=grid_monotonicities,
        base_seed=base_seed,
        default_handling=default_handling,
        dealer_ticket_size=Decimal(str(dealer_ticket_size)),
        dealer_share=Decimal(str(dealer_share)),
        vbt_share=Decimal(str(vbt_share)),
        liquidity_mode=liquidity_mode,
        liquidity_agent=liquidity_agent,
        name_prefix=name_prefix,
    )

    runner = ComparisonSweepRunner(config, out_dir)
    results = runner.run_all()

    # Summary
    completed = [r for r in results if r.delta_reduction is not None]
    if completed:
        mean_relief = sum(float(r.relief_ratio or 0) for r in completed) / len(completed)
        improved = sum(1 for r in completed if r.delta_reduction and r.delta_reduction > 0)
        console.print(f"\n[green]Comparison sweep complete.[/green]")
        console.print(f"  Pairs completed: {len(completed)}/{len(results)}")
        console.print(f"  Mean relief ratio: {mean_relief:.1%}")
        console.print(f"  Pairs with improvement: {improved}")
    else:
        console.print(f"\n[yellow]Comparison sweep complete but no pairs completed successfully.[/yellow]")

    console.print(f"\n[green]Results:[/green]")
    console.print(f"  Comparison CSV: {runner.comparison_path}")
    console.print(f"  Summary JSON: {runner.summary_path}")
    console.print(f"  Control registry: {runner.control_dir / 'registry' / 'experiments.csv'}")
    console.print(f"  Treatment registry: {runner.treatment_dir / 'registry' / 'experiments.csv'}")


@cli.command()
@click.argument('scenario_file', type=click.Path(exists=True, path_type=Path))
@click.option('--mode', type=click.Choice(['step', 'until-stable']), 
              default='until-stable', help='Simulation run mode')
@click.option('--max-days', type=int, default=90, 
              help='Maximum days to simulate')
@click.option('--quiet-days', type=int, default=2,
              help='Required quiet days for stable state')
@click.option('--show', type=click.Choice(['summary', 'detailed', 'table']),
              default='detailed', help='Event display mode')
@click.option('--agents', type=str, default=None,
              help='Comma-separated list of agent IDs to show balances for')
@click.option('--check-invariants', 
              type=click.Choice(['setup', 'daily', 'none']),
              default='setup',
              help='When to check system invariants')
@click.option('--export-balances', type=click.Path(path_type=Path),
              default=None, help='Path to export balances CSV')
@click.option('--export-events', type=click.Path(path_type=Path),
              default=None, help='Path to export events JSONL')
@click.option('--html', type=click.Path(path_type=Path),
              default=None, help='Path to export colored output as HTML')
@click.option('--t-account/--no-t-account', default=False, help='Use detailed T-account layout for balances')
@click.option('--default-handling', type=click.Choice(['fail-fast', 'expel-agent']),
              default=None, help='Default-handling mode (override scenario setting)')
def run(scenario_file: Path, 
        mode: str,
        max_days: int,
        quiet_days: int,
        show: str,
        agents: Optional[str],
        check_invariants: str,
        export_balances: Optional[Path],
        export_events: Optional[Path],
        html: Optional[Path],
        t_account: bool,
        default_handling: Optional[str]):
    """Run a Bilancio simulation scenario.
    
    Load a scenario from a YAML file and run the simulation either
    step-by-step or until a stable state is reached.
    """
    try:
        # Parse agent list if provided
        agent_ids = None
        if agents:
            agent_ids = [a.strip() for a in agents.split(',')]
        
        # Override export paths if provided via CLI
        export = {
            'balances_csv': str(export_balances) if export_balances else None,
            'events_jsonl': str(export_events) if export_events else None
        }
        
        # Run the scenario
        run_scenario(
            path=scenario_file,
            mode=mode,
            max_days=max_days,
            quiet_days=quiet_days,
            show=show,
            agent_ids=agent_ids,
            check_invariants=check_invariants,
            export=export,
            html_output=html,
            t_account=t_account,
            default_handling=default_handling
        )
        
    except FileNotFoundError as e:
        console.print(Panel(
            f"[red]File not found:[/red] {e}",
            title="Error",
            border_style="red"
        ))
        sys.exit(1)
        
    except ValueError as e:
        console.print(Panel(
            f"[red]Configuration error:[/red]\n{e}",
            title="Error",
            border_style="red"
        ))
        sys.exit(1)
        
    except Exception as e:
        console.print(Panel(
            f"[red]Unexpected error:[/red]\n{e}",
            title="Error",
            border_style="red"
        ))
        if '--debug' in sys.argv:
            raise
        sys.exit(1)


@cli.command()
@click.argument('scenario_file', type=click.Path(exists=True, path_type=Path))
def validate(scenario_file: Path):
    """Validate a Bilancio scenario configuration file.
    
    Check that a YAML configuration file is valid without running
    the simulation. Reports any errors in the configuration structure,
    agent definitions, or initial actions.
    """
    try:
        from bilancio.config import load_yaml
        from bilancio.engines.system import System
        from bilancio.config import apply_to_system
        
        # Load and parse the configuration
        console.print(f"[dim]Validating {scenario_file}...[/dim]")
        config = load_yaml(scenario_file)
        
        console.print(f"[green]✓[/green] Configuration syntax is valid")
        console.print(f"  Name: {config.name}")
        console.print(f"  Version: {config.version}")
        console.print(f"  Agents: {len(config.agents)}")
        console.print(f"  Initial actions: {len(config.initial_actions)}")
        
        # Try to apply to a test system to validate actions
        console.print("[dim]Checking if configuration can be applied...[/dim]")
        test_system = System()
        apply_to_system(config, test_system)
        
        console.print(f"[green]✓[/green] Configuration can be applied successfully")
        
        # Run invariant checks
        test_system.assert_invariants()
        console.print(f"[green]✓[/green] System invariants pass")
        
        # Summary
        console.print("\n[bold green]Configuration is valid![/bold green]")
        console.print(f"\nAgents defined:")
        for agent in config.agents:
            console.print(f"  • {agent.id} ({agent.kind}): {agent.name}")
        
        if config.run.export.balances_csv or config.run.export.events_jsonl:
            console.print(f"\nExports configured:")
            if config.run.export.balances_csv:
                console.print(f"  • Balances: {config.run.export.balances_csv}")
            if config.run.export.events_jsonl:
                console.print(f"  • Events: {config.run.export.events_jsonl}")
        
    except FileNotFoundError as e:
        console.print(Panel(
            f"[red]File not found:[/red] {e}",
            title="Error",
            border_style="red"
        ))
        sys.exit(1)
        
    except ValueError as e:
        console.print(Panel(
            f"[red]Configuration error:[/red]\n{e}",
            title="Validation Failed",
            border_style="red"
        ))
        sys.exit(1)
        
    except Exception as e:
        console.print(Panel(
            f"[red]Validation error:[/red]\n{e}",
            title="Validation Failed",
            border_style="red"
        ))
        if '--debug' in sys.argv:
            raise
        sys.exit(1)


@cli.command()
@click.option('--from', 'from_template', type=str, default=None,
              help='Base template to use')
@click.option('-o', '--output', type=click.Path(path_type=Path),
              required=True, help='Output YAML file path')
def new(from_template: Optional[str], output: Path):
    """Create a new scenario configuration.
    
    Interactive wizard to create a new Bilancio scenario
    configuration file.
    """
    try:
        create_scenario_wizard(output, from_template)
        console.print(f"[green]✓[/green] Created scenario file: {output}")
        
    except Exception as e:
        console.print(Panel(
            f"[red]Failed to create scenario:[/red]\n{e}",
            title="Error",
            border_style="red"
        ))
        sys.exit(1)


@cli.command()
@click.option('--events', 'events_path', type=click.Path(exists=True, path_type=Path), required=True,
              help='Path to events JSONL exported by a run')
@click.option('--balances', 'balances_path', type=click.Path(exists=False, path_type=Path), required=False,
              help='Path to balances CSV (optional, improves G_t/M_t)')
@click.option('--days', type=str, default=None,
              help='Days to analyze, e.g. "1,2-3". Default: infer from events')
@click.option('--out-csv', 'out_csv', type=click.Path(path_type=Path), default=None,
              help='Output CSV for day-level metrics')
@click.option('--out-json', 'out_json', type=click.Path(path_type=Path), default=None,
              help='Output JSON for day-level metrics')
@click.option('--intraday-csv', 'intraday_csv', type=click.Path(path_type=Path), default=None,
              help='Optional CSV for intraday P_prefix steps')
@click.option('--html', 'html_out', type=click.Path(path_type=Path), default=None,
              help='Optional HTML analytics report')
def analyze(
    events_path: Path,
    balances_path: Optional[Path],
    days: Optional[str],
    out_csv: Optional[Path],
    out_json: Optional[Path],
    intraday_csv: Optional[Path],
    html_out: Optional[Path],
):
    """Analyze a completed run and export Kalecki-style metrics.

    Produces a day-level metrics CSV/JSON, optional intraday CSV (diagnostic).
    """
    # Load inputs
    console.print(f"[dim]Reading events from {events_path}...[/dim]")
    events = list(read_events_jsonl(events_path))

    balances_rows = None
    if balances_path and balances_path.exists():
        console.print(f"[dim]Reading balances from {balances_path}...[/dim]")
        balances_rows = read_balances_csv(balances_path)

    day_list = parse_day_ranges(days) if days else None

    bundle = compute_day_metrics(events, balances_rows, day_list)

    if not bundle["day_metrics"]:
        console.print("[yellow]No days found to analyze.[/yellow]")
        return

    # Determine default output paths if not provided
    base = events_path.stem.replace("_events", "") or "metrics"
    out_dir = events_path.parent
    if not out_csv:
        out_csv = out_dir / f"{base}_metrics_day.csv"
    if not out_json:
        out_json = out_dir / f"{base}_metrics_day.json"
    if intraday_csv:
        intraday_csv.parent.mkdir(parents=True, exist_ok=True)

    # Write outputs
    metrics_rows = bundle["day_metrics"]
    ds_rows = bundle["debtor_shares"]
    intraday_rows = bundle["intraday"]

    write_day_metrics_csv(out_csv, metrics_rows)
    console.print(f"[green]✓[/green] Wrote day metrics CSV: {out_csv}")
    write_day_metrics_json(out_json, metrics_rows)
    console.print(f"[green]✓[/green] Wrote day metrics JSON: {out_json}")

    # Debtor shares and intraday are optional; only write if path provided
    base_name = out_csv.stem.replace("_metrics_day", "") if out_csv else "metrics"
    ds_path = out_csv.parent / f"{base_name}_ds.csv"
    write_debtor_shares_csv(ds_path, ds_rows)
    console.print(f"[green]✓[/green] Wrote debtor shares CSV: {ds_path}")

    if intraday_csv:
        write_intraday_csv(intraday_csv, intraday_rows)
        console.print(f"[green]✓[/green] Wrote intraday CSV: {intraday_csv}")

    if html_out:
        title = f"Bilancio Analytics — {events_path.stem.replace('_events','')}"
        subtitle = f"Events: {events_path.name}{' | Balances: ' + balances_path.name if balances_path else ''}"
        write_metrics_html(html_out, metrics_rows, ds_rows, intraday_rows, title=title, subtitle=subtitle)
        console.print(f"[green]✓[/green] Wrote HTML analytics: {html_out}")


def main():
    """Main entry point for the CLI."""
    cli()


if __name__ == '__main__':
    main()

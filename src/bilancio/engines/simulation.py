"""Simulation engines for financial scenario analysis."""

import random
from dataclasses import dataclass
from typing import Any, Protocol

from bilancio.engines.clearing import settle_intraday_nets
from bilancio.engines.settlement import settle_due


IMPACT_EVENTS = {
    "PayableSettled",
    "DeliveryObligationSettled",
    "InterbankCleared",
    "InterbankOvernightCreated",
}


@dataclass
class DayReport:
    day: int
    impacted: int
    notes: str = ""


def _impacted_today(system, day: int) -> int:
    return sum(1 for e in system.state.events if e.get("day") == day and e.get("kind") in IMPACT_EVENTS)


def _has_open_obligations(system) -> bool:
    for c in system.state.contracts.values():
        if c.kind in ("payable", "delivery_obligation"):
            return True
    return False


class SimulationEngine(Protocol):
    """Protocol for simulation engines that can run financial scenarios."""

    def run(self, scenario: Any) -> Any:
        """
        Run a simulation for a given scenario.
        
        Args:
            scenario: The scenario to simulate
            
        Returns:
            Simulation results
        """
        ...


class MonteCarloEngine:
    """Monte Carlo simulation engine for financial scenarios."""

    def __init__(self, num_simulations: int = 1000, n_simulations: int | None = None, random_seed: int | None = None):
        """
        Initialize the Monte Carlo engine.
        
        Args:
            num_simulations: Number of simulation runs to perform
            n_simulations: Alternative parameter name for num_simulations (for compatibility)
            random_seed: Optional seed for reproducible results
        """
        # Support both parameter names for compatibility
        if n_simulations is not None:
            self.num_simulations = n_simulations
            self.n_simulations = n_simulations
        else:
            self.num_simulations = num_simulations
            self.n_simulations = num_simulations

        if random_seed is not None:
            random.seed(random_seed)

    def run(self, scenario: Any) -> dict[str, Any]:
        """
        Run Monte Carlo simulation for a scenario.
        
        This is a placeholder implementation. A real implementation would:
        1. Extract parameters and distributions from the scenario
        2. Generate random samples according to those distributions
        3. Run the scenario multiple times with different random inputs
        4. Aggregate and return statistical results
        
        Args:
            scenario: The scenario to simulate
            
        Returns:
            Dictionary containing simulation results and statistics
        """
        # Placeholder implementation
        results = []

        for i in range(self.num_simulations):
            # In a real implementation, this would:
            # - Sample from probability distributions
            # - Apply scenario logic with sampled values
            # - Calculate outcome metrics

            # For now, just generate dummy results
            result = {
                'run_id': i,
                'outcome': random.gauss(100, 20),  # Placeholder random outcome
                'scenario': scenario
            }
            results.append(result)

        # Calculate summary statistics
        outcomes = [r['outcome'] for r in results]
        summary = {
            'num_simulations': self.num_simulations,
            'mean': sum(outcomes) / len(outcomes),
            'min': min(outcomes),
            'max': max(outcomes),
            'results': results
        }

        return summary

    def set_num_simulations(self, num_simulations: int) -> None:
        """Update the number of simulations to run."""
        self.num_simulations = num_simulations


def run_day(system):
    """
    Run a single day's simulation with three phases.
    
    Phase A: Log PhaseA event (noop for now)
    Phase B: Settle obligations due on the current day using settle_due
    Phase C: Clear intraday nets for the current day using settle_intraday_nets
    
    Finally, increment the system day counter.
    
    Args:
        system: System instance to run the day for
    """
    current_day = system.state.day

    # Phase A: Log PhaseA event (reserved)
    system.log("PhaseA")

    # Phase B: two subphases — B1 scheduled actions, B2 settlements
    system.log("PhaseB")  # Phase B bucket marker
    # B1: Execute scheduled actions for this day (if any)
    system.log("SubphaseB1")
    try:
        actions_today = system.state.scheduled_actions_by_day.get(current_day, [])
        if actions_today:
            # Lazy import to avoid heavy imports at module load
            from bilancio.config.apply import apply_action
            agents = system.state.agents
            for action_dict in actions_today:
                apply_action(system, action_dict, agents)
    except Exception:
        # Allow scheduled-action errors to bubble via apply_action's own error handling
        # but keep guard to ensure the simulation loop stability
        raise

    # B2: Automated settlements due today
    system.log("SubphaseB2")
    settle_due(system, current_day)

    # Phase C: Clear intraday nets for the current day
    system.log("PhaseC")  # optional: helps timeline
    settle_intraday_nets(system, current_day)

    # Increment system day
    system.state.day += 1


def run_until_stable(system, max_days: int = 365, quiet_days: int = 2) -> list[DayReport]:
    """
    Advance day by day until the system is stable:
    - No impactful events happen for `quiet_days` consecutive days, AND
    - No outstanding payables or delivery obligations remain.
    """
    reports = []
    consecutive_quiet = 0
    start_day = system.state.day

    for _ in range(max_days):
        day_before = system.state.day
        run_day(system)
        impacted = _impacted_today(system, day_before)
        reports.append(DayReport(day=day_before, impacted=impacted))

        if impacted == 0:
            consecutive_quiet += 1
        else:
            consecutive_quiet = 0

        if consecutive_quiet >= quiet_days and not _has_open_obligations(system):
            break

    return reports

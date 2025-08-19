from bilancio.config import load_yaml, apply_to_system
from bilancio.engines.system import System
from bilancio.engines.simulation import run_day

config = load_yaml('examples/scenarios/rich_simulation.yaml')
system = System()
apply_to_system(config, system)

# Run day 1
run_day(system)

# Show all events from day 1 phase B
day1_events = [e for e in system.state.events if e.get('day') == 1 and e.get('phase') == 'simulation']
print(f"Found {len(day1_events)} events in day 1")
for event in day1_events[:20]:
    print(f"{event.get('kind', 'Unknown')}: {event}")

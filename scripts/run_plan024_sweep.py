#!/usr/bin/env python
"""Run Plan 024 balanced sweep with 125 parameter combinations.

This script is resumable - if interrupted, just run it again and it will
pick up where it left off.

Output is quiet - only progress is shown. Full logs go to the output directory.
"""

from decimal import Decimal
from pathlib import Path
from datetime import datetime
import sys
import os
import io

# Redirect stdout to suppress verbose simulation output
# Progress will be written to stderr which the user sees
class QuietStdout:
    def __init__(self, log_file):
        self.log_file = log_file
        self.original_stdout = sys.stdout

    def write(self, text):
        # Write everything to log file
        self.log_file.write(text)
        # Only show our progress lines (they start with [ or contain specific keywords)
        if text.strip() and (
            text.strip().startswith('[') or
            text.strip().startswith('Resuming:') or
            text.strip().startswith('Completed') or
            text.strip().startswith('Output directory') or
            text.strip().startswith('Starting') or
            text.strip().startswith('Total') or
            text.strip().startswith('Sweep complete') or
            text.strip().startswith('Results at') or
            text.strip().startswith('Scenarios') or
            text.strip().startswith('SWEEP_') or
            text.strip().startswith('ERROR')
        ):
            self.original_stdout.write(text)
            self.original_stdout.flush()

    def flush(self):
        self.log_file.flush()
        self.original_stdout.flush()

# Fixed output directory for resumption (no timestamp)
out_dir = Path('out/experiments/plan024_sweep')
out_dir.mkdir(parents=True, exist_ok=True)

# Setup logging
log_path = out_dir / 'sweep.log'
log_file = open(log_path, 'a')
sys.stdout = QuietStdout(log_file)

print(f'Output directory: {out_dir}', flush=True)
print(f'Starting Plan 024 balanced sweep (resumable)...', flush=True)
print(f'Full output logged to: {log_path}', flush=True)

from bilancio.experiments.balanced_comparison import BalancedComparisonRunner, BalancedComparisonConfig

# Full sweep config matching Plan 023 but with Plan 024 improvements
config = BalancedComparisonConfig(
    # Ring parameters
    n_agents=100,  # 100 traders
    maturity_days=10,
    max_simulation_days=15,
    Q_total=Decimal('10000'),
    liquidity_mode='uniform',
    base_seed=42,
    default_handling='expel-agent',
    detailed_logging=True,  # Plan 022 detailed CSV logging

    # Grid parameters - 5x5x5 = 125 combinations
    kappas=[Decimal('0.25'), Decimal('0.5'), Decimal('1'), Decimal('2'), Decimal('4')],
    concentrations=[Decimal('0.2'), Decimal('0.5'), Decimal('1'), Decimal('2'), Decimal('5')],
    mus=[Decimal('0'), Decimal('0.25'), Decimal('0.5'), Decimal('0.75'), Decimal('1')],
    monotonicities=[Decimal('0')],
    outside_mid_ratios=[Decimal('0.75')],  # Single mid ratio for this sweep

    # Plan 024 parameters
    face_value=Decimal('20'),
    big_entity_share=Decimal('0.25'),  # DEPRECATED
    vbt_share_per_bucket=Decimal('0.25'),  # VBT holds 25% per bucket
    dealer_share_per_bucket=Decimal('0.125'),  # Dealer holds 12.5% per bucket
    rollover_enabled=True,  # Continuous rollover
    vbt_share=Decimal('0.50'),  # VBT capital share for active mode
)

# Calculate total
total_combos = (
    len(config.kappas)
    * len(config.concentrations)
    * len(config.mus)
    * len(config.monotonicities)
    * len(config.outside_mid_ratios)
)
print(f'Total parameter combinations: {total_combos}', flush=True)
print(f'Total runs (passive + active): {total_combos * 2}', flush=True)

# Run sweep
runner = BalancedComparisonRunner(config, out_dir)
print('\nStarting sweep...', flush=True)

try:
    results = runner.run_all()

    print(f'\nCompleted {len(results)} comparisons', flush=True)

    # Summary stats
    defaults_passive = sum(1 for r in results if r.delta_passive and r.delta_passive > 0)
    defaults_active = sum(1 for r in results if r.delta_active and r.delta_active > 0)
    trading_helped = sum(1 for r in results if r.trading_effect and r.trading_effect > 0)

    print(f'Scenarios with passive defaults: {defaults_passive}', flush=True)
    print(f'Scenarios with active defaults: {defaults_active}', flush=True)
    print(f'Scenarios where trading reduced defaults: {trading_helped}', flush=True)

    # Write summary
    with open(out_dir / 'aggregate' / 'sweep_summary.txt', 'w') as f:
        f.write(f'Plan 024 Balanced Sweep Results\n')
        f.write(f'================================\n')
        f.write(f'Completed at: {datetime.now().isoformat()}\n')
        f.write(f'Total comparisons: {len(results)}\n')
        f.write(f'Passive defaults: {defaults_passive}\n')
        f.write(f'Active defaults: {defaults_active}\n')
        f.write(f'Trading helped: {trading_helped}\n')

    print(f'\nResults saved to: {out_dir}', flush=True)
    print(f'SWEEP_COMPLETED_SUCCESSFULLY', flush=True)

except Exception as e:
    print(f'ERROR: {e}', flush=True)
    import traceback
    traceback.print_exc()
    sys.exit(1)
finally:
    log_file.close()

# Verification Prompt for Dealer Ring Examples

Use this prompt with an independent AI instance to verify that all examples match the PDF specification exactly.

---

## Task

You are a verification agent. Your job is to systematically check that each dealer ring example implementation matches its specification in the PDF document exactly.

**Stop immediately when you find the first mismatch and report it.**

## File Locations

- **PDF Specification**: `/Users/vladgheorghe/code/bilancio/docs/dealer_ring/dealer_examples.pdf`
- **Example Scripts**: `/Users/vladgheorghe/code/bilancio/examples/dealer_ring/example*.py`
- **HTML Reports**: `/Users/vladgheorghe/code/bilancio/examples/dealer_ring/out/example*_report.html`
- **README**: `/Users/vladgheorghe/code/bilancio/examples/dealer_ring/README.md`

## Verification Checklist

For each example (1-14), perform these checks in order:

### 1. Filename Check
Verify the filename matches the expected pattern:
- `example1_migrating_claim.py` through `example14_ticket_transfer.py`
- Each filename should include a descriptive suffix matching the PDF example title

### 2. PDF-to-Code Mapping Check
Read the PDF section and verify:
- Example N in code corresponds to PDF Section (N+1) for N=1-6
- Example 7 corresponds to PDF Section 8
- Example 8 corresponds to PDF Section 9
- ... continuing through Example 14 corresponds to PDF Section 15

### 3. Numerical Values Check
For each example, verify these numerical values match the PDF exactly:
- Initial state values (a, C, x, V, K*, X*, etc.)
- Transaction prices (bid, ask, outside quotes A, B)
- Post-transaction values
- Recovery rates (R) for settlement examples
- Ticket counts for each holder type

### 4. Execution Flow Check
Verify the sequence of operations matches the PDF:
- Trade sequence (SELL, BUY, passthrough)
- Which entity (dealer, VBT, trader) is involved at each step
- Which condition triggers each path (interior vs pinned)

### 5. Assertion Check
Verify the code includes assertions that check:
- Cash conservation (sum of cash changes = 0)
- Inventory conservation (tickets transferred, not created/destroyed except settlement)
- Feasibility pre-conditions
- Pin detection (when quotes hit outside bounds)

### 6. HTML Output Check
Run the example and verify the HTML report:
- Title matches example number and description
- All numerical values displayed match PDF specification

## Example-Specific Checks

### Examples 1-6 (PDF Sections 2-7)
These are explicitly numbered in the PDF. Verify example number matches PDF "EXAMPLE N:" header.

### Example 7 (PDF Section 8: Edge Rung Without Interior Clipping)
- Verify interior quotes strictly inside outside quotes
- Check boundary pin behavior at x=0 and x=X*

### Example 8 (PDF Section 9: Guard at Very Low M)
- M_min = 0.02 triggers Guard mode
- X* = 0 forces all trades to VBT
- Dealer (x, C) unchanged by both SELL and BUY

### Example 9 (PDF Section 10: Partial Recovery R=0.375)
- N_I(t) = 8 tickets, C_I(t) = 3, R = 3/8 = 0.375
- Holder composition: (q_D, q_V, q_K) = (3, 2, 3)
- Payouts: Dealer=1.125, VBT=0.75, Trader=1.125

### Example 10 (PDF Section 11: Trader-Held Rebucketing)
- Trader holds ticket crossing Long->Mid boundary
- Only bucket_id changes, no cash movement
- Dealer states unchanged

### Example 11 (PDF Section 12: Partial Recovery R=0.6)
- N_I(t) = 5 tickets, C_I(t) = 3, R = 3/5 = 0.6
- Holder composition: (q_D, q_VBT, q_K) = (2, 2, 1)
- Payouts: Dealer=1.2, VBT=1.2, Trader=0.6

### Example 12 (PDF Section 13: Capacity Integer Crossing)
- Case A: Up-jump K* 3->4 after interior BUY
- Case B: Down-jump K* 4->3 after interior SELL
- Verify lambda and I values change discretely

### Example 13 (PDF Section 14: Minimal Event-Loop Harness)
- Three arrivals with eligibility set discipline
- Fallback from empty SELL set to BUY set
- No-feasible retention (poor agent stays in set)

### Example 14 (PDF Section 15: Ticket-Level Transfer)
- Specific ticket IDs transferred (no generic materialization)
- Tie-breaker by lowest maturity
- Case A: dealer interior, Case B: VBT passthrough

## Output Format

For each example, report:
```
Example N: [PASS/FAIL]
- Filename: [PASS/FAIL]
- PDF Mapping: [PASS/FAIL]
- Numerical Values: [PASS/FAIL]
- Execution Flow: [PASS/FAIL]
- Assertions: [PASS/FAIL]
- HTML Output: [PASS/FAIL]
```

**If any check fails, STOP immediately and report:**
```
VERIFICATION FAILED at Example N
Issue: [Detailed description of the mismatch]
Expected (from PDF): [value/behavior]
Actual (from code): [value/behavior]
File: [path to file with issue]
Line: [line number if applicable]
```

## How to Start

1. First, read the PDF to understand the overall structure
2. For Example 1, read PDF Section 2 completely
3. Read the corresponding `example1_migrating_claim.py` file
4. Run `uv run python examples/dealer_ring/example1_migrating_claim.py`
5. Check the HTML output at `examples/dealer_ring/out/example1_report.html`
6. Document findings
7. Proceed to Example 2, or STOP if any issue found

Begin verification now.

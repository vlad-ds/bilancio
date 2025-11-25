# Verification Task: Check Example 1 HTML Report Against Specification

## Your Task

Verify that the HTML report correctly implements **Example 1** from the dealer ring specification. Read both files and check if the simulation output matches the expected values.

## Files to Read

1. **Specification**: `docs/dealer_ring/dealer_examples.pdf` - Read pages 1-3 which describe Example 1
2. **HTML Report**: `examples/dealer_ring/out/example1_report.html` - The generated report to verify

## What Example 1 Should Show

Example 1 is titled "Selling a migrating claim and dealer rebucketing". The scenario is:

### Initial Setup (Day 0)
- **Long Dealer (D_L)**:
  - Inventory a = 1 ticket
  - Cash C = 1
  - VBT anchors: M = 1.00, O = 0.30
  - Should compute: bid = 0.95, ask = 1.05

- **Mid Dealer (D_M)**:
  - Inventory a = 1 ticket
  - Cash C = 1
  - VBT anchors: M = 1.00, O = 0.20

- **Trader A1**: Has ticket T* (issued by A2) with tau = 9 (Long bucket), cash = 1.05
- **Trader A2**: Issuer of T*, cash = 10.00

### Day 1 Events
1. **Trade**: A1 sells T* to Long dealer at bid price (~0.95)
   - After trade: Long dealer has a = 2, C approximately 0.05

2. **Maturity Update**: T* tau decrements 9 -> 8, crossing from Long to Mid bucket

3. **Rebucket**: Internal dealer sale from D_L to D_M
   - **IMPORTANT**: Transfer occurs at **receiving bucket's mid anchor M** (M_Mid = 1.00)
   - NOT at old-bucket dealer's ask price
   - After rebucket: D_L has a = 1, D_M has a = 2

### Key Values to Verify (CORRECTED)

| Parameter | Day 0 (Long) | After Trade | After Rebucket |
|-----------|--------------|-------------|----------------|
| Long a | 1 | 2 | 1 |
| Long C | 1.00 | ~0.05 | **1.05** |
| Long bid | 0.95 | - | - |
| Mid a | 1 | 1 | 2 |
| Mid C | 1.00 | 1.00 | **0.00** |

### Rebucket Transfer Price

The specification states rebucketing happens at **M_receiving** (the receiving bucket's mid anchor):
- PDF spec: "internal sale at the Mid bucket mid M_M = 1"
- Transfer price should be **1.00** (M_Mid), NOT 0.975 (D_L's ask at x=2)

### Verification Checklist

Please check the HTML report for:

1. **Day 0 (Setup) Section**:
   - [ ] Long dealer shows a = 1, C = 1
   - [ ] Long dealer bid approximately 0.95
   - [ ] Mid dealer shows a = 1, C = 1
   - [ ] VBT Long shows M = 1, O = 0.30, B = 0.85, A = 1.15
   - [ ] VBT Mid shows M = 1, O = 0.20, B = 0.90, A = 1.10
   - [ ] Trader A1 shows cash = 1.05, owns T*
   - [ ] Trader A2 shows cash = 10.00

2. **Day 1 Section**:
   - [ ] Events table shows a SELL trade for T* at ~0.95
   - [ ] Events table shows a rebucket event long -> mid at price **1.00** (not 0.975)
   - [ ] Long dealer shows a = 1, C = **1.05** (not 1.025)
   - [ ] Mid dealer shows a = 2, C = **0.00** (not 0.025)
   - [ ] Quote events are logged

3. **Equity Conservation**:
   - [ ] Long E = C + M*a = 1.05 + 1*1 = 2.05 (unchanged from before rebucket)
   - [ ] Mid E = C + M*a = 0.00 + 1*2 = 2.00 (unchanged from before rebucket)

4. **General**:
   - [ ] Report has proper title and subtitle
   - [ ] Dealer cards show all kernel parameters (a, x, C, V, K*, X*, lambda, I, midline, bid, ask)
   - [ ] VBT cards show anchors (M, O, A, B)
   - [ ] Trader balance sheets show assets and liabilities

## Report Format

Provide your findings in this format:

```
## Verification Results

### Matches (checkmark)
- [List items that correctly match the specification]

### Mismatches (X)
- [List any discrepancies between the HTML and spec]

### Notes
- [Any observations or minor issues]

### Conclusion
[PASS/FAIL with brief explanation]
```

## Important Notes

- The bid price of 0.95 is computed from the L1 kernel formula when a=1, C=1, M=1, O=0.30, S=1
- Small precision differences (e.g., 0.95 vs 0.9500000) are acceptable
- The rebucket transfer price MUST be M_receiving (1.00), not ask_old (which would be ~0.975)
- After rebucketing, equity should be conserved (E = C + M*a is unchanged for both dealers)

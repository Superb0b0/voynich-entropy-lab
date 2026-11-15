# Attempt 014 — pre-execution feasibility and identifiability audit
Date: 2026-11-15. This audit does not alter PROTOCOL.md and contains no empirical result.

## Blocking issues to resolve before a run can be called protocol-compliant

1. **Computational budget is not yet demonstrated.** The frozen protocol requires 500 bootstrap replicates per direction, two-stage fitting over 7 theta and 9 phi grid values, and 200 predictive simulations per grid point. This implies up to 500 × 2 × (7+9) × 200 = 3,200,000 group-level predictive simulations, before opposite-split predictive checks. Each simulation performs paragraph-level MCMC with burn-in and thinning. No runtime benchmark has been recorded. The protocol explicitly says to stop INCOMPLETE rather than reduce the grid after seeing IT2a; therefore a small pilot must estimate runtime on a fixed subset of bootstrap indices, with no model-result inspection, before authorizing the full run.

2. **R-hat is underspecified for this algorithm.** The existing attempt-005 sampler uses a single swap-MCMC trajectory and does not return chain-level draws, acceptance counts, or multiple independent chains. Split-chain R-hat cannot be reconstructed from aggregate predictive count arrays. A compliant implementation needs multiple independently seeded chains and stored per-chain parameter/draw traces, or must declare R-hat unavailable and fail the protocol's convergence diagnostic requirement. Do not claim convergence from deterministic reproducibility.

3. **Acceptance rate is not currently measured.** Existing sample() performs Metropolis swaps but discards proposed/accepted counts. The new implementation must instrument accepted/proposed swaps and report them by chain and parameter setting.

4. **Bootstrap unit and duplicate handling.** Resampling whole paragraph groups with replacement is coherent, but duplicate sampled paragraphs must be treated as distinct bootstrap copies. The parser's split assignment is by leaf hash; the bootstrap must preserve the fixed split and sample only within it.

5. **Parameter-grid boundary interpretation.** Existing attempt-005 solve() interpolates between grid means and clamps to grid endpoints. A bootstrap boundary hit must be defined before execution as a fitted value exactly equal to the minimum or maximum of the declared grid. The protocol does not specify whether the theta grid for phi fitting is fixed to GRID_T or uses theta_nonqo. Preserve attempt-005's two-stage procedure exactly.

## Safe next step
Run a time-only benchmark using a fixed, preregistered subset of bootstrap indices and the exact 200-replicate grid procedure, suppressing all parameter/result summaries. Record elapsed time and extrapolated total runtime. If it cannot finish within the runner limit, report INCOMPLETE and do not shrink the design. Implement and test chain diagnostics before the full empirical run.

## Status
014 remains PREREGISTERED / NOT RUN. No bootstrap estimates, confidence intervals, stability verdict, or validation claim are made by this audit.

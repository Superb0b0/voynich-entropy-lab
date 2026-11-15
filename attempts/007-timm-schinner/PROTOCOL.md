# Attempt 007: Timm–Schinner, preregistered decision gate

Status: EXPLORATORY / NOT VERIFIED until independent CI reproduces the complete attempt. No holdout access. No merge.

## Calibration (completed before TS measurement)
Known theta=0.8, phi=1.2, seeds 1..5, acceptable theta 0.5..1.1 and phi 0.7..1.7, at least 4/5 PASS. Calibration-only GitHub run 43733172027: 5/5 PASS. This is not scientific validation of TS.

## Data and segmentation fixed BEFORE TS metrics
Thirty deterministic Timm–Schinner Java-generator outputs (seeds 1..30), verified against original per_seed.csv SHA256 hashes. The synthetic generator does not mark paragraphs: use **page** as the unit, using generator configuration text.lines_per_page=29, 1200 lines per output. Each output therefore has 41 complete pages and one final partial page. Preserve original line order. Ignore lines beginning '#' and blank lines; if nontext header sections exist, parse only the generated text section. First word of each nonempty line, lowercase letters only. Eight first-word prefix classes in priority order: qo,ch,sh,d,o,y,s,other. The Voynich reference uses only P rows and paragraph units as in attempt 005. Grouping is not identical between the corpora and this is a limitation.

## Null, statistics, threshold
Within each page, randomly shuffle the order of first words, preserving word multiset and page size, 1000 replicas with fixed RNG seed 20261121. For each output compute O/E ratios of (1) adjacent first words sharing any prefix class, (2) qo→qo adjacent first-word pairs, and (3) identical adjacent first words. E is the mean null count across 1000 replicas. Fail closed if E=0 for a reported ratio; report raw O and E. Aggregate all adjacent pairs across pages of a seed before computing its ratios.

Across 30 seeds, compute 5th percentile of the 30 same-class O/E values (linear interpolation) and median of the 30 qo→qo O/E values. **Reject Timm–Schinner for these particular sequential features iff both** percentile_5(same-class O/E)>0.75 **and** median(qo→qo O/E)>0.5. Otherwise NOT REJECTED. No post-hoc adjustment.

Reference values supplied in the experiment brief: Voynich train same-class O/E 0.51 and 0.59; qo→qo O/E 0.25 and 0.13 (different train directions). These are context, not recalculated in this attempt.

## Integrity
Record every input file SHA256 in manifest.json. No access to HOLDOUT.md-designated withheld text. Calibration and TS runs remain separate. Only an independently reproducible full CI run can change status from EXPLORATORY.

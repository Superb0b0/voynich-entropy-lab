# CAL-01 D05 canonical resolution evidence — for independent approval

## Scope and pinned receipts

Approved aggregator: 7e499468a6150afede51af29a554bdbdcd152f1c, SHA-256 eb69abd8b40e97a70ec854d160e837f740688067f9d71a440a82fab7d1c76ed0.
Qualification run 45834981307, artifact 15124911403, qualification JSON SHA-256 5c3a130aead4fa52cd17f0809242e39398deac91e6c899941c28722c375e71d8.
Margins run 45836019873, artifact 15125246963, margins JSON SHA-256 5e56416b32b2592cf30b24df60b49372d34c0cf71d2734fd4e20f9d7d965e500.
Dataset SHA-256 4fec2b880a886a9633395a8c99d3f60622e46ebbc3a9c2525bccd6f8ae4b0c06.
Bundle SHA-256 b2f1a6173d33d957fd8d1db862aaaef7652357149b7c1e718689d7d86506c039.
Review SHA-256 1a341945a3405cd1eb53e5b3516127c0be58f8fd6088685669e7c180f943fef7.

## Resolution of adjacent_rank only

The reported margins receipt has 40 unresolved entries, exclusively adjacent_rank. This evidence does not remove or change that check or the receipt. It proposes resolution through the existing canonical authorization gate. No classifications, frequencies or scientific verdict are inspected or computed in preparing this note.

Assume componentwise absolute perturbations of gains a_i, G0=g and L0=l bounded respectively by E_GAIN, E_G0 and E_L0, all equal to EPS = 1000 * 9.163456018285165e-12. This is the approved empirical audit allocation, NOT a proven universal bound on errors. The following argument concerns mathematical endpoint stability conditional on that assumption; it does not certify every possible hardware or floating-point implementation.

If max_i |a_i-b_i| <= E_GAIN, monotonicity of order statistics gives a_(j)-E_GAIN <= b_(j) <= a_(j)+E_GAIN for every j. Hence the linear quantile at .975 (zero-based index 974.025 for n=1000, weights .975 and .025 on indices 974 and 975) changes by at most E_GAIN in exact arithmetic. Individual ranks need not remain fixed. The mean is likewise 1-Lipschitz in the maximum norm. These bounds are mathematical bounds on the perturbed inputs, not an additional bound on rounding in evaluating the statistics.

The receipt reports strict clearance for G0_zero, L0_zero, L0_quarter_G0, row_vs_G0, P97_5_zero, rho_quarter and rho_three_quarters. Thus the sign of g, the two H1 inequalities, each comparison a_i >= g (and therefore k and p), the sign of the upper quantile and both ratio comparisons remain fixed within the approved perturbation model. For the ratio comparisons, use the sign of mean(a)-c*g together with the unchanged nonzero sign of g; the uncertainty bound is E_GAIN+c*E_G0. This covers either sign of g without assuming it positive. Therefore the frozen classify() decision is invariant in that model. Exact identity of ranks is sufficient but not necessary for this conclusion. No finite set of simultaneous +/-EPS perturbation trials is needed or claimed to prove the full componentwise box.

The narrowest reported decision margin is row_vs_G0, approximately 5.39 times its audit bound. This is not a universal safety guarantee. Canonical discrete outcomes, if separately authorized, must come from the already recomputed and qualified D05 dataset and the unchanged classifier in an admitted D05 environment, not from historical copied values.

## ZL3b_04

The successful technical qualification is evidence for admission of the fresh D05 recomputation, including the historical control checks, stream and canonical anchors. The original strict failure and prior exposure remain disclosed; the historical local reference is not reinstated. The final authorization must separately attest ZL3b_04_qualified and require the already implemented descriptive exclusion sensitivity. This note does not itself grant that approval.

## Gate status

Evidence proposed for independent review. No canonical_resolution_approved or final authorization has been issued. No changes to scientific thresholds, sources, receipts or replicas. No HOLDOUT access. Aggregation remains locked pending explicit review of this evidence and the final authorization bound to the exact receipt and evidence hashes.

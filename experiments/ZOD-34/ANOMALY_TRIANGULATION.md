# ZOD-34: source-level anomaly triangulation, 2026-11-14

STATUS: DOCUMENTARY EVIDENCE ONLY, NOT INDEPENDENT IMAGE PIXEL VERIFICATION; NOT A QUALIFYING VOYNICH EXPERIMENT.

## Sources and observations
1. Rene Zandbergen, quire 11: https://www.voynich.nu/q11/index.html
   - f72r1 Taurus dark: 15 nymphs and 15 labels.
   - f72r2 Gemini: 30 nymphs and 29 labels; one outer lower-right nymph lacks a star, one outer-left nymph lacks a label. The missing star and label are **different figures**, so do not conflate them.
   - f72r3 Cancer: 30 nymphs and 30 labels, a positive control for ordinary 1:1 counts.
2. Jorge Stolfi, f72r1: https://vib.tamagothi.de/index.php?id=f72r1&show=page
   - 6 inner plus 10 outer figures = 16. Stolfi suggests the small figure around 08:30 may explain the 15/16 count discrepancy; interpretation as a late addition is conjectural.
3. Stolfi, f72r2: https://vib.tamagothi.de/index.php?id=f72r2&show=page
   - 9 inner, 16 middle, 5 external figures = 30. This independent distribution supports the total but not independent visual validation of missing label.
4. Yale official high-resolution catalog via https://beinecke.library.yale.edu/beinecke/collections/beinecke-cipher-voynich-manuscript . Catalog image https://collections.library.yale.edu/catalog/2002046?child_oid=1006203 was blocked with HTTP 403 from current web reader. Therefore original-image pixels have **not** been independently examined in this run.

## Discriminating interpretation
The rigid universal model M0: 'every depicted nymph must have exactly one star and one adjacent label' is contradicted by documented f72r2 exceptions, conditional on catalog accuracy. A weaker model M1: '30 positions encode a calendar with occasional execution errors' remains viable. A different model M2: 'each label names a depicted person' also remains viable if one omission is accidental. M0 failure does **not** falsify the zodiac/calendar function or prove a translation.

## Next blinded inspection
On authenticated original Yale scans, two independent coders separately mark figure, star and label bounding boxes on f72r1 and f72r2, before consulting transcription. Specifically test Gemini outer-left absent label versus lower-right absent star, Taurus inner ~08:30 small figure. Add f72r3 as a positive control. Record image and crop SHA256, coder disagreements, and whether each claimed absence is real rather than faint or cropped. Then freeze numeric semantic predictions before reading token identities.

No HOLDOUT data read, no changes to RC1.4.2 CLOSED_PENDING_VALIDATION, RP-01, f085v, or ANCHOR staging. No CI claim.

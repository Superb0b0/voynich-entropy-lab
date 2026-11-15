# DECIPHER-CANDIDATE-001: Caspari–Faccini Italian shorthand key (external hypothesis)

Status: CANDIDATE_IDENTIFIED / NOT VALIDATED / NO TRANSLATION.

Source: Gino Caspari and Agnese Faccini, *A Key to the Voynich Manuscript*, https://pure.mpg.de/rest/items/item_3644902_2/component/file_3644903/content .

## Explicit claims
The authors propose an Italian vernacular shorthand cipher, a glyph-to-letter table, special ligatures and expansions, and 400+ candidate words. Their proposed initial anchors include POLAR and TOARE. These are the authors' readings, not established plaintext.

## Immediate audit issue
Their paper explicitly states that the proposed decipherment was developed from manuscript images rather than EVA transcription, and that some EVA units may split or merge glyphs incorrectly. Therefore **do not** apply the published key directly to ZL3b EVA strings without a independently audited glyph-to-EVA correspondence. This is a compatibility blocker, not a negative test result.

## Decisive validation path
1. Freeze a machine-readable key with one glyph image/shape, deterministic output, abbreviation-expansion rule and uncertainty code per entry. Separate literal mappings from contextual guesses.
2. Independently map every key glyph to the actual source manuscript image, and only then to a specified EVA or other transcription unit; log ambiguous/unsupported glyphs.
3. Fit nothing on held-out pages. Apply the frozen mapping to unseen pages, report coverage and a **complete** contiguous passage, including unreadable tokens, with no ad-hoc corrections.
4. Evaluate grammatical coherence and semantic fit blind to illustrations; compare against equally flexible rival mappings and historical Italian control texts. Require independent reproduction.
5. If any step fails, mark candidate UNVERIFIED or REJECTED; never promote a word list to a decipherment.

## Current evidence
No independent glyph alignment, locked machine-readable key, blind reading, or successful held-out translation has been produced by this project. Previous EXP-TRAIN-001/002 prefix-adjacency effects neither verify nor falsify the candidate.

Constraints: preserve protected holdout; no protected text or IDs in outputs; no changes to historical attempts, frozen public dataset or main.

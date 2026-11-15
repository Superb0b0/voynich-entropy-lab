#!/usr/bin/env python3
"""G0: aggregated candidate IVTFF counts, not an RC1.2 parser or a scientific test.

Usage (requires an independently filtered training copy):
 python g0_count_audit.py --input TRAIN_ONLY.txt --sha256 <64hex> --out g0_counts.csv

A full-source run is opt-in and is NOT an independent holdout test.
No tokens, page IDs, or protected folio labels are printed or exported.
"""
import argparse
import csv
import hashlib
import re
from pathlib import Path

LOCUS = re.compile(r'^<(?P<page>f(?:\d+[rv]\d*|Ros))\.(?P<line>\d+),(?P<locus>[^>]*)>\s*(?P<body>.*)$')
VARIANT = re.compile(r'\[([^:\]\n]+):([^\]\n]+)\]')
COMMENT = re.compile(r'<!.*?>|<[^>]*>|\{[^}]*\}')
SPLITS = {'space': re.compile(r'\s+'), 'dot_comma_space': re.compile(r'[.,\s]+')}
MARKERS = {
    'numeric_P': re.compile(r'^[*@+=]P[0-9]+$'),
    'anchor_P': re.compile(r'^[@*]P[0-9]*$'),
    'family_P': re.compile(r'^[*@+=]P'),
    'contains_P': re.compile(r'P'),
}
FIELDS = ('source_sha256', 'scope', 'locus_rule', 'variant_rule', 'token_rule',
          'loci', 'tokens', 'pages', 'folios', 'paragraph_starts', 'candidate_only')


def sanitize(s, variant_rule):
    if variant_rule == 'first':
        s = VARIANT.sub(lambda m: m.group(1), s)
    elif variant_rule == 'second':
        s = VARIANT.sub(lambda m: m.group(2), s)
    elif variant_rule == 'remove':
        s = VARIANT.sub('', s)
    else:
        raise ValueError(variant_rule)
    s = COMMENT.sub(' ', s)
    s = re.sub(r'\[[^\]\n]*\]', ' ', s)
    return s


def analyze(raw, scope, source_sha):
    # Only aggregate counters and opaque page names exist in memory during execution.
    entries = []
    malformed_loci = 0
    for line in raw.decode('utf-8').splitlines():
        m = LOCUS.match(line)
        if m:
            entries.append((m['page'], m['locus'], m['body']))
        elif re.match(r'^<f\d+[rv]\d*\.', line):
            malformed_loci += 1
    rows = []
    for marker_name, matcher in MARKERS.items():
        chosen = [(p, locus, body) for p, locus, body in entries
                  if (matcher.search(locus) if marker_name == 'contains_P'
                      else matcher.match(locus))]
        pages = {p for p, _, _ in chosen}
        folios = {(re.match(r'f\d+', p).group() if re.match(r'f\d+', p) else p) for p in pages}
        starts = sum(l.startswith(('@P', '*P')) for _, l, _ in chosen)
        for variant_rule in ('first', 'second', 'remove'):
            clean = [sanitize(body, variant_rule) for _, _, body in chosen]
            for split_name, splitter in SPLITS.items():
                tokens = sum(sum(bool(tok) for tok in splitter.split(s.strip()))
                             for s in clean)
                rows.append(dict(source_sha256=source_sha, scope=scope,
                                 locus_rule=marker_name, variant_rule=variant_rule,
                                 token_rule=split_name, loci=len(chosen),
                                 tokens=tokens, pages=len(pages), folios=len(folios),
                                 paragraph_starts=starts, candidate_only=True))
    return rows, malformed_loci


def self_test():
    fake = ('<f1r> <! page\n'
            '<f1r.1,@P0> qo.kedy [daiin:chol],ol <%> otedy\n'
            '<f1r.2,+P0> qokedy other\n'
            '<f1r.3,@Q0> unknown.thing\n'
            '<f2v> <! page\n'
            '<f2v.1,*P0> daiin.chedy\n').encode()
    rows, malformed = analyze(fake, 'SYNTHETIC', hashlib.sha256(fake).hexdigest())
    assert malformed == 0
    a = next(x for x in rows if x['locus_rule'] == 'family_P'
             and x['variant_rule'] == 'first'
             and x['token_rule'] == 'dot_comma_space')
    assert (a['loci'], a['pages'], a['folios'], a['tokens']) == (3, 2, 2, 9), a
    b = next(x for x in rows if x['locus_rule'] == 'anchor_P'
             and x['variant_rule'] == 'first'
             and x['token_rule'] == 'dot_comma_space')
    assert (b['loci'], b['tokens']) == (2, 7), b
    print('SELF-TEST PASS (synthetic data only; no Voynich text opened)')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input', type=Path)
    p.add_argument('--sha256', help='Expected complete SHA-256 of input bytes')
    p.add_argument('--scope', choices=('TRAIN_FILTERED', 'FULL'), default='TRAIN_FILTERED')
    p.add_argument('--ack-full-corpus', action='store_true',
                   help='Explicitly acknowledge FULL is not an independent holdout test')
    p.add_argument('--out', type=Path, default=Path('g0_counts.csv'))
    p.add_argument('--self-test', action='store_true')
    a = p.parse_args()
    if a.self_test:
        self_test(); return
    if not a.input or not a.sha256 or not re.fullmatch(r'[a-fA-F0-9]{64}', a.sha256):
        p.error('--input and complete --sha256 are mandatory')
    if a.scope == 'FULL' and not a.ack_full_corpus:
        p.error('FULL scope requires explicit --ack-full-corpus')
    raw = a.input.read_bytes()
    actual = hashlib.sha256(raw).hexdigest()
    if actual.lower() != a.sha256.lower():
        raise SystemExit('FAIL CLOSED: SHA-256 mismatch')
    rows, malformed = analyze(raw, a.scope, actual)
    if malformed:
        raise SystemExit(f'FAIL CLOSED: {malformed} IVTFF locus headers unparsed')
    if not any(r['loci'] for r in rows):
        raise SystemExit('FAIL CLOSED: no P loci recognized')
    with a.out.open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader(); w.writerows(rows)
    print(f'G0 CANDIDATE COUNTS WRITTEN: {a.out} ({len(rows)} specs, no corpus text output)')
    print('STATUS: NON VERIFICABILE against historical counts until canonical parser specs and source population are supplied')


if __name__ == '__main__':
    main()

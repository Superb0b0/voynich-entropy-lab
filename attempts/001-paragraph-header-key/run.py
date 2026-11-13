#!/usr/bin/env python3
"""001: Prespecified first-line lexical-key experiment. Stdlib + numpy only."""
import argparse
import hashlib
import importlib.util
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

SEED_PERM = 20261113
SEED_BOOT = 20261114
SEED_RIVAL = 20261115
PERMUTATIONS = 1999
BOOTSTRAPS = 1999
RIVAL_RUNS = 199
SHA_CORPUS = 'bf5b6d4ac1e3a51b1847a9c388318d609020441ccd56984c901c32b09beccafc'
SHA_PARSER = '8a614436a2d5dc3cb30c282743929aaa21a379d9da7e691b4277c670ce2a91c5'


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(corpus, parserpath):
    assert sha256(corpus) == SHA_CORPUS, 'CORPUS SHA256 MISMATCH'
    assert sha256(parserpath) == SHA_PARSER, 'PARSER SHA256 MISMATCH'
    spec = importlib.util.spec_from_file_location('locked_parser', str(parserpath))
    parser = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(parser)
    records = parser.parse_corpus(corpus, verify_source=True)['records']
    assert len(records) == 4130
    lines = corpus.read_text(encoding='utf-8').splitlines()
    by_folio = defaultdict(list)
    for rec in records:
        by_folio[rec['folio']].append(rec)
    folios = {}
    all_folio_count = 0
    all_para_count = 0
    for f, rows in by_folio.items():
        all_folio_count += 1
        paras = []
        for idx, row in enumerate(rows):
            if idx == 0 or '<%>' in lines[row['physical_line'] - 1]:
                paras.append([])
            paras[-1].append(idx)
        all_para_count += len(paras)
        eligible = []
        for para in paras:
            if len(para) < 3:
                continue
            head = [w for w in rows[para[0]]['tokens'] if len(w) >= 3]
            body = [w for i in para[2:] for w in rows[i]['tokens'] if len(w) >= 3]
            if len(head) >= 2 and len(body) >= 1:
                eligible.append(para)
        if len(eligible) >= 2:
            folios[f] = {'rows': rows, 'pars': eligible,
                          'split': hashlib.sha256(f.encode('ascii')).digest()[0] % 2}
    return folios, {'all_folios': all_folio_count, 'all_paragraphs': all_para_count,
                    'P_rows': len(records)}


def matrices(data, override_rows=None):
    rows = override_rows if override_rows is not None else [r['tokens'] for r in data['rows']]
    pars = data['pars']
    heads = [set(w[:3] for w in rows[p[0]] if len(w) >= 3) for p in pars]
    wholes = [set(w for w in rows[p[0]] if len(w) >= 3) for p in pars]
    bodies = [[w for z in p[2:] for w in rows[z] if len(w) >= 3] for p in pars]
    n = len(pars)
    m3 = np.zeros((n, n), dtype=np.int32)
    mw = np.zeros((n, n), dtype=np.int32)
    for j, body in enumerate(bodies):
        for i in range(n):
            h3, hw = heads[i], wholes[i]
            m3[j, i] = sum(w[:3] in h3 for w in body)
            mw[j, i] = sum(w in hw for w in body)
    return m3, mw, sum(len(b) for b in bodies)


def quantiles(values):
    return [float(np.quantile(values, .025)), float(np.quantile(values, .975))]


def compare(folios):
    blocks = []
    for f, data in sorted(folios.items()):
        m3, mw, denom = matrices(data)
        blocks.append((f, data['split'], m3, mw, denom))
    out = {'inputs': {'ZL3b-n.txt': SHA_CORPUS, 'ivtff_parser_rc1_2.py': SHA_PARSER},
           'config': {'permutations': PERMUTATIONS, 'bootstrap_folios': BOOTSTRAPS,
                      'rival_runs': RIVAL_RUNS, 'seeds': [SEED_PERM, SEED_BOOT, SEED_RIVAL]},
           'splits': {}, 'secondary': {}, 'rival': {}}
    rng = np.random.default_rng(SEED_PERM)
    sums = np.zeros((PERMUTATIONS, 2, 2), np.float64)
    for k in range(PERMUTATIONS):
        for f, split, m3, mw, denom in blocks:
            q = rng.permutation(len(m3))
            ii = np.arange(len(m3))
            sums[k, split, 0] += m3[ii, q].sum()
            sums[k, split, 1] += mw[ii, q].sum()
    bs_rng = np.random.default_rng(SEED_BOOT)
    for split in [0, 1]:
        b = [x for x in blocks if x[1] == split]
        n_folios = len(b)
        n_paras = sum(len(x[2]) for x in b)
        token_denom = sum(x[4] for x in b)
        assert token_denom > 0
        for j, label in enumerate(['primary_prefix3', 'secondary_exact_word']):
            observed_total = sum(int(np.trace(x[2 + j])) for x in b)
            observed = observed_total / token_denom
            sim = sums[:, split, j] / token_denom
            nullmean = float(sim.mean())
            deltas = np.array([float(np.trace(x[2 + j]) - x[2 + j].sum() / len(x[2+j]))
                               for x in b])
            weights = np.array([x[4] for x in b], dtype=float)
            boot = np.empty(BOOTSTRAPS)
            for k in range(BOOTSTRAPS):
                q = bs_rng.integers(0, n_folios, n_folios)
                boot[k] = deltas[q].sum() / weights[q].sum()
            result = {'folio_count': n_folios, 'paragraph_count': n_paras,
                      'body_tokens_len_ge_3': token_denom, 'observed': observed,
                      'null_mean': nullmean, 'null_q025_q975': quantiles(sim),
                      'obs_over_exp': observed / nullmean if nullmean else None,
                      'obs_minus_null': observed - nullmean,
                      'one_sided_p': float((1 + np.count_nonzero(sim >= observed)) / (PERMUTATIONS + 1)),
                      'folio_bootstrap_diff_ci95': quantiles(boot)}
            if j == 0:
                out['splits'][str(split)] = result
            else:
                out['secondary'][str(split)] = result
    out['summary'] = {'eligible_folios': len(blocks), 'eligible_paragraphs': sum(len(x[2]) for x in blocks),
                      'body_tokens_len_ge_3': sum(x[4] for x in blocks)}
    rng_rival = np.random.default_rng(SEED_RIVAL)
    rival = np.zeros((RIVAL_RUNS, 2))
    rival_den = np.zeros((RIVAL_RUNS, 2))
    for k in range(RIVAL_RUNS):
        for f, data in folios.items():
            rows = data['rows']
            all_tokens = np.array([w for row in rows for w in row['tokens']], dtype=object)
            shuffled = rng_rival.permutation(all_tokens)
            at, fake = 0, []
            for row in rows:
                width = len(row['tokens'])
                fake.append(shuffled[at:at + width])
                at += width
            m3, _, denom = matrices(data, fake)
            rival[k, data['split']] += int(np.trace(m3))
            rival_den[k, data['split']] += denom
    for split in [0, 1]:
        rv = rival[:, split] / rival_den[:, split]
        out['rival'][str(split)] = {'token_within_folio_shuffle_mean': float(rv.mean()),
                                    'q025_q975': quantiles(rv)}
    if min(out['splits'][str(s)]['folio_count'] for s in [0, 1]) < 20:
        verdict = 'INCONCLUDENTE (meno di 20 folii in uno split)'
    elif all(out['splits'][str(s)]['one_sided_p'] <= .01 and
             out['splits'][str(s)]['obs_minus_null'] > 0 for s in [0, 1]):
        verdict = 'H1 SOSTENUTA SOLO ESPLORATIVAMENTE'
    else:
        verdict = 'H1 NON SOSTENUTA / SMENTITA DAL TEST PRIMARIO'
    out['status'] = 'ESPLORATIVO'
    out['verdict'] = verdict
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--corpus', type=Path, required=True)
    ap.add_argument('--parser', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()
    folios, audit = load(a.corpus, a.parser)
    r = compare(folios)
    r['source_audit'] = audit
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(r, ensure_ascii=False, sort_keys=True, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(r, ensure_ascii=False, sort_keys=True, indent=2))

if __name__ == '__main__':
    main()

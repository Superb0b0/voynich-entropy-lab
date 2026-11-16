#!/usr/bin/env python3
"""Fail-closed, read-only preflight for W47 exact-firstword exploratory workflow.

Provenance checks do NOT substitute for independent validation of scientific
claims inside an attestation. No access to corpus or HOLDOUT; only Git objects.
"""
import argparse
import datetime as dt
import hashlib
import json
import os
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
CUTOFF = dt.datetime.fromisoformat('2026-11-20T17:00:00+00:00')
ZL3B = 'bf5b6d4ac1e3a51b1847a9c388318d609020441ccd56984c901c32b09beccafc'
RC12 = '8a614436a2d5dc3cb30c282743929aaa21a379d9da7e691b4277c670ce2a91c5'
PROTOCOL_PATH = 'research/week47-qo-decision/PROTOCOL.json'
RUNNER_PATH = 'research/week47-qo-decision/run_locked.py'
GATE_PATH = 'research/week47-qo-decision/gate.json'
HEX40 = re.compile(r'^[a-f0-9]{40}$')
HEX64 = re.compile(r'^[a-f0-9]{64}$')

class GateError(RuntimeError):
    pass

def require(ok, message):
    if not ok:
        raise GateError(message)

def git(*args):
    p = subprocess.run(['git', '-C', str(ROOT), *args], capture_output=True)
    if p.returncode:
        raise GateError('Git provenance check failed (missing or non-ancestor object)')
    return p.stdout

def sha(b):
    return hashlib.sha256(b).hexdigest()

def clean_path(path):
    require(isinstance(path, str) and path and not path.startswith('/'), 'Invalid relative evidence path')
    parts = pathlib.PurePosixPath(path).parts
    require('..' not in parts and parts[0] == 'research' and len(parts) >= 3, 'Unsafe evidence path')
    require('\\' not in path and not path.endswith('/'), 'Malformed evidence path')
    return path

def immutable_bytes(item, label, *, expected_path=None):
    require(isinstance(item, dict), f'{label}: missing evidence item')
    commit, path, digest = item.get('commit'), item.get('path'), item.get('sha256')
    require(isinstance(commit, str) and HEX40.fullmatch(commit), f'{label}: full frozen commit required')
    require(isinstance(digest, str) and HEX64.fullmatch(digest), f'{label}: full SHA-256 required')
    # The legacy policy source is the single specifically whitelisted tools/ path;
    # all other immutable evidence stays below research/.
    if expected_path == 'tools/qo_rival_calibration.py':
        require(path == expected_path, f'{label}: wrong protected policy path')
    else:
        path = clean_path(path)
        if expected_path:
            require(path == expected_path, f'{label}: wrong evidence path')
    head = git('rev-parse', 'HEAD').decode().strip()
    require(head != commit, f'{label}: source commit must precede execution checkout')
    git('merge-base', '--is-ancestor', commit, head)
    # Git commit timestamp is a limited timestamp, not an external certification.
    timestamp = git('show', '-s', '--format=%cI', commit).decode().strip()
    committed = dt.datetime.fromisoformat(timestamp)
    require(committed <= CUTOFF, f'{label}: evidence committed after frozen cutoff')
    data = git('show', f'{commit}:{path}')
    require(sha(data) == digest, f'{label}: committed file hash mismatch')
    current = ROOT / path
    require(current.is_file() and sha(current.read_bytes()) == digest,
            f'{label}: working checkout differs from frozen source')
    return data

def check_protocol(data):
    try:
        p = json.loads(data)
    except (json.JSONDecodeError, UnicodeDecodeError):
        raise GateError('Frozen protocol is not valid JSON')
    require(p.get('status') == 'FROZEN_EXPLORATORY' and p.get('question_type') == 'NULL_ONLY',
            'No frozen NULL_ONLY exploratory protocol')
    require(p.get('source_corpora', {}).get('ZL3b') == ZL3B,
            'Frozen protocol has wrong ZL3b hash')
    require(p.get('parser', {}).get('name') == 'RC1.2' and
            p['parser'].get('source_sha256') == RC12,
            'Frozen protocol has wrong parser')
    parser = p['parser']
    for key, n in [('full_corpus_structural_blocks', 740), ('full_corpus_P_loci', 4130),
                   ('full_corpus_tokens', 35492), ('full_corpus_types', 6980)]:
        require(parser.get(key) == n, f'Frozen protocol: missing canonical {key}')
    require(p.get('scope', {}).get('population') == 'AUTHORIZED_TRAINING_ONLY',
            'Experiment would use unapproved input population')
    require(p.get('scope', {}).get('endpoint') == 'EXACT_FIRST_WORD_REPETITION',
            'Wrong endpoint: positional qo and qo-to-qo are distinct')
    require(p.get('null_model', {}).get('kind') == 'WITHIN_IVTFF_BLOCK_PERMUTE_FIRST_WORDS',
            'Null model not frozen')
    require(p.get('uncertainty', {}).get('cluster_unit'), 'Folio cluster unit missing')
    require(p.get('cross_transcription_rule'), 'IT2a discordance rule missing')
    require(p.get('decision_thresholds') and all(k in p['decision_thresholds']
            for k in ('SUPPORTED', 'FALSIFIED', 'INCONCLUSIVE', 'NOT VERIFIABLE')),
            'Four outcome thresholds not frozen')
    require(p.get('deadline_utc') == '2026-11-20T17:00:00Z',
            'Protocol deadline differs from irreversible W47 cutoff')
    require(p.get('null_model', {}).get('replicates') == 10000,
            'Null permutations not frozen')
    return p

def check_parser_report(data):
    try:
        p = json.loads(data)
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise GateError('Parser parity report is not JSON')
    require(p.get('status') == 'VERIFIED', 'Parser parity is not verified')
    require(p.get('canonical_source_sha256') == ZL3B and
            p.get('canonical_parser_sha256') == RC12,
            'Parser parity: wrong canonical input or parser')
    required_counts = {'blocks': 740, 'P_loci': 4130, 'tokens': 35492, 'types': 6980,
                       'matched_blocks': 740, 'matched_loci': 4130,
                       'block_boundary_mismatches': 0, 'token_mismatches': 0,
                       'adjacency_mismatches': 0, 'unexplained_differences': 0}
    for key, expected in required_counts.items():
        require(type(p.get(key)) is int and p[key] == expected,
                f'Parser parity: {key} differs from canonical reference')
    require(p.get('matched_token_stream') is True, 'Parser parity: token stream unverified')
    require(p.get('matched_pair_eligibility') is True, 'Parser parity: adjacency unverified')
    require(p.get('it2a_pair_mapping_checked') is True, 'IT2a correspondence not verified')
    for name in ('block_manifest', 'locus_manifest', 'difference_register'):
        evidence = p.get(name)
        require(isinstance(evidence, dict), f'Parser parity: {name} missing')
        immutable_bytes(evidence, f'parser:{name}')
    # Attestation checks alone do not prove independent parser equivalence.
    return p

def check_gate_manifest_frozen_before_cutoff(manifest):
    """Verify the WHOLE approval manifest was committed by the W47 deadline.

    This is a provenance/sequence check, not proof of independent scientific
    review or a trusted external timestamp. It prevents late approval using
    otherwise old evidence refs.
    """
    actual = (ROOT / GATE_PATH).read_bytes()
    try:
        checked = json.loads(actual)
    except (json.JSONDecodeError, UnicodeDecodeError):
        raise GateError('Approval gate manifest is not valid JSON')
    require(checked == manifest, 'Approved evidence must match canonical gate.json')
    commit = git('log', '-1', '--format=%H', '--', GATE_PATH).decode().strip()
    require(bool(HEX40.fullmatch(commit)), 'Approval manifest lacks a full Git commit')
    head = git('rev-parse', 'HEAD').decode().strip()
    git('merge-base', '--is-ancestor', commit, head)
    try:
        when = dt.datetime.fromisoformat(
            git('show', '-s', '--format=%cI', commit).decode().strip()
        )
    except ValueError as exc:
        raise GateError('Approval commit timestamp invalid') from exc
    require(when.tzinfo is not None and when <= CUTOFF,
            'Approval manifest was not frozen by 20 Nov 2026 18:00 Europe/Rome')
    require(git('show', f'{commit}:{GATE_PATH}') == actual,
            'Approval manifest differs from the last committed approval')
    return commit

def verify(manifest, now=None):
    now = now or dt.datetime.now(dt.timezone.utc)
    require(isinstance(manifest, dict) and manifest.get('schema_version') == 1,
            'Preflight manifest missing or wrong version')
    require(manifest.get('question_type') == 'NULL_ONLY',
            'Generator comparison requires a DIFFERENT frozen protocol; never auto-fallback')
    require(manifest.get('rivals', {}).get('status') == 'NOT_APPLICABLE_NULL_ONLY',
            'Timm-Schinner is not an attested rival under this NULL_ONLY question')
    protocol_bytes = immutable_bytes(manifest.get('protocol'), 'protocol', expected_path=PROTOCOL_PATH)
    check_protocol(protocol_bytes)
    evidence = manifest.get('parser_evidence', {})
    require(evidence.get('status') == 'VERIFIED', 'Parser parity evidence PENDING')
    check_parser_report(immutable_bytes(evidence, 'parser_evidence'))
    preparer = manifest.get('preparer', {})
    require(preparer.get('status') == 'APPROVED_TRAINING_ONLY',
            'Training input preparer not independently approved')
    immutable_bytes(preparer, 'preparer',
                    expected_path='research/week47-qo-decision/training_preflight.py')
    partition_policy = manifest.get('partition_policy', {})
    require(partition_policy.get('status') == 'AUDITED_PARTITION_POLICY',
            'Protected-folio exclusion policy not independently audited')
    immutable_bytes(partition_policy, 'partition_policy',
                    expected_path='tools/qo_rival_calibration.py')
    runner = manifest.get('runner', {})
    require(runner.get('status') == 'APPROVED_ISOLATED', 'Isolated runner NOT APPROVED')
    immutable_bytes(runner, 'runner', expected_path=RUNNER_PATH)
    require(manifest.get('input_isolation') == 'VERIFIED_TRAINING_ONLY',
            'No proof of isolated training-only input')
    # Gate APPROVAL itself must be committed by cutoff, not only its sources.
    check_gate_manifest_frozen_before_cutoff(manifest)
    # Pre-cutoff frozen approvals can support a controlled 21–22 Nov run.
    return 'READY_TO_RUN_EXPLORATORY_NULL_ONLY'

def main():
    a = argparse.ArgumentParser(description=__doc__)
    a.add_argument('--manifest', default='research/week47-qo-decision/gate.json')
    args = a.parse_args()
    mpath = ROOT / clean_path(args.manifest)
    try:
        require(mpath.is_file(), 'Gate manifest missing')
        manifest = json.loads(mpath.read_text())
        verdict = verify(manifest)
    except (GateError, json.JSONDecodeError, OSError) as e:
        verdict = ('NOT VERIFIABLE' if dt.datetime.now(dt.timezone.utc) >= CUTOFF
                   else 'BLOCKED_PENDING_EVIDENCE')
        print(f'W47 PREFLIGHT: {verdict} | {e}', file=sys.stderr)
        return 1
    print(f'W47 PREFLIGHT: {verdict} | all commit/hash/provenance gates passed')
    return 0

if __name__ == '__main__':
    sys.exit(main())

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
import urllib.error
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[2]
CUTOFF = dt.datetime.fromisoformat('2026-11-20T17:00:00+00:00')
REPOSITORY = 'Superb0b0/voynich-entropy-lab'
PR_NUMBER = 26
PR_AUTHOR = 'Superb0b0'
APPROVED_BRANCH = 'research/week47-qo-rivals-plan-20261116'
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
    # Explicitly allow only the two non-research evidence files used by W47.
    if expected_path in ('tools/qo_rival_calibration.py',
                         '.github/workflows/week47-qo-gated.yml'):
        require(path == expected_path, f'{label}: wrong evidence path')
    else:
        path = clean_path(path)
        if expected_path:
            require(path == expected_path, f'{label}: wrong evidence path')
    head = git('rev-parse', 'HEAD').decode().strip()
    require(head != commit, f'{label}: source commit must precede execution checkout')
    git('merge-base', '--is-ancestor', commit, head)
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

def check_gate_manifest_at_head(manifest):
    """Bind gate bytes to HEAD; timing comes from GitHub's review timestamp."""
    actual = (ROOT / GATE_PATH).read_bytes()
    try:
        checked = json.loads(actual)
    except (json.JSONDecodeError, UnicodeDecodeError):
        raise GateError('Approval gate manifest is not valid JSON')
    require(checked == manifest, 'Approved evidence must match canonical gate.json')
    head = git('rev-parse', 'HEAD').decode().strip()
    require(bool(HEX40.fullmatch(head)), 'Current HEAD is not a full commit')
    require(git('show', f'{head}:{GATE_PATH}') == actual,
            'Gate manifest differs from reviewed HEAD')
    return head

def validate_review_approval(approval, head_sha, now=None):
    """Require a GitHub-submitted approval for this exact PR head by cutoff."""
    require(isinstance(approval, dict), 'GitHub PR review approval unavailable')
    require(approval.get('repository') == REPOSITORY and
            approval.get('pr_number') == PR_NUMBER and
            approval.get('pr_author') == PR_AUTHOR,
            'Approval is for the wrong repository, PR, or author')
    require(approval.get('pr_state') == 'open' and
            approval.get('head_branch') == APPROVED_BRANCH and
            approval.get('head_sha') == head_sha,
            'PR head differs from the reviewed W47 commit')
    review = approval.get('review')
    require(isinstance(review, dict) and review.get('state') == 'APPROVED',
            'A formal GitHub APPROVED review is required')
    require(review.get('commit_id') == head_sha,
            'Approval does not cover the exact reviewed head commit')
    reviewer = review.get('reviewer')
    require(isinstance(reviewer, str) and reviewer and
            reviewer.casefold() != PR_AUTHOR.casefold(),
            'Approval must come from someone other than the PR author')
    try:
        submitted = dt.datetime.fromisoformat(review['submitted_at'].replace('Z', '+00:00'))
    except (KeyError, TypeError, ValueError) as exc:
        raise GateError('GitHub review timestamp is missing or invalid') from exc
    require(submitted.tzinfo is not None and submitted <= CUTOFF,
            'GitHub review was not submitted by the 20 Nov 2026 18:00 Rome cutoff')
    return {'reviewer': reviewer, 'submitted_at': submitted.isoformat(),
            'commit_id': head_sha, 'pr_number': PR_NUMBER}

def github_json(url):
    token = os.environ.get('GITHUB_TOKEN')
    require(bool(token), 'GitHub token unavailable for server-side approval check')
    request = urllib.request.Request(url, headers={
        'Accept': 'application/vnd.github+json',
        'Authorization': f'Bearer {token}',
        'X-GitHub-Api-Version': '2022-11-28',
    })
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return json.loads(response.read())
    except (urllib.error.URLError, json.JSONDecodeError, OSError) as exc:
        raise GateError('Unable to verify approval using GitHub API') from exc

def github_review_approval():
    """Fetch authoritative PR/review timestamps from GitHub, never Git dates."""
    require(os.environ.get('GITHUB_REPOSITORY') == REPOSITORY,
            'Preflight must run in the canonical GitHub repository')
    require(os.environ.get('GITHUB_EVENT_NAME') == 'workflow_dispatch',
            'Approval preflight must be a manual W47 dispatch')
    require(os.environ.get('GITHUB_REF_NAME') == APPROVED_BRANCH,
            'Dispatch must target the reviewed W47 branch')
    head = git('rev-parse', 'HEAD').decode().strip()
    base = f'https://api.github.com/repos/{REPOSITORY}'
    pr = github_json(f'{base}/pulls/{PR_NUMBER}')
    require(pr.get('state') == 'open' and
            pr.get('user', {}).get('login') == PR_AUTHOR and
            pr.get('head', {}).get('ref') == APPROVED_BRANCH and
            pr.get('head', {}).get('sha') == head,
            'Open PR #26 must point at the exact dispatched W47 HEAD')
    page = 1
    reviews = []
    while page <= 10:
        batch = github_json(f'{base}/pulls/{PR_NUMBER}/reviews?per_page=100&page={page}')
        require(isinstance(batch, list), 'GitHub review list has invalid format')
        reviews.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    latest = {}
    for review in reviews:
        user = review.get('user') or {}
        login = user.get('login')
        submitted_at = review.get('submitted_at')
        if not login or not submitted_at:
            continue
        try:
            stamp = dt.datetime.fromisoformat(submitted_at.replace('Z', '+00:00'))
        except (TypeError, ValueError):
            continue
        if login.casefold() == PR_AUTHOR.casefold() or review.get('commit_id') != head:
            continue
        old = latest.get(login.casefold())
        if old is None or stamp > old[0]:
            latest[login.casefold()] = (stamp, review)
    eligible = [(stamp, review) for stamp, review in latest.values()
                if review.get('state') == 'APPROVED' and stamp <= CUTOFF]
    require(bool(eligible),
            'No non-author GitHub approval for this exact HEAD was submitted by cutoff')
    stamp, review = max(eligible, key=lambda item: item[0])
    return {'repository': REPOSITORY, 'pr_number': PR_NUMBER,
            'pr_author': PR_AUTHOR, 'pr_state': pr['state'],
            'head_branch': pr['head']['ref'], 'head_sha': head,
            'review': {'state': review['state'], 'commit_id': review['commit_id'],
                       'reviewer': review['user']['login'],
                       'submitted_at': stamp.isoformat()}}

def verify(manifest, now=None, approval=None, require_approval=True):
    require(isinstance(manifest, dict) and manifest.get('schema_version') == 1,
            'Preflight manifest missing or wrong version')
    require(manifest.get('question_type') == 'NULL_ONLY',
            'Generator comparison requires a DIFFERENT frozen protocol; never auto-fallback')
    require(manifest.get('rivals', {}).get('status') == 'NOT_APPLICABLE_NULL_ONLY',
            'Timm-Schinner is not an attested rival under this NULL_ONLY question')
    protocol_bytes = immutable_bytes(manifest.get('protocol'), 'protocol', expected_path=PROTOCOL_PATH)
    check_protocol(protocol_bytes)
    evidence = manifest.get('parser_evidence', {})
    check_parser_report(immutable_bytes(evidence, 'parser_evidence'))
    preparer = manifest.get('preparer', {})
    immutable_bytes(preparer, 'preparer',
                    expected_path='research/week47-qo-decision/training_preflight.py')
    partition_policy = manifest.get('partition_policy', {})
    immutable_bytes(partition_policy, 'partition_policy',
                    expected_path='tools/qo_rival_calibration.py')
    runner = manifest.get('runner', {})
    immutable_bytes(runner, 'runner', expected_path=RUNNER_PATH)
    isolation = manifest.get('input_isolation', {})
    immutable_bytes(isolation, 'input_isolation',
                    expected_path='.github/workflows/week47-qo-gated.yml')
    head = check_gate_manifest_at_head(manifest)
    if require_approval:
        validate_review_approval(approval if approval is not None else github_review_approval(),
                                head, now=now)
    return 'READY_TO_RUN_EXPLORATORY_NULL_ONLY'

def main():
    a = argparse.ArgumentParser(description=__doc__)
    a.add_argument('--manifest', default='research/week47-qo-decision/gate.json')
    a.add_argument('--receipt', type=pathlib.Path)
    args = a.parse_args()
    mpath = ROOT / clean_path(args.manifest)
    try:
        require(mpath.is_file(), 'Gate manifest missing')
        manifest = json.loads(mpath.read_text())
        # Check frozen evidence first so a synthetic negative fixture proves
        # its intended fail-closed condition without needing a live PR review.
        verdict = verify(manifest, require_approval=False)
        approval = github_review_approval()
        head = git('rev-parse', 'HEAD').decode().strip()
        validate_review_approval(approval, head)
        if args.receipt:
            head = git('rev-parse', 'HEAD').decode().strip()
            receipt = {'schema_version': 1, 'decision': verdict,
                       'repository': REPOSITORY, 'pr_number': approval['pr_number'],
                       'reviewer': approval['review']['reviewer'],
                       'review_submitted_at': approval['review']['submitted_at'],
                       'review_commit': approval['review']['commit_id'],
                       'head_sha': head, 'gate_sha256': sha((ROOT / GATE_PATH).read_bytes()),
                       'runner_sha256': manifest['runner']['sha256'],
                       'preparer_sha256': manifest['preparer']['sha256'],
                       'protocol_sha256': manifest['protocol']['sha256'],
                       'parser_sha256': RC12,
                       'workflow_path': '.github/workflows/week47-qo-gated.yml',
                       'run_id': os.environ.get('GITHUB_RUN_ID', '')}
            args.receipt.parent.mkdir(parents=True, exist_ok=True)
            args.receipt.write_text(json.dumps(receipt, sort_keys=True, indent=2) + '\n')
    except (GateError, json.JSONDecodeError, OSError) as e:
        verdict = ('NOT VERIFIABLE' if dt.datetime.now(dt.timezone.utc) >= CUTOFF
                   else 'BLOCKED_PENDING_EVIDENCE')
        print(f'W47 PREFLIGHT: {verdict} | {e}', file=sys.stderr)
        return 1
    print(f'W47 PREFLIGHT: {verdict} | GitHub review timestamp, reviewer and commit/hash gates passed')
    return 0

if __name__ == '__main__':
    sys.exit(main())

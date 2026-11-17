"""Synthetic-only W47 gate tests. Never read corpus, protected list, or HOLDOUT."""
import importlib.util
import json
import pathlib
import unittest
from unittest.mock import patch

SRC = pathlib.Path(__file__).resolve().parents[1] / 'research/week47-qo-decision/preflight.py'
spec = importlib.util.spec_from_file_location('w47_guard', SRC)
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)

def protocol():
    return {
        'status': 'FROZEN_EXPLORATORY', 'question_type': 'NULL_ONLY',
        'source_corpora': {'ZL3b': g.ZL3B},
        'parser': {'name': 'RC1.2', 'source_sha256': g.RC12,
                   'full_corpus_structural_blocks': 740, 'full_corpus_P_loci': 4130,
                   'full_corpus_tokens': 35492, 'full_corpus_types': 6980},
        'scope': {'population': 'AUTHORIZED_TRAINING_ONLY',
                  'endpoint': 'EXACT_FIRST_WORD_REPETITION'},
        'null_model': {'kind': 'WITHIN_IVTFF_BLOCK_PERMUTE_FIRST_WORDS', 'replicates': 10000},
        'uncertainty': {'cluster_unit': 'physical folio'},
        'cross_transcription_rule': 'discordance=inconclusive',
        'decision_thresholds': dict.fromkeys(
            ('SUPPORTED', 'FALSIFIED', 'INCONCLUSIVE', 'NOT VERIFIABLE'), 'fixed'),
        'deadline_utc': '2026-11-20T17:00:00Z'
    }

def parity():
    return {'canonical_source_sha256': g.ZL3B, 'canonical_parser_sha256': g.RC12,
            'blocks': 740, 'P_loci': 4130, 'tokens': 35492, 'types': 6980,
            'matched_blocks': 740, 'matched_loci': 4130,
            'block_boundary_mismatches': 0, 'token_mismatches': 0,
            'adjacency_mismatches': 0, 'unexplained_differences': 0,
            'matched_token_stream': True, 'matched_pair_eligibility': True,
            'it2a_pair_mapping_checked': True,
            'block_manifest': {}, 'locus_manifest': {}, 'difference_register': {}}

def approval(head, submitted='2026-11-19T12:00:00+00:00', reviewer='IndependentReviewer'):
    return {'repository': g.REPOSITORY, 'pr_number': g.PR_NUMBER,
            'pr_author': g.PR_AUTHOR, 'pr_state': 'open',
            'head_branch': g.APPROVED_BRANCH, 'head_sha': head,
            'review': {'state': 'APPROVED', 'commit_id': head,
                       'reviewer': reviewer, 'submitted_at': submitted}}

class TestW47Guard(unittest.TestCase):
    def test_science_job_uses_dedicated_github_environment(self):
        workflow = SRC.parents[2] / '.github/workflows/week47-qo-gated.yml'
        text = workflow.read_text()
        self.assertRegex(text, r'(?ms)^  experiment:\n(?:(?!^  [a-zA-Z_-]+:).)*?^    environment: w47-science$')

    def test_frozen_null_protocol_accepted(self):
        self.assertEqual(g.check_protocol(json.dumps(protocol()).encode())['question_type'], 'NULL_ONLY')

    def test_generator_comparison_requires_different_protocol(self):
        p = protocol(); p['question_type'] = 'GENERATOR_COMPARISON'
        with self.assertRaises(g.GateError): g.check_protocol(json.dumps(p).encode())

    def test_protocol_hash_endpoint_and_cutoff_are_fixed(self):
        cases = [('source_corpora', 'ZL3b', '0' * 64),
                 ('parser', 'source_sha256', '1' * 64),
                 ('scope', 'endpoint', 'QO_TO_QO'),
                 ('scope', 'population', 'FULL_MANUSCRIPT'),
                 ('deadline_utc', None, '2026-11-25T17:00:00Z')]
        for where, key, value in cases:
            with self.subTest(where=where):
                p = protocol()
                if key is None: p[where] = value
                else: p[where][key] = value
                with self.assertRaises(g.GateError): g.check_protocol(json.dumps(p).encode())

    def test_parser_manifest_needs_all_canonical_checks(self):
        good = parity()
        with patch.object(g, 'immutable_bytes', return_value=b'frozen') as check:
            self.assertIsNotNone(g.check_parser_report(json.dumps(good).encode()))
            self.assertEqual(check.call_count, 3)
        for key, value in [('blocks', 739), ('P_loci', 4129), ('tokens', 35491),
                           ('adjacency_mismatches', 1), ('it2a_pair_mapping_checked', False)]:
            with self.subTest(key=key):
                bad = parity(); bad[key] = value
                with self.assertRaises(g.GateError): g.check_parser_report(json.dumps(bad).encode())

    def test_self_declared_status_does_not_replace_review(self):
        head = 'a' * 40
        self.assertEqual(g.validate_review_approval(approval(head), head)['reviewer'],
                         'IndependentReviewer')
        for bad, message in [
            (approval(head, reviewer=g.PR_AUTHOR), 'other than the PR author'),
            (approval('b' * 40), 'reviewed W47 commit'),
            (approval(head, submitted='2026-11-20T17:00:01+00:00'), 'by the 20 Nov'),
        ]:
            with self.subTest(message=message):
                with self.assertRaisesRegex(g.GateError, message):
                    g.validate_review_approval(bad, head)

    def test_server_review_lookup_binds_approval_to_current_pr_head(self):
        head = 'a' * 40
        pr = {'state': 'open', 'user': {'login': g.PR_AUTHOR},
              'head': {'ref': g.APPROVED_BRANCH, 'sha': head}}
        reviews = [{'state': 'APPROVED', 'commit_id': head,
                    'submitted_at': '2026-11-19T12:00:00Z',
                    'user': {'login': 'IndependentReviewer'}}]
        env = {'GITHUB_REPOSITORY': g.REPOSITORY,
               'GITHUB_EVENT_NAME': 'workflow_dispatch',
               'GITHUB_REF_NAME': g.APPROVED_BRANCH,
               'GITHUB_TOKEN': 'synthetic-token'}
        with patch.dict(g.os.environ, env, clear=True), \
             patch.object(g, 'git', return_value=head.encode()), \
             patch.object(g, 'github_json', side_effect=[pr, reviews]):
            result = g.github_review_approval()
        self.assertEqual(g.validate_review_approval(result, head)['reviewer'],
                         'IndependentReviewer')

    def test_missing_github_api_review_blocks_preflight(self):
        head = 'a' * 40
        pr = {'state': 'open', 'user': {'login': g.PR_AUTHOR},
              'head': {'ref': g.APPROVED_BRANCH, 'sha': head}}
        env = {'GITHUB_REPOSITORY': g.REPOSITORY,
               'GITHUB_EVENT_NAME': 'workflow_dispatch',
               'GITHUB_REF_NAME': g.APPROVED_BRANCH,
               'GITHUB_TOKEN': 'synthetic-token'}
        with patch.dict(g.os.environ, env, clear=True), \
             patch.object(g, 'git', return_value=head.encode()), \
             patch.object(g, 'github_json', side_effect=[pr, []]):
            with self.assertRaisesRegex(g.GateError, 'No non-author GitHub approval'):
                g.github_review_approval()

    def test_gate_bytes_are_bound_to_head_without_git_committer_dates(self):
        head = 'a' * 40
        manifest = {'schema_version': 1, 'question_type': 'NULL_ONLY'}
        encoded = json.dumps(manifest).encode()
        class Root:
            def __truediv__(self, _):
                class File:
                    def read_bytes(self): return encoded
                return File()
        def fake_git(*args):
            if args[:2] == ('rev-parse', 'HEAD'): return head.encode()
            if args[:2] == ('show', f'{head}:{g.GATE_PATH}'): return encoded
            raise AssertionError(f'Unexpected git call: {args}')
        with patch.object(g, 'ROOT', Root()), patch.object(g, 'git', side_effect=fake_git):
            self.assertEqual(g.check_gate_manifest_at_head(manifest), head)

    def test_incomplete_manifest_fails_before_any_science(self):
        manifest = {'schema_version': 1, 'question_type': 'NULL_ONLY',
                    'rivals': {'status': 'NOT_APPLICABLE_NULL_ONLY'}, 'protocol': {},
                    'parser_evidence': {'path': '', 'commit': '', 'sha256': ''}}
        with patch.object(g, 'immutable_bytes', side_effect=lambda item, label, **kw:
                          (_ for _ in ()).throw(g.GateError('full frozen commit required'))):
            with self.assertRaisesRegex(g.GateError, 'full frozen commit required'):
                g.verify(manifest)

    def test_only_expected_evidence_paths_allowed(self):
        for path in ('/tmp/x', '../../HOLDOUT.md', 'data/ZL3b-n.txt',
                     'research/../../HOLDOUT.md', ''):
            with self.subTest(path=path):
                with self.assertRaises(g.GateError): g.clean_path(path)

if __name__ == '__main__': unittest.main()

"""W47 preflight synthetic tests: never open Voynich data or protected folios."""
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
        'status':'FROZEN_EXPLORATORY', 'question_type':'NULL_ONLY',
        'source_corpora':{'ZL3b':g.ZL3B},
        'parser':{'name':'RC1.2','source_sha256':g.RC12,
                  'full_corpus_structural_blocks':740,'full_corpus_P_loci':4130,
                  'full_corpus_tokens':35492,'full_corpus_types':6980},
        'scope':{'population':'AUTHORIZED_TRAINING_ONLY',
                 'endpoint':'EXACT_FIRST_WORD_REPETITION'},
        'null_model':{'kind':'WITHIN_IVTFF_BLOCK_PERMUTE_FIRST_WORDS','replicates':10000},
        'uncertainty':{'cluster_unit':'physical folio'},
        'cross_transcription_rule':'discordance=inconclusive',
        'decision_thresholds':dict.fromkeys(('SUPPORTED','FALSIFIED','INCONCLUSIVE','NOT VERIFIABLE'),'fixed'),
        'deadline_utc':'2026-11-20T17:00:00Z'
    }

def parity():
    return {'status':'VERIFIED','canonical_source_sha256':g.ZL3B,
            'canonical_parser_sha256':g.RC12,
            'blocks':740,'P_loci':4130,'tokens':35492,'types':6980,
            'matched_blocks':740,'matched_loci':4130,
            'block_boundary_mismatches':0,'token_mismatches':0,
            'adjacency_mismatches':0,'unexplained_differences':0,
            'matched_token_stream':True,'matched_pair_eligibility':True,
            'it2a_pair_mapping_checked':True,
            'block_manifest':{},'locus_manifest':{},'difference_register':{}}

class TestW47Guard(unittest.TestCase):
    def test_frozen_null_protocol_accepted(self):
        self.assertEqual(g.check_protocol(json.dumps(protocol()).encode())['question_type'],'NULL_ONLY')
    def test_generator_not_equivalent_to_null(self):
        p=protocol();p['question_type']='GENERATOR_COMPARISON'
        with self.assertRaises(g.GateError):g.check_protocol(json.dumps(p).encode())
    def test_wrong_hashes_and_endpoint_rejected(self):
        for where,key,new in [('source_corpora','ZL3b','0'*64),('parser','source_sha256','1'*64),
                              ('scope','endpoint','QO_TO_QO'),('scope','population','FULL_MANUSCRIPT')]:
            with self.subTest(where=where,key=key):
                p=protocol();p[where][key]=new
                with self.assertRaises(g.GateError):g.check_protocol(json.dumps(p).encode())
    def test_cutoff_cannot_be_extended(self):
        p=protocol();p['deadline_utc']='2026-11-25T17:00:00Z'
        with self.assertRaises(g.GateError):g.check_protocol(json.dumps(p).encode())
    def test_no_parser_evidence_stops_before_any_runner(self):
        m={'schema_version':1,'question_type':'NULL_ONLY',
           'rivals':{'status':'NOT_APPLICABLE_NULL_ONLY'},'protocol':{},
           'parser_evidence':{'status':'PENDING'}}
        with patch.object(g,'immutable_bytes',return_value=json.dumps(protocol()).encode()):
            with self.assertRaisesRegex(g.GateError,'Parser parity evidence PENDING'):
                g.verify(m)
    def test_missing_or_inconsistent_parser_alignment_rejected(self):
        for key,new in [('blocks',739),('P_loci',4129),('tokens',35491),
                        ('matched_blocks',739),('token_mismatches',1),
                        ('adjacency_mismatches',1),('it2a_pair_mapping_checked',False)]:
            with self.subTest(key=key):
                p=parity();p[key]=new
                with self.assertRaises(g.GateError):g.check_parser_report(json.dumps(p).encode())
    def test_parser_evidence_requires_all_three_committed_details(self):
        with patch.object(g,'immutable_bytes',return_value=b'fixed') as verify:
            g.check_parser_report(json.dumps(parity()).encode())
            self.assertEqual(verify.call_count,3)
    def test_no_runner_and_isolation_still_blocks(self):
        m={'schema_version':1,'question_type':'NULL_ONLY',
           'rivals':{'status':'NOT_APPLICABLE_NULL_ONLY'},'protocol':{},
           'parser_evidence':{'status':'VERIFIED'},'runner':{'status':'PENDING'}}
        def source(_, label, **kwargs):
            return json.dumps(protocol() if label=='protocol' else parity()).encode()
        with patch.object(g,'immutable_bytes',side_effect=source):
            with patch.object(g,'check_parser_report',return_value={}):
                with self.assertRaisesRegex(g.GateError,'Isolated runner NOT APPROVED'):
                    g.verify(m)
    def test_only_research_evidence_paths_allowed(self):
        for path in ('/tmp/x','../../HOLDOUT.md','data/ZL3b-n.txt',
                     'research/../../HOLDOUT.md',''):
            with self.subTest(path=path):
                with self.assertRaises(g.GateError):g.clean_path(path)

if __name__=='__main__':unittest.main()

import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

SCRIPT = Path(__file__).with_name("score.py")
spec = importlib.util.spec_from_file_location('quality_score', SCRIPT)
score = importlib.util.module_from_spec(spec)
spec.loader.exec_module(score)

class ScoreContract(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'proof.log').write_text('actual checked fixture result\n')
        self.proof = [{'path': 'proof.log', 'sha256': hashlib.sha256((self.root/'proof.log').read_bytes()).hexdigest()}]
        self.plan = {'schema_version': 1, 'assessment_id': 'fixture', 'frozen_at': '2026-10-20T00:00:00Z', 'target': 9.5, 'scope': {'files': ['fixture.py'], 'exclusions': []}, 'dimensions': []}
        for d in score.DIMENSIONS:
            self.plan['dimensions'].append({'id': d, 'applicable': True, 'criteria': [{'id': d+'.large', 'weight': 99, 'critical': False, 'pass_condition': 'fixture contract holds', 'evidence_level': 'executed contract log', 'raw_measure': 'passed / total'}, {'id': d+'.boundary', 'weight': 1, 'critical': True, 'pass_condition': 'boundary holds', 'evidence_level': 'executed boundary log', 'raw_measure': 'passed / total'}]})
        self.observations = {'schema_version': 1, 'assessment_id': 'fixture', 'plan_sha256': score.digest(self.plan), 'scope_sha256': score.digest(self.plan['scope']), 'observed_at': '2026-10-20T01:00:00Z', 'source': {'revision': 'fixture-revision', 'diff_sha256': '0'*64}, 'criteria': [{'id': c['id'], 'status': 'PASS', 'reason': 'verified fixture', 'raw': {'passed': 1, 'total': 1}, 'evidence': copy.deepcopy(self.proof)} for d in self.plan['dimensions'] for c in d['criteria']]}

    def run_score(self):
        return score.score(self.plan, self.observations, self.root)

    def test_all_pass(self):
        result = self.run_score()
        self.assertTrue(result['all_applicable_dimensions_met'])
        self.assertEqual([r['score'] for r in result['dimensions']], [10.0]*8)

    def test_critical_fail_and_unknown_block_high_score(self):
        for status in ['FAIL', 'UNAVAILABLE', 'NOT RUN']:
            with self.subTest(status=status):
                self.observations['criteria'][1]['status'] = status
                row = self.run_score()['dimensions'][0]
                self.assertEqual(row['score'], 9.9)
                self.assertFalse(row['target_met'])
                self.assertEqual(row['critical_blockers'][0]['status'], status)

    def test_unknown_preserves_denominator(self):
        self.observations['criteria'][0].update(status='UNAVAILABLE', evidence=[], raw={'passed': None, 'total': 1, 'missing': 'runtime'})
        row = self.run_score()['dimensions'][0]
        self.assertEqual(row['total_weight'], 100)
        self.assertEqual(row['unknown_weight'], 99)
        self.assertEqual(row['possible_interval'], [0.1, 10.0])
        self.assertFalse(row['target_met'])

    def test_noncritical_failure_stays_in_denominator(self):
        self.observations['criteria'][0]['status'] = 'FAIL'
        row = self.run_score()['dimensions'][0]
        self.assertEqual(row['score'], 0.1)
        self.assertEqual(row['status_weights']['FAIL'], 99)

    def test_evidence_refusals(self):
        mutations = [[], [{'path': 'absent.log', 'sha256': '0'*64}], [{'path': 'proof.log', 'sha256': '0'*64}], [{'path': '../escape.log', 'sha256': '0'*64}]]
        for evidence in mutations:
            with self.subTest(evidence=evidence):
                self.observations['criteria'][0]['evidence'] = evidence
                with self.assertRaises(ValueError): self.run_score()

    def test_unknown_with_supplied_missing_evidence_is_rejected(self):
        self.observations['criteria'][0].update(status='NOT RUN', evidence=[{'path': 'absent.log', 'sha256': '0'*64}])
        with self.assertRaises(ValueError): self.run_score()

    def test_inventory_and_hash_refusals(self):
        original = copy.deepcopy(self.observations)
        for mutation in ['missing', 'extra', 'duplicate', 'scope_hash', 'plan_hash', 'assessment_id']:
            with self.subTest(mutation=mutation):
                self.observations = copy.deepcopy(original)
                if mutation == 'missing': self.observations['criteria'].pop()
                elif mutation == 'extra': self.observations['criteria'].append({**self.observations['criteria'][0], 'id': 'extra'})
                elif mutation == 'duplicate': self.observations['criteria'].append(self.observations['criteria'][0])
                elif mutation == 'scope_hash': self.observations['scope_sha256'] = '0'*64
                elif mutation == 'plan_hash': self.observations['plan_sha256'] = '0'*64
                else: self.observations['assessment_id'] = 'other'
                with self.assertRaises(ValueError): self.run_score()

    def test_changed_threshold_requires_new_assessment_hash(self):
        self.plan['target'] = 1
        with self.assertRaisesRegex(ValueError, 'plan_sha256 mismatch'): self.run_score()

    def test_na_requires_evidence_and_is_not_ten(self):
        self.plan['dimensions'][0] = {'id': 'functional', 'applicable': False, 'criteria': [], 'reason': 'fixture application has no scoped functional contracts', 'evidence': self.proof}
        self.observations['plan_sha256'] = score.digest(self.plan)
        self.observations['criteria'] = [c for c in self.observations['criteria'] if not c['id'].startswith('functional.')]
        row = self.run_score()['dimensions'][0]
        self.assertEqual(row['status'], 'N/A')
        self.assertIsNone(row['score'])
        self.plan['dimensions'][0]['evidence'] = []
        with self.assertRaises(ValueError): score.validate_plan(self.plan, self.root)

    def test_cli_codes_and_strict_json(self):
        plan_path, obs_path = self.root/'plan.json', self.root/'observations.json'
        plan_path.write_text(json.dumps(self.plan))
        obs_path.write_text(json.dumps(self.observations))
        prefix = ['python3', str(SCRIPT)]
        def call(mode, observations=True):
            return subprocess.run(prefix+[mode, str(plan_path)]+([str(obs_path)] if observations else [])+['--evidence-root', str(self.root)], capture_output=True, text=True)
        self.assertEqual(call('freeze', False).returncode, 0)
        self.assertEqual(call('score').returncode, 0)
        self.observations['criteria'][0]['status'] = 'FAIL'
        obs_path.write_text(json.dumps(self.observations))
        result = call('score')
        self.assertEqual(result.returncode, 1)
        self.assertFalse(json.loads(result.stdout)['all_applicable_dimensions_met'])
        for invalid in ['{"schema_version": 1, "schema_version": 1}', '{"target": NaN}']:
            plan_path.write_text(invalid)
            result = call('score')
            self.assertEqual(result.returncode, 2)
            self.assertEqual(result.stdout, '')
            self.assertIn('error', json.loads(result.stderr))

if __name__ == '__main__': unittest.main(verbosity=2)

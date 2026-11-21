"""Tests for the static IaC teardown preflight checker with planted defects."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).with_name('preflight_tf.py')


class PreflightTfTests(unittest.TestCase):
    def run_cli(self, *args: str):
        proc = subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            text=True, capture_output=True, check=False,
        )
        return proc, (json.loads(proc.stdout) if proc.stdout.strip() else None)

    def test_planted_teardown_traps_and_comment_ignoring(self):
        with tempfile.TemporaryDirectory() as tmp:
            tf_dir = Path(tmp)
            (tf_dir / 'main.tf').write_text(
                '# prevent_destroy = true inside a comment must be ignored\n'
                '/* import { to = aws_route53_record.ignored } */\n'
                'import {\n'
                '  to = aws_route53_record.site_apex\n'
                '  id = "Z123_example.com_A"\n'
                '}\n'
                'resource "aws_route53_record" "site_apex" {\n'
                '  zone_id = "Z123"\n'
                '  name    = "example.com"\n'
                '  type    = "A"\n'
                '}\n'
                'resource "aws_route53_record" "dmarc" {\n'
                '  zone_id = "Z123"\n'
                '  name    = "_dmarc.example.com"\n'
                '  type    = "TXT"\n'
                '}\n'
                'resource "aws_s3_bucket" "backups" {\n'
                '  bucket = "example-backups"\n'
                '  lifecycle {\n'
                '    prevent_destroy = true\n'
                '  }\n'
                '}\n'
                'resource "aws_cognito_user_pool" "operators" {\n'
                '  name                = "operators"\n'
                '  deletion_protection = "ACTIVE"\n'
                '}\n'
                'resource "aws_ecr_repository" "app" {\n'
                '  name = "app"\n'
                '}\n',
                encoding='utf-8',
            )
            state_file = tf_dir / 'state.txt'
            state_file.write_text('aws_s3_bucket.backups\naws_route53_record.dmarc\n', encoding='utf-8')

            proc, report = self.run_cli(str(tf_dir), '--state-list', str(state_file))
            self.assertEqual(proc.returncode, 2, proc.stderr)
            self.assertFalse(report['clean'])
            counts = report['counts']
            self.assertEqual(counts['unapplied_import_block'], 1)
            self.assertEqual(counts['shared_dns_or_email_record'], 2)
            self.assertEqual(counts['lifecycle_lock'], 1)
            self.assertEqual(counts['deletion_protection'], 1)
            self.assertEqual(counts['versioned_or_nonempty_store'], 2)

            unapplied = next(f for f in report['findings'] if f['rule'] == 'unapplied_import_block')
            self.assertEqual(unapplied['severity'], 'high')
            self.assertEqual(unapplied['address'], 'aws_route53_record.site_apex')

    def test_clean_stack_and_stale_import_distinction(self):
        with tempfile.TemporaryDirectory() as tmp:
            tf_dir = Path(tmp)
            (tf_dir / 'clean.tf').write_text(
                'resource "aws_s3_bucket" "scratch" {\n'
                '  bucket        = "scratch"\n'
                '  force_destroy = true\n'
                '}\n'
                'resource "aws_ecr_repository" "scratch" {\n'
                '  name         = "scratch"\n'
                '  force_delete = true\n'
                '}\n',
                encoding='utf-8',
            )
            proc, report = self.run_cli(str(tf_dir))
            self.assertEqual((proc.returncode, report['clean']), (0, True))

            (tf_dir / 'imports.tf').write_text(
                'import {\n  to = aws_s3_bucket.scratch\n  id = "scratch"\n}\n',
                encoding='utf-8',
            )
            state_file = tf_dir / 'state.txt'
            state_file.write_text('aws_s3_bucket.scratch\n', encoding='utf-8')
            proc2, report2 = self.run_cli(str(tf_dir), '--state-list', str(state_file))
            self.assertEqual(proc2.returncode, 2)
            self.assertEqual(report2['counts'].get('stale_import_block'), 1)
            self.assertIsNone(report2['counts'].get('unapplied_import_block'))

    def test_plan_json_flags_mixed_drift_and_deferred_db_change(self):
        with tempfile.TemporaryDirectory() as tmp:
            tf_dir = Path(tmp)
            (tf_dir / 'empty.tf').write_text('terraform {}\n', encoding='utf-8')
            plan = tf_dir / 'plan.json'
            plan.write_text(json.dumps({
                'resource_changes': [
                    {
                        'address': 'aws_cloudwatch_metric_alarm.old',
                        'type': 'aws_cloudwatch_metric_alarm',
                        'change': {'actions': ['delete'], 'before': {}, 'after': None},
                    },
                    {
                        'address': 'aws_lambda_function.unrelated',
                        'type': 'aws_lambda_function',
                        'change': {'actions': ['update'], 'before': {}, 'after': {}},
                    },
                    {
                        'address': 'aws_rds_cluster.reader',
                        'type': 'aws_rds_cluster',
                        'change': {
                            'actions': ['update'],
                            'before': {'manage_master_user_password': True, 'apply_immediately': None},
                            'after': {'manage_master_user_password': None, 'apply_immediately': None},
                        },
                    },
                ],
            }), encoding='utf-8')
            proc, report = self.run_cli(str(tf_dir), '--plan-json', str(plan))
            self.assertEqual(proc.returncode, 2)
            self.assertEqual(report['counts'].get('plan_unexpected_drift'), 2)
            self.assertEqual(report['counts'].get('deferred_db_change'), 1)

    def test_locals_data_or_import_attr_does_not_swallow_following_resource(self):
        with tempfile.TemporaryDirectory() as tmp:
            tf_dir = Path(tmp)
            (tf_dir / 'locals.tf').write_text(
                'locals {\n'
                '  data   = var.input\n'
                '  import = "safe"\n'
                '}\n'
                'resource "aws_route53_record" "dmarc" {\n'
                '  zone_id = "Z123"\n'
                '  name    = "_dmarc.example.com"\n'
                '  type    = "TXT"\n'
                '}\n',
                encoding='utf-8',
            )
            proc, report = self.run_cli(str(tf_dir))
            self.assertEqual(proc.returncode, 2, proc.stderr)
            self.assertEqual(report['counts'].get('shared_dns_or_email_record'), 1)
            self.assertIsNone(report['counts'].get('unapplied_import_block'))

    def test_snake_case_validation_and_txt_dns_records_are_high_severity(self):
        with tempfile.TemporaryDirectory() as tmp:
            tf_dir = Path(tmp)
            (tf_dir / 'dns.tf').write_text(
                'resource "aws_route53_record" "apex_spf" {\n'
                '  zone_id = "Z1"\n'
                '  name    = var.domain_name\n'
                '  type    = "TXT"\n'
                '}\n'
                'resource "aws_route53_record" "site_ownership" {\n'
                '  zone_id = "Z1"\n'
                '  name    = "example.com"\n'
                '  type    = "TXT"\n'
                '}\n'
                'resource "aws_route53_record" "cert_demo_validation" {\n'
                '  zone_id = "Z1"\n'
                '  name    = local.cert_demo_validation_name\n'
                '  type    = "CNAME"\n'
                '}\n'
                'resource "aws_route53_record" "candidate_a" {\n'
                '  zone_id = "Z1"\n'
                '  name    = "mw.example.com"\n'
                '  type    = "A"\n'
                '}\n',
                encoding='utf-8',
            )
            proc, report = self.run_cli(str(tf_dir))
            self.assertEqual(proc.returncode, 2, proc.stderr)
            by_addr = {f['address']: f['severity'] for f in report['findings']}
            self.assertEqual(by_addr['aws_route53_record.apex_spf'], 'high')
            self.assertEqual(by_addr['aws_route53_record.site_ownership'], 'high')
            self.assertEqual(by_addr['aws_route53_record.cert_demo_validation'], 'high')
            self.assertEqual(by_addr['aws_route53_record.candidate_a'], 'medium')

    def test_missing_path_exits_one(self):
        proc, _ = self.run_cli('/nonexistent/path/to/tf')
        self.assertEqual(proc.returncode, 1)
        self.assertIn('does not exist', proc.stderr)

    def test_non_tf_explicit_file_exits_one(self):
        with tempfile.TemporaryDirectory() as tmp:
            txt = Path(tmp) / 'notes.txt'
            txt.write_text('not terraform', encoding='utf-8')
            proc, _ = self.run_cli(str(txt))
            self.assertEqual(proc.returncode, 1)
            self.assertIn('.tf', proc.stderr)

    def test_heredoc_with_unquoted_comment_or_quote_preserves_following_blocks(self):
        with tempfile.TemporaryDirectory() as tmp:
            tf_dir = Path(tmp)
            tf_file = tf_dir / 'heredoc.tf'
            tf_file.write_text(
                'locals {\n'
                '  script = <<-EOF\n'
                '    /* unclosed comment in heredoc\n'
                '    echo "unclosed quote\n'
                '  EOF\n'
                '}resource "aws_s3_bucket" "locked" {\n'
                '  bucket = "locked-bucket"\n'
                '  lifecycle {\n'
                '    prevent_destroy = true\n'
                '  }\n'
                '}\n'
                'resource "aws_route53_zone" "main" {\n'
                '  name = "example.com"\n'
                '}\n'
                'resource "cloudflare_dns_record" "web" {\n'
                '  zone_id = "z1"\n'
                '  name    = "www"\n'
                '  type    = "CNAME"\n'
                '}\n',
                encoding='utf-8',
            )
            proc, report = self.run_cli(str(tf_file))
            self.assertEqual(proc.returncode, 2, proc.stderr)
            self.assertEqual(report['counts'].get('lifecycle_lock'), 1)
            self.assertEqual(report['counts'].get('versioned_or_nonempty_store'), 1)
            self.assertEqual(report['counts'].get('shared_dns_or_email_record'), 2)
            lock = next(f for f in report['findings'] if f['rule'] == 'lifecycle_lock')
            self.assertEqual(lock['line'], 9)
            zone = next(f for f in report['findings'] if f['address'] == 'aws_route53_zone.main')
            self.assertEqual(zone['severity'], 'high')

    def test_quoted_map_key_import_matches_state_and_plan_create_drift(self):
        with tempfile.TemporaryDirectory() as tmp:
            tf_dir = Path(tmp)
            (tf_dir / 'imports.tf').write_text(
                'import {\n'
                '  to = aws_ssm_parameter.cfg["/prod/key"]\n'
                '  id = "/prod/key"\n'
                '}\n',
                encoding='utf-8',
            )
            state_file = tf_dir / 'state.txt'
            state_file.write_text('aws_ssm_parameter.cfg["/prod/key"]\n', encoding='utf-8')
            plan = tf_dir / 'plan.json'
            plan.write_text(json.dumps({
                'resource_changes': [
                    {
                        'address': 'aws_s3_bucket.old',
                        'type': 'aws_s3_bucket',
                        'change': {'actions': ['delete'], 'before': {}, 'after': None},
                    },
                    {
                        'address': 'aws_ssm_parameter.new_drift',
                        'type': 'aws_ssm_parameter',
                        'change': {'actions': ['create'], 'before': None, 'after': {}},
                    },
                ],
            }), encoding='utf-8')
            proc, report = self.run_cli(
                str(tf_dir), '--state-list', str(state_file), '--plan-json', str(plan)
            )
            self.assertEqual(proc.returncode, 2, proc.stderr)
            self.assertEqual(report['counts'].get('stale_import_block'), 1)
            self.assertIsNone(report['counts'].get('unapplied_import_block'))
            stale = next(f for f in report['findings'] if f['rule'] == 'stale_import_block')
            self.assertEqual(stale['address'], 'aws_ssm_parameter.cfg["/prod/key"]')
            self.assertEqual(report['counts'].get('plan_unexpected_drift'), 1)


if __name__ == '__main__':
    unittest.main()

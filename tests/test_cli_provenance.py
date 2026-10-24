import unittest,subprocess,sys,json,copy
from voltvar.cli import load_case
from voltvar.studies import run
class CliProvenance(unittest.TestCase):
    def test_cli_examples(self):
        r=subprocess.run([sys.executable,'-m','voltvar.cli','examples'],capture_output=True,text=True);self.assertEqual(r.returncode,0);self.assertIn('industrial',r.stdout)
    def test_cli_study(self):
        r=subprocess.run([sys.executable,'-m','voltvar.cli','study','example:industrial'],capture_output=True,text=True);self.assertEqual(r.returncode,0,r.stderr);self.assertIn('provenance',json.loads(r.stdout))
    def test_unknown_study(self):
        with self.assertRaises(ValueError):run(load_case('example:industrial'),'unknown')
    def test_fingerprint_repeatable(self):
        m=load_case('example:industrial');self.assertEqual(run(m)['provenance'],run(copy.deepcopy(m))['provenance'])
    def test_inputs_preserved(self):
        m=load_case('example:industrial');before=copy.deepcopy(m);run(m);self.assertEqual(m,before)

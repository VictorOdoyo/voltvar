import unittest,json
from pathlib import Path
import numpy as np
from voltvar._gridflow.solver import solve
class ExternalCase9(unittest.TestCase):
    def test_newton_external(self):self.compare('newton')
    def test_gauss_seidel_external(self):self.compare('gauss_seidel')
    def test_fast_decoupled_external(self):self.compare('fast_decoupled')
    def compare(self,method):
        ref=json.loads((Path(__file__).parents[1]/'benchmarks/case9-reference.json').read_text(encoding='utf-8'));r=solve(ref['network'],method)
        self.assertTrue(r['converged']);np.testing.assert_allclose([b['vm_pu'] for b in r['buses']],ref['expected']['vm_pu'],atol=1e-8,rtol=0);np.testing.assert_allclose([b['va_deg'] for b in r['buses']],ref['expected']['va_deg'],atol=1e-6,rtol=0)
        flows=[[b[k] for k in ['p_from_mw','q_from_mvar','p_to_mw','q_to_mvar']] for b in r['branches']];np.testing.assert_allclose(flows,ref['expected']['branch_power_columns_pf_qf_pt_qt'],atol=2e-6,rtol=0)

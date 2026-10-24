import unittest
from voltvar.cli import load_case
from voltvar.regulators import regulate
from voltvar.profiles import time_series
class Regulators(unittest.TestCase):
    def test_local_terminates_explicitly(self):
        r=regulate(load_case('example:industrial'));self.assertIn(r['discrete_reason'],['settled_or_at_bounds','control_cycle','inverter_not_converged','round_limit']);self.assertLessEqual(len(r['discrete_history']),40)
    def test_round_limit_not_feasible(self):
        m=load_case('example:industrial');m['network']['loads'][0]['q_mvar']=4
        r=regulate(m,max_rounds=1,deadband_pu=.001)
        if not r['discrete_converged']:self.assertFalse(r['feasible'])
    def test_local_profile(self):
        m=load_case('example:industrial');r=time_series(m,m['profile'],mode='local');self.assertEqual(len(r['periods']),4)

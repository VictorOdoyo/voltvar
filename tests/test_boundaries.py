import unittest,copy
from voltvar.cli import load_case
from voltvar.devices import *
from voltvar.control import optimize,local_control
from voltvar.evaluate import assess
from voltvar.profiles import uncertain_solar
from voltvar.model import validate
class Boundaries(unittest.TestCase):
    def test_capability_overrated(self):
        with self.assertRaises(ValueError):reactive_capability(2,1)
    def test_curve_not_increasing(self):
        with self.assertRaises(ValueError):volt_var(1,[[1,0],[.9,1]],1)
    def test_curve_fraction_limit(self):
        with self.assertRaises(ValueError):volt_var(1,[[.9,2],[1,0]],1)
    def test_fractional_tap(self):
        with self.assertRaises(ValueError):tap_ratio(.5)
    def test_negative_capacitor(self):
        with self.assertRaises(ValueError):capacitor_output(-1,.5)
    def test_search_limit(self):
        with self.assertRaises(ValueError):optimize(load_case('example:industrial'),max_candidates=1)
    def test_invalid_q_command(self):
        with self.assertRaises(ValueError):assess(load_case('example:industrial'),reactive={'solar':99})
    def test_nonconverged_local_reported(self):
        r=local_control(load_case('example:industrial'),max_iterations=1,tolerance=1e-10)
        self.assertIn('control_converged',r)
        if not r['control_converged']:self.assertFalse(r['feasible'])
    def test_uncertainty_outside_circle(self):
        r=uncertain_solar(load_case('example:industrial'),[1,2]);self.assertFalse(r['robust_feasible']);self.assertIn('error',r['scenarios'][-1])
    def test_unknown_bus(self):
        m=load_case('example:industrial');m['inverters'][0]['bus']='absent'
        with self.assertRaises(ValueError):validate(m)
    def test_boolean_positions(self):
        with self.assertRaises(ValueError):assess(load_case('example:industrial'),[True,0])
    def test_optimization_grid_lower_bound(self):
        r=optimize(load_case('example:industrial'));feasible=[x['score'] for x in r['candidates'] if x['feasible']];self.assertAlmostEqual(r['best']['score'],min(feasible))

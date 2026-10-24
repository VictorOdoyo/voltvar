import unittest,json
from pathlib import Path
from tests.reference_runner import verify
class Reference(unittest.TestCase):
    def test_power_factor_03(self):
        case=json.loads((Path(__file__).parents[1]/'references/power_factor_03.json').read_text(encoding='utf-8'))
        verify(self,case)

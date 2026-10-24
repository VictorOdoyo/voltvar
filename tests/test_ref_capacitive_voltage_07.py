import unittest,json
from pathlib import Path
from tests.reference_runner import verify
class Reference(unittest.TestCase):
    def test_capacitive_voltage_07(self):
        case=json.loads((Path(__file__).parents[1]/'references/capacitive_voltage_07.json').read_text(encoding='utf-8'))
        verify(self,case)

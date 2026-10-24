import unittest,json
from pathlib import Path
from tests.reference_runner import verify
class Reference(unittest.TestCase):
    def test_local_deadband_10(self):
        case=json.loads((Path(__file__).parents[1]/'references/local_deadband_10.json').read_text(encoding='utf-8'))
        verify(self,case)

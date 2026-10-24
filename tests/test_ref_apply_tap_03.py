import unittest,json
from pathlib import Path
from tests.reference_runner import verify
class Reference(unittest.TestCase):
    def test_apply_tap_03(self):
        case=json.loads((Path(__file__).parents[1]/'references/apply_tap_03.json').read_text(encoding='utf-8'))
        verify(self,case)

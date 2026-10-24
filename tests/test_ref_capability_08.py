import unittest,json
from pathlib import Path
from tests.reference_runner import verify
class Reference(unittest.TestCase):
    def test_capability_08(self):
        case=json.loads((Path(__file__).parents[1]/'references/capability_08.json').read_text(encoding='utf-8'))
        verify(self,case)

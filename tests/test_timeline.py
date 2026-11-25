import unittest,json
from scripts.smoke import ROOT,validate_timeline
class TimelineTests(unittest.TestCase):
    def setUp(self): self.ir=json.loads((ROOT/'fixtures/video_ir.synthetic.json').read_text())
    def test_valid(self): validate_timeline(self.ir)
    def test_gap(self):
        self.ir['scenes'][1]['start_frame']+=1
        with self.assertRaises(ValueError): validate_timeline(self.ir)
    def test_overlap(self):
        self.ir['scenes'][1]['start_frame']-=1
        with self.assertRaises(ValueError): validate_timeline(self.ir)
    def test_missing_end(self):
        self.ir['scenes'].pop()
        with self.assertRaises(ValueError): validate_timeline(self.ir)
    def test_duplicate_id(self):
        self.ir['scenes'][1]['id']=self.ir['scenes'][0]['id']
        with self.assertRaises(ValueError): validate_timeline(self.ir)

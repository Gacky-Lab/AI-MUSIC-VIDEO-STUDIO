import copy,hashlib,unittest
from scripts.lyric_preview import make_props
class PreviewTests(unittest.TestCase):
    def setUp(self):
        self.h={"contract_version":"1.0.0","lyric_version_id":"v1","lyrics_text":"first\nsecond"}
        self.h["lyrics_sha256"]=hashlib.sha256(self.h["lyrics_text"].encode()).hexdigest()
        self.digest="a"*64
        self.t={"schema_version":"0.1.0","master_sha256":self.digest,"lyrics_sha256":self.h["lyrics_sha256"],"lyric_version_id":"v1","review_status":"HUMAN_APPROVED_FOR_PREVIEW","cues":[{"start_ms":1000,"end_ms":4000,"line_index":0},{"start_ms":4000,"end_ms":7000,"line_index":1}]}
    def test_crop(self):
        p=make_props(self.h,self.t,self.digest,2000)
        self.assertEqual(p["cues"],[{"startFrame":0,"endFrame":60,"text":"first"},{"startFrame":60,"endFrame":150,"text":"second"}])
    def test_hash(self):
        with self.assertRaises(ValueError): make_props(self.h,self.t,"b"*64,0)
    def test_lyric_change(self):
        self.h["lyrics_text"]="altered"
        with self.assertRaises(ValueError): make_props(self.h,self.t,self.digest,0)
    def test_overlap(self):
        self.t["cues"][1]["start_ms"]=3000
        with self.assertRaises(ValueError): make_props(self.h,self.t,self.digest,0)
    def test_not_approved(self):
        self.t["review_status"]="PENDING"
        with self.assertRaises(ValueError): make_props(self.h,self.t,self.digest,0)
    def test_mir_hash(self):
        with self.assertRaises(ValueError): make_props(self.h,self.t,self.digest,0,{"schema_version":"0.1.0","source_sha256":"wrong"})
    def test_unknown_pulse(self):
        p=make_props(self.h,self.t,self.digest,0,{"schema_version":"0.1.0","source_sha256":self.digest,"pulse":{"status":"UNKNOWN","verified_musical_bpm":False}})
        self.assertEqual(p["pulses"],[])
    def test_frame_collapse(self):
        self.t["cues"]=[{"start_ms":1000,"end_ms":1001,"line_index":0}]
        with self.assertRaises(ValueError): make_props(self.h,self.t,self.digest,0)

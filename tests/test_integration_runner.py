import tempfile
import unittest
import wave
from pathlib import Path
from scripts import integration_runner as r

class IntegrationTests(unittest.TestCase):
    def test_reject(self):
        with self.assertRaises(AssertionError): r.reject(lambda: None)
        r.reject(lambda: r.require(False,"bad"))
    def test_synthetic_source(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"source.wav"
            r.synthesize([{"start_sample":0,"end_sample":24000,"pitch_midi":69}],p)
            with wave.open(str(p),"rb") as w: self.assertEqual(w.getnframes(),8000)
            with self.assertRaises(ValueError): r.synthesize([{"start_sample":1,"end_sample":24000,"pitch_midi":69}],p)
    def test_failure_report(self):
        with tempfile.TemporaryDirectory() as d:
            out=Path(d)/"out"
            self.assertEqual(r.execute(Path(d)/"absent",out),1)
            report=r.read(out/"report.json")
            self.assertEqual(report["stages"]["provenance"],"FAIL")
            self.assertEqual(report["stages"]["lyric"],"NOT_RUN")
            self.assertEqual(report["live_suno"],"NOT_RUN")
            with self.assertRaises(FileExistsError): r.execute(Path(d),out)

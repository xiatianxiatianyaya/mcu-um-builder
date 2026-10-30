import copy
import json
import tempfile
import unittest
from pathlib import Path
from build_um import validate, build
from audit_docx import audit
from figure_tools import render

BASE=Path(__file__).resolve().parents[1]/'assets'/'demo'

class UMTests(unittest.TestCase):
    def setUp(self): self.m=json.loads((BASE/'model.json').read_text(encoding='utf-8'))
    def test_valid(self): validate(self.m)
    def test_overlap(self):
        self.m['peripherals'][0]['registers'].append(copy.deepcopy(self.m['peripherals'][0]['registers'][0]))
        self.m['peripherals'][0]['registers'][1]['name']='OTHER'
        with self.assertRaises(ValueError): validate(self.m)
    def test_field_overlap(self):
        r=self.m['peripherals'][0]['registers'][0]; r['fields'].append(copy.deepcopy(r['fields'][0]))
        with self.assertRaises(ValueError): validate(self.m)
    def test_reset_overflow(self):
        self.m['peripherals'][0]['registers'][0]['reset_value']=2**32
        with self.assertRaises(ValueError): validate(self.m)
    def test_enum_overflow(self):
        self.m['peripherals'][1]['registers'][0]['fields'][0]['enums'][0]['value']=2**8
        with self.assertRaises(ValueError): validate(self.m)
    def test_address_mismatch(self):
        self.m['peripherals'][0]['registers'][0]['address']+=4
        with self.assertRaises(ValueError): validate(self.m)
    def test_output_and_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)/'out'; path=build(BASE/'model.json',BASE/'content.json',out)
            self.assertTrue(audit(path)['structural_pass'])
            self.assertEqual(audit(path)['images'],4)
            with self.assertRaises(FileExistsError): build(BASE/'model.json',BASE/'content.json',out)
    def test_unsupported_figure(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError): render({'width':100,'height':100,'items':[{'type':'unknown'}]},Path(tmp)/'fig')

if __name__=='__main__': unittest.main()

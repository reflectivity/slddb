import unittest
import os
from glob import glob
from slddb.importers import CifImporter

NO_VALIDATION = ['7lzm.cif']

class TestFormula(unittest.TestCase):

    def test_import(self):
        fls=glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_data', '*.cif'))

        for fi in fls:
            res=CifImporter(fi, validate=os.path.basename(fi) not in NO_VALIDATION)
            repr(res)
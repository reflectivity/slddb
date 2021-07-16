import unittest
import os
from glob import glob
from slddb.importers import CifImporter

class TestFormula(unittest.TestCase):

    def test_import(self):
        fls=glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_data', '*.cif'))

        for fi in fls:
            res=CifImporter(fi)
            repr(res)
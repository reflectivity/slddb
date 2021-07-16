import os
import unittest
import json
from glob import glob
from slddb import SLDDB


class TestMaterialDB(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db=SLDDB(':memory:')
        cls.db.create_database()

    def test_noimport(self):
        with self.assertRaises(IOError):
            self.db.import_material('file.does.not.exist')

    def test_cif(self):
        fls=glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_data', '*.cif'))

        for fi in fls:
            self.db.import_material(fi)

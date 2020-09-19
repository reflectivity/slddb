import unittest
from slddb import SLDDB
from slddb.material import Formula

class TestFormula(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db=SLDDB(':memory:')
        cls.db.create_database()
        cls.db.add_elements()

    def test_valid(self):
        Formula('NaCl')
        Formula('H2 O')
        Formula('Cr3O4')
        Formula('H12 C5O8')

    def test_invalid(self):
        with self.assertRaises(ValueError):
            f=Formula('Beer')
        with self.assertRaises(ValueError):
            f=Formula('')
        with self.assertRaises(ValueError):
            f=Formula('(Fe)3')

    def test_merge(self):
        f1=Formula('NaCl')
        f2=Formula('NaCl')
        self.assertEqual(f1,f2)

        f2=Formula('Na1Cl1')
        self.assertEqual(f1,f2)

        f2=Formula('Na0.5Cl1Na0.5')
        self.assertEqual(f1,f2)

        f2=Formula('ClNa1.0')
        self.assertEqual(f1,f2)

    def test_strparse(self):
        str(Formula('NaCl'))
        str(Formula('Na1Cl1.0'))
        str(Formula('Na0.5Cl2'))

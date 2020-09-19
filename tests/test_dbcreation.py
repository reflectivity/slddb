import unittest
from slddb import SLDDB, dbconfig
from numpy import ndarray, testing

class TestCreateDB(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.db=SLDDB(':memory:')
        cls.db.create_database()

    @classmethod
    def tearDownClass(cls):
        del(cls.db)

    def test_tables(self):
        c=self.db.db.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type='table'")
        items=c.fetchall()
        for i, tbl in enumerate([dbconfig.DB_MATERIALS_NAME,
                                 dbconfig.DB_ELEMENTS_NAME,
                                 dbconfig.DB_ISOTOPES_NAME,
                                 dbconfig.DB_SLDATA_NAME]):
            with self.subTest(msg=tbl, i=i):
                self.assertTrue((tbl,) in items)

    def test_elements(self):
        # check validity of elements by trying back conversion
        c=self.db.db.cursor()
        c.execute('select * from %s'%dbconfig.DB_ELEMENTS_NAME)
        for i, element in enumerate(c.fetchall()):
            with self.subTest(i=i):
                [ci.revert(element[i]) for i, ci
                 in enumerate(dbconfig.DB_ELEMENTS_CONVERTERS)]

    def test_isotopes(self):
        # check validity of isotopes by trying back conversion
        c=self.db.db.cursor()
        c.execute('select * from %s'%dbconfig.DB_ISOTOPES_NAME)
        for i, isotope in enumerate(c.fetchall()):
            with self.subTest(i=i):
                [ci.revert(isotope[i]) for i, ci
                 in enumerate(dbconfig.DB_ISOTOPES_CONVERTERS)]

    def test_sldata(self):
        # check validity of scattering data by trying back conversion
        c=self.db.db.cursor()
        c.execute('select * from %s'%dbconfig.DB_SLDATA_NAME)
        for i, element in enumerate(c.fetchall()):
            with self.subTest(i=i):
                self.assertTrue(
                    type(dbconfig.DB_SLDATA_CONVERTERS[1].revert(element[1]))
                    is ndarray)

    def test_element_search(self):
        with self.subTest('database search', i=0):
            s1=self.db.elements.get_element('Si')
            s2=self.db.elements.get_element(14)
        with self.subTest('equality', i=0):
            self.assertEqual(s1.Z, s2.Z)
            self.assertEqual(s1.symbol, s2.symbol)
            self.assertEqual(s1.mass, s2.mass)
            self.assertEqual(s1.b, s2.b)
            testing.assert_array_equal(s1._xdata, s2._xdata)

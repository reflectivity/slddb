import unittest
from slddb import SLDDB
from slddb.material import Material
from slddb.element_table import Element
from slddb.constants import Cu_kalpha, Mo_kalpha

class TestMaterial(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db=SLDDB(':memory:')
        cls.db.create_database()

    def test_density(self):
        m1=Material([(Element(self.db.db, 'Ni'), 1.0)], dens=8.9)
        m2=Material([(Element(self.db.db, 'Fe'), 2.0),
                     (Element(self.db.db, 'O'), 3.0)], dens=5.24)
        self.assertAlmostEqual(m1.dens, 8.9)
        self.assertAlmostEqual(m2.dens, 5.24)

    def test_volume(self):
        m1=Material([(Element(self.db.db, 'Ni'), 1.0)], fu_volume=10.950864)
        m2=Material([(Element(self.db.db, 'Fe'), 2.0),
                     (Element(self.db.db, 'O'), 3.0)], fu_volume=50.604676)
        self.assertAlmostEqual(m1.dens, 8.9, places=6)
        self.assertAlmostEqual(m2.dens, 5.24, places=6)

    def test_rho_n(self):
        m1=Material([(Element(self.db.db, 'Ni'), 1.0)], rho_n=9.4057e-06-1.1402e-09j)
        m2=Material([(Element(self.db.db, 'Fe'), 2.0),
                     (Element(self.db.db, 'O'), 3.0)], rho_n=7.1762e-06-2.8139e-10j)
        self.assertAlmostEqual(m1.dens, 8.9, places=4)
        self.assertAlmostEqual(m2.dens, 5.24, places=4)

    def test_rho_x(self):
        m1=Material([(Element(self.db.db, 'Ni'), 1.0)], xsld=7.2969e-05-2.8945e-06j, xE=Mo_kalpha)
        m2=Material([(Element(self.db.db, 'Fe'), 2.0),
                     (Element(self.db.db, 'O'), 3.0)], xsld=4.1136e-05-3.6296e-06j, xE=Cu_kalpha)
        self.assertAlmostEqual(m1.dens, 8.9, places=3)
        self.assertAlmostEqual(m2.dens, 5.24, places=3)

    def test_fail(self):
        with self.assertRaises(ValueError):
            m1=Material([(Element(self.db.db, 'Ni'), 1.0)])

    def test_neutron_ni(self):
        m1=Material([(Element(self.db.db, 'Ni'), 1.0)], dens=8.9)

        # compare with value from sld-calculator.appspot.com
        self.assertAlmostEqual(m1.rho_n.real, 9.4057e-06)
        self.assertAlmostEqual(m1.rho_n.imag, -1.1402e-09)

    def test_neutron_d2o(self):
        m1=Material([(Element(self.db.db, 'D'), 2.0),
                     (Element(self.db.db, 'O'), 1.0)], dens=1.11)
        m2=Material([(Element(self.db.db, 'H[2]'), 2.0),
                     (Element(self.db.db, 'O'), 1.0)], dens=1.11)

        # compare with value from sld-calculator.appspot.com
        self.assertAlmostEqual(m1.rho_n.real, 6.3927e-06)
        self.assertAlmostEqual(m1.rho_n.imag, -1.1398e-13)
        self.assertEqual(m1.rho_n, m2.rho_n)

    def test_neutron_fe2o3(self):
        m2=Material([(Element(self.db.db, 'Fe'), 2.0),
                     (Element(self.db.db, 'O'), 3.0)], dens=5.24)

        # compare with value from sld-calculator.appspot.com
        self.assertAlmostEqual(m2.rho_n.real, 7.1762e-06)
        self.assertAlmostEqual(m2.rho_n.imag, -2.8139e-10)

    def test_xray_kalpha(self):
        m2=Material([(Element(self.db.db, 'Fe'), 2.0),
                     (Element(self.db.db, 'O'), 3.0)], dens=5.24)

        with self.subTest('Cu', i=0):
            sld=m2.delta_of_E(Cu_kalpha)
            self.assertAlmostEqual(sld.real,  4.1125e-05)
            self.assertAlmostEqual(sld.imag, -3.6347e-06)
        with self.subTest('Mo', i=1):
            sld=m2.delta_of_E(Mo_kalpha)
            self.assertAlmostEqual(sld.real,  4.274e-05)
            self.assertAlmostEqual(sld.imag, -9.5604e-07)

    def test_xray_all(self):
        m2=Material([(Element(self.db.db, 'Fe'), 2.0),
                     (Element(self.db.db, 'O'), 3.0)], dens=5.24)
        E,delta=m2.delta_vs_E()

    def test_magnetic(self):
        m2=Material([(Element(self.db.db, 'Fe'), 2.0),
                     (Element(self.db.db, 'O'), 3.0)], dens=5.24, mu=3.5)
        #self.assertAlmostEqual(m2.rho_m, 0.) TODO: Fix the conversions in Material
        #self.assertAlmostEqual(m2.M, 0.)
        m2.rho_m
        m2.M

    def test_string_conversion(self):
        m2=Material([(Element(self.db.db, 'Mo'), 1.0),
                     (Element(self.db.db, 'Fe'), 2.0),
                     (Element(self.db.db, 'O'), 3.2)], dens=5.24)
        str(m2)
        repr(m2)

    def test_missing_data(self):
        with self.assertRaises(ValueError):
            Element(self.db.db)
        e=Element(self.db.db, 'Mo')
        self.assertEqual(e.f_of_E(1e10), 0.+0j)

    def test_element_properties(self):
        e=Element(self.db.db, 'Mo')
        self.assertEqual(e.E.shape, e.f.shape)
        self.assertEqual(e.E.shape, e.fp.shape)
        self.assertEqual(e.E.shape, e.fpp.shape)

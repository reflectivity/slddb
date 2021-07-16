import unittest
from numpy.testing import assert_array_equal
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
        with self.assertRaises(ValueError):
            Material([(Element(self.db.db, 'Ni'), 1.0)], dens=5.0, fu_dens=1.04)

    def test_volume(self):
        m1=Material([(Element(self.db.db, 'Ni'), 1.0)], fu_volume=10.950864)
        m2=Material([(Element(self.db.db, 'Fe'), 2.0),
                     (Element(self.db.db, 'O'), 3.0)], fu_volume=50.604676)
        m3=Material([(Element(self.db.db, 'Ni'), 1.0)], fu_dens=1./10.950864)
        self.assertAlmostEqual(m1.dens, 8.9, places=6)
        self.assertAlmostEqual(m2.dens, 5.24, places=6)
        self.assertAlmostEqual(m1.dens, m3.dens, places=6)
        self.assertAlmostEqual(m1.fu_volume, 10.950864, places=10)
        self.assertAlmostEqual(m2.fu_volume, 50.604676, places=10)
        self.assertAlmostEqual(m3.fu_volume, 10.950864, places=10)
        with self.assertRaises(ValueError):
            Material([(Element(self.db.db, 'Ni'), 1.0)], dens=5.0, fu_volume=10.950864)

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

    def test_formula(self):
        m1=Material([(Element(self.db.db, 'Ni'), 1.0)], xsld=7.2969e-05-2.8945e-06j, xE=Mo_kalpha)
        self.assertAlmostEqual(str(m1.formula), 'Ni')

    def test_fail(self):
        with self.assertRaises(ValueError):
            m1=Material([(Element(self.db.db, 'Ni'), 1.0)])
        m2=Material([(Element(self.db.db, 'Pu'), 1.0)], dens=20.0)
        m3=Material([(Element(self.db.db, 'Po'), 1.0)], dens=20.0)

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

        # compare calculated values with known parameters from external sources
        with self.subTest('Cu', i=0):
            sld=m2.rho_of_E(Cu_kalpha)
            # sld-calculator.appspot.com: 4.1125e-05  	-3.6347e-06
            self.assertAlmostEqual(sld.real,  4.1125e-05)
            self.assertAlmostEqual(sld.imag, -3.6347e-06)
            # Henke: 8047.82959 eV  delta=1.55382077E-05  beta=1.37184929E-06
            self.assertAlmostEqual(m2.delta_of_E(Cu_kalpha), 1.55382E-05, places=5)
            self.assertAlmostEqual(m2.beta_of_E(Cu_kalpha),  1.37185E-06, places=5)
            # Henke: 8047.83 eV  mu=8.93664 µm
            self.assertAlmostEqual(m2.mu_of_E(Cu_kalpha), 1./8.93664e4, places=5)
        with self.subTest('Mo', i=1):
            sld=m2.rho_of_E(Mo_kalpha)
            # sld-calculator.appspot.com: 4.274e-05  	-9.5604e-07
            self.assertAlmostEqual(sld.real,  4.274e-05)
            self.assertAlmostEqual(sld.imag, -9.5604e-07)
            # Henke: 17479.4004 eV  delta=3.4223483E-06  beta=7.66335759E-08
            self.assertAlmostEqual(m2.delta_of_E(Mo_kalpha), 3.4223483E-06, places=5)
            self.assertAlmostEqual(m2.beta_of_E(Mo_kalpha), 7.66335759E-08, places=5)
            # Henke: 17479.4 eV  mu=73.6570 µm
            self.assertAlmostEqual(m2.mu_of_E(Mo_kalpha), 1./73.6570e4, places=5)

    def test_xray_all(self):
        m2=Material([(Element(self.db.db, 'Fe'), 2.0),
                     (Element(self.db.db, 'O'), 3.0)], dens=5.24)
        E1,rho=m2.rho_vs_E()
        E2,delta=m2.delta_vs_E()
        E3,beta=m2.beta_vs_E()
        E4,mu=m2.mu_vs_E()
        assert_array_equal(E1, E2)
        assert_array_equal(E1, E3)
        assert_array_equal(E1, E4)

    def test_magnetic(self):
        m0=Material([(Element(self.db.db, 'Fe'), 2.0),
                     (Element(self.db.db, 'O'), 3.0)], dens=5.24)
        m1=Material([(Element(self.db.db, 'Fe'), 2.0),
                     (Element(self.db.db, 'O'), 3.0)], dens=5.24, mu=3.5)
        m2=Material([(Element(self.db.db, 'Fe'), 2.0),
                     (Element(self.db.db, 'O'), 3.0)], dens=5.24, M=m1.M)
        self.assertEqual(m0.rho_m, 0.)
        self.assertEqual(m0.M, 0.)
        self.assertAlmostEqual(m1.mu, m2.mu)
        self.assertAlmostEqual(m1.rho_m, m2.rho_m)
        self.assertAlmostEqual(m1.M, m2.M)
        with self.assertRaises(ValueError):
            Material([(Element(self.db.db, 'Fe'), 2.0),
                     (Element(self.db.db, 'O'), 3.0)], dens=5.24, mu=m1.mu, M=m1.M)

    def test_string_conversion(self):
        m2=Material([(Element(self.db.db, 'Mo'), 1.0),
                     (Element(self.db.db, 'Fe'), 2.0),
                     (Element(self.db.db, 'O'), 3.2)], dens=5.24, ID=13)
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

    def test_element_strings(self):
        e=Element(self.db.db, 'H')
        str(e)
        repr(e)
        e=Element(self.db.db, 'H[2]')
        str(e)
        repr(e)

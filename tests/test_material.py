import unittest
from numpy.testing import assert_array_equal
from slddb.material import Material
from slddb.element_table import Element, element
from slddb.constants import Cu_kalpha, Mo_kalpha, Cu_kalpha1, Mo_kalpha1

# reference data uses Henke tables
from slddb.element_table.xray_henke import XRAY_SCATTERING_FACTORS
element.XRAY_SCATTERING_FACTORS = XRAY_SCATTERING_FACTORS
# calculated using NIST calculator at https://www.ncnr.nist.gov/resources/activation/
REFERENCE_RESULTS = {
    # compound: [neutron, xray Cu, xray Mo]
    'Ni': [9.406e-6-0.001e-6j, 64.390e-6-1.351e-6j, 72.969e-6-2.894e-6j], # dens=8.9
    'Fe2O3': [7.176e-6-0j, 41.125e-6-3.635e-6j, 42.740e-6-0.956e-6j], # dens=5.24
    'D2O': [6.393e-6-0j, 9.455e-6-0.032e-6j, 9.416e-6-0.006e-6j], # dens=1.11
    }

class TestMaterial(unittest.TestCase):
    def test_density(self):
        m1=Material([(Element('Ni'), 1.0)], dens=8.9)
        m2=Material([(Element('Fe'), 2.0),
                     (Element('O'), 3.0)], dens=5.24)
        self.assertAlmostEqual(m1.dens, 8.9)
        self.assertAlmostEqual(m2.dens, 5.24)
        with self.assertRaises(ValueError):
            Material([(Element( 'Ni'), 1.0)], dens=5.0, fu_dens=1.04)

    def test_volume(self):
        m1=Material([(Element( 'Ni'), 1.0)], fu_volume=10.950863331638253)
        m2=Material([(Element( 'Fe'), 2.0),
                     (Element( 'O'), 3.0)], fu_volume=50.60467453722025)
        m3=Material([(Element( 'Ni'), 1.0)], fu_dens=1./10.950863331638253)
        self.assertAlmostEqual(m1.dens, 8.9, places=6)
        self.assertAlmostEqual(m2.dens, 5.24, places=6)
        self.assertAlmostEqual(m1.dens, m3.dens, places=6)
        self.assertAlmostEqual(m1.fu_volume, 10.950863331638253, places=10)
        self.assertAlmostEqual(m2.fu_volume, 50.60467453722025, places=10)
        self.assertAlmostEqual(m3.fu_volume, 10.950863331638253, places=10)
        with self.assertRaises(ValueError):
            Material([(Element( 'Ni'), 1.0)], dens=5.0, fu_volume=10.950864)

    def test_rho_n(self):
        m1=Material([(Element( 'Ni'), 1.0)], rho_n=REFERENCE_RESULTS['Ni'][0])
        m2=Material([(Element( 'Fe'), 2.0),
                     (Element( 'O'), 3.0)], rho_n=REFERENCE_RESULTS['Fe2O3'][0])
        self.assertAlmostEqual(m1.dens, 8.9, places=3)
        self.assertAlmostEqual(m2.dens, 5.24, places=3)

    def test_rho_x(self):
        m1=Material([(Element( 'Ni'), 1.0)], xsld=REFERENCE_RESULTS['Ni'][2], xE=Mo_kalpha)
        m2=Material([(Element( 'Fe'), 2.0),
                     (Element( 'O'), 3.0)], xsld=REFERENCE_RESULTS['Fe2O3'][1], xE=Cu_kalpha)
        self.assertAlmostEqual(m1.dens, 8.9, places=3)
        self.assertAlmostEqual(m2.dens, 5.24, places=3)

    def test_formula(self):
        m1=Material([(Element( 'Ni'), 1.0)], xsld=REFERENCE_RESULTS['Ni'][2], xE=Mo_kalpha)
        self.assertAlmostEqual(str(m1.formula), 'Ni')

    def test_fail(self):
        with self.assertRaises(ValueError):
            m1=Material([(Element('Ni'), 1.0)])
        with self.assertRaises(ValueError):
            m2=Material([(Element('Pu'), 1.0)], dens=20.0)
        with self.assertRaises(ValueError):
            m3=Material([(Element('Po'), 1.0)], dens=20.0)

    def test_neutron_ni(self):
        m1=Material([(Element( 'Ni'), 1.0)], dens=8.9)

        # compare with value from NIST
        self.assertAlmostEqual(m1.rho_n.real, REFERENCE_RESULTS['Ni'][0].real)
        self.assertAlmostEqual(m1.rho_n.imag, REFERENCE_RESULTS['Ni'][0].imag)

    def test_neutron_d2o(self):
        m1=Material([(Element( 'D'), 2.0),
                     (Element( 'O'), 1.0)], dens=1.11)
        m2=Material([(Element( 'H[2]'), 2.0),
                     (Element( 'O'), 1.0)], dens=1.11)

        # compare with value from NIST
        self.assertAlmostEqual(m1.rho_n.real, REFERENCE_RESULTS['D2O'][0].real)
        self.assertAlmostEqual(m1.rho_n.imag, REFERENCE_RESULTS['D2O'][0].imag)
        self.assertEqual(m1.rho_n, m2.rho_n)

    def test_neutron_fe2o3(self):
        m2=Material([(Element( 'Fe'), 2.0),
                     (Element( 'O'), 3.0)], dens=5.24)

        # compare with value from NIST
        self.assertAlmostEqual(m2.rho_n.real, REFERENCE_RESULTS['Fe2O3'][0].real)
        self.assertAlmostEqual(m2.rho_n.imag, REFERENCE_RESULTS['Fe2O3'][0].imag)

    def test_xray_kalpha(self):
        m2=Material([(Element( 'Fe'), 2.0),
                     (Element( 'O'), 3.0)], dens=5.24)

        # compare calculated values with known parameters from external sources
        with self.subTest('Cu', i=0):
            sld=m2.rho_of_E(Cu_kalpha)
            # sld-calculator.appspot.com: 4.1125e-05  	-3.6347e-06
            self.assertAlmostEqual(sld.real,  4.1125e-05)
            self.assertAlmostEqual(sld.imag, -3.6347e-06)
            # Henke: 8047.82959 eV  delta=1.55382077E-05  beta=1.37184929E-06
            self.assertAlmostEqual(m2.delta_of_E(Cu_kalpha1), 1.55382E-05, places=5)
            self.assertAlmostEqual(m2.beta_of_E(Cu_kalpha1),  1.37185E-06, places=5)
            # Henke: 8047.83 eV  mu=8.93664 µm
            self.assertAlmostEqual(m2.mu_of_E(Cu_kalpha1), 1./8.93664e4, places=5)
        with self.subTest('Mo', i=1):
            sld=m2.rho_of_E(Mo_kalpha)
            # sld-calculator.appspot.com: 4.274e-05  	-9.5604e-07
            self.assertAlmostEqual(sld.real,  4.274e-05)
            self.assertAlmostEqual(sld.imag, -9.5604e-07)
            # Henke: 17479.4004 eV  delta=3.4223483E-06  beta=7.66335759E-08
            self.assertAlmostEqual(m2.delta_of_E(Mo_kalpha1), 3.4223483E-06, places=5)
            self.assertAlmostEqual(m2.beta_of_E(Mo_kalpha1), 7.66335759E-08, places=5)
            # Henke: 17479.4 eV  mu=73.6570 µm
            self.assertAlmostEqual(m2.mu_of_E(Mo_kalpha1), 1./73.6570e4, places=5)

    def test_xray_all(self):
        m2=Material([(Element( 'Fe'), 2.0),
                     (Element( 'O'), 3.0)], dens=5.24)
        E1,rho=m2.rho_vs_E()
        E2,delta=m2.delta_vs_E()
        E3,beta=m2.beta_vs_E()
        E4,mu=m2.mu_vs_E()
        assert_array_equal(E1, E2)
        assert_array_equal(E1, E3)
        assert_array_equal(E1, E4)

    def test_magnetic(self):
        m0=Material([(Element( 'Fe'), 2.0),
                     (Element( 'O'), 3.0)], dens=5.24)
        m1=Material([(Element( 'Fe'), 2.0),
                     (Element( 'O'), 3.0)], dens=5.24, mu=3.5)
        m2=Material([(Element( 'Fe'), 2.0),
                     (Element( 'O'), 3.0)], dens=5.24, M=m1.M)
        self.assertEqual(m0.rho_m, 0.)
        self.assertEqual(m0.M, 0.)
        self.assertAlmostEqual(m1.mu, m2.mu)
        self.assertAlmostEqual(m1.rho_m, m2.rho_m)
        self.assertAlmostEqual(m1.M, m2.M)
        with self.assertRaises(ValueError):
            Material([(Element( 'Fe'), 2.0),
                     (Element( 'O'), 3.0)], dens=5.24, mu=m1.mu, M=m1.M)

    def test_string_conversion(self):
        m2=Material([(Element( 'Mo'), 1.0),
                     (Element( 'Fe'), 2.0),
                     (Element( 'O'), 3.2)], dens=5.24, ID=13)
        str(m2)
        repr(m2)

    def test_missing_data(self):
        with self.assertRaises(ValueError):
            Element()
        e=Element( 'Mo')
        self.assertEqual(e.f_of_E(1e10), 0.+0j)

    def test_element_properties(self):
        e=Element( 'Mo')
        self.assertEqual(e.E.shape, e.f.shape)
        self.assertEqual(e.E.shape, e.fp.shape)
        self.assertEqual(e.E.shape, e.fpp.shape)

    def test_element_strings(self):
        e=Element( 'H')
        str(e)
        repr(e)
        e=Element( 'H[2]')
        str(e)
        repr(e)

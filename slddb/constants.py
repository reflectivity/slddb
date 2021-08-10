"""
Physical constants and conversion factors used in the package.

The values given here have been taken from the
CODATA Internationally recommended 2018 values of the Fundamental Physical Constants
provided at https://physics.nist.gov/cuu/Constants/index.html
"""

u2g=1.660_539_066_60e-24 # 1/N_Avogadro (g/mol => g/atom)
h_eVs=4.135_667_696e-15 # eV·s Planck's constant
c_ms=299_792_458.0 # m/s speed of light
# some conversion constants used
kilo=1e3
m2angstrom=1e10
fm2angstrom=1e-5

r_e=2.817_940_3262 # fm - classical electron radius
r_e_angstrom=fm2angstrom*r_e # Å - classical electron radius
sigma_to_b=2.780_867_6e-4 # fm/barn absorption at 1.798Å (sigma=4*pi*b/k)
E_to_lambda=h_eVs/kilo*c_ms*m2angstrom # keV·Å conversion x-ray energy to wavelength (h*c)

muB=9.274_010_0783e3 # kA/m Å³ - Bohr Magneton scaled to get kA/m from Ä³ FU volume

#
# Non-fundamental constant derived values with yet undocumented origin
#
Cu_kalpha=8.047823 # keV
Mo_kalpha=17.4794 # keV

rho_of_M=2.853e-9 # Å^-2 from kA/m

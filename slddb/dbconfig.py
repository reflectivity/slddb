"""
Configure the database file as well as parameters for DB tables used.
"""

import os

if 'APPDATA' in os.environ:
    confighome = os.environ['APPDATA']
elif 'XDG_CONFIG_HOME' in os.environ:
    confighome = os.environ['XDG_CONFIG_HOME']
else:
    confighome = os.path.join(os.environ['HOME'], '.config')
configpath = os.path.join(confighome, 'slddb')
if not os.path.exists(configpath):
    os.makedirs(configpath)

from .converters import CType, CLimited, CArray, CDate, CComplex, CFormula, CSelect, CMultiSelect, \
    CUrl, CMail, Cdoi, Ccas

cstr=CType(str, str)
cint=CType(int, int)
pint=CType(int, int, 'integer primary key')
cfloat=CType(float, float)
cposfloat=CLimited(float, float, 1e-30)
cdate=CDate()
cformula=CFormula()
ccomplex=CComplex()
carray=CArray()
curl=CUrl()
cmail=CMail()

WEBAPI_URL='https://slddb.esss.dk/slddb/'
DB_FILE=os.path.join(configpath, 'local_database.db')

DB_MATERIALS_NAME='materials'
DB_MATERIALS_COLUMNS=[
   #(Name,           converter, default, unit)
    ('ID',           pint,      None,    None),
    ('created',      cdate,     'CURRENT_TIMESTAMP',    None),
    ('created_by',   cmail,     None,    None),
    ('updated',      cdate,     None,    None),
    ('validated',    cdate,     None,    None),
    ('validated_by', cstr,      None,    None),
    ('accessed',     cint,      0,       None),
    ('selected',     cint,      0,       None),
    ('name',         cstr,      None,    '*'),
    ('description',  cstr,      None,    None),
    ('formula',      cformula,  None,    '*'),
    ('HR_fomula',    cstr,      None,    None),
    ('density',      cposfloat, None, 'g/cm³ **'),
    ('FU_volume',    cposfloat, None,    'Å³ **'),
    ('SLD_n',        ccomplex,  None,   'Å⁻² **'),
    ('SLD_x',        ccomplex,  None, 'r_e/Å⁻³ **'),
    ('E_x',          cfloat,    None,   'keV'),
    ('mu',           cfloat,    0.0,  'µB/FU'),
    ('physical_state', CSelect(['solid', 'liquid', 'gas', 'solution',
                                'micellar aggregate', 'assembled monolayer/bilayer',
                                'nanoparticle']), 'solid',    None),
    ('tags', CMultiSelect(['magnetic', 'polymer', 'biology', 'membrane', 'lipid',
                           'metal', 'metal alloy', 'inorganic', 'small organic',
                           'surfactant', 'lipid', 'protein']), None,    None),
    ('ref_website',  curl,      None,    None),
    ('reference',    cstr,      None,    None),
    ('doi',          Cdoi(),    None,    None),
    ('purity',       cstr,      None,    None),
    ('CAS_No',       Ccas(),    None,    None),
    ('crystal_data', cstr,      None,    None),
    ('temperature',  cposfloat, None,     'K'),
    ('magnetic_field', cfloat,  None,     'T'),
    ('data_origin',  CSelect(['unspecified', 'text book',
                              'x-ray reflectivity', 'neutron reflectivity',
                              'mass density', 'diffraction', 'interferometry',
                              'SANS', 'SAXS', 'molecular dynamics']), 'unspecified',    None),
    ('comments',     cstr,      None,    None),
    ('invalid',      cdate,     None,    None),
    ('invalid_by',   cstr,      None,    None),
    ]
DB_MATERIALS_FIELDS=[fi[0] for fi in DB_MATERIALS_COLUMNS]
DB_MATERIALS_CONVERTERS=[fi[1] for fi in DB_MATERIALS_COLUMNS]
DB_MATERIALS_FIELD_DEFAULTS=[fi[2] for fi in DB_MATERIALS_COLUMNS]
DB_MATERIALS_FIELD_UNITS=[fi[3] for fi in DB_MATERIALS_COLUMNS]
DB_MATERIALS_HIDDEN_DATA=    ['created', 'created_by', 'updated',
                              'validated', 'validated_by', 'accessed', 'selected',
                              'invalid', 'invalid_by']
db_lookup=dict([(field, (i, converter, default, unit))
                for i, (field, converter, default, unit) in
                enumerate(zip(DB_MATERIALS_FIELDS,
                              DB_MATERIALS_CONVERTERS,
                              DB_MATERIALS_FIELD_DEFAULTS,
                              DB_MATERIALS_FIELD_UNITS))])

# stores all chemical elements together with their stable isotopes and
# an index to the scattering length data row index
DB_ELEMENTS_NAME='elements'
DB_ELEMENTS_FIELDS=    ['Z',  'Symbol', 'Name', 'Weight', 'Isotopes',
                        'n_scat', 'x_scat']
DB_ELEMENTS_CONVERTERS=[pint, cstr,     cstr,   cposfloat,   cstr,
                        cint,     cint]

# for neutrons store isotope specific data similar to elements
DB_ISOTOPES_NAME='isotopes'
DB_ISOTOPES_FIELDS=    ['ID', 'Z',  'N',  'Weight',  'n_scat']
DB_ISOTOPES_CONVERTERS=[pint, cint, cint, cposfloat,    cint]

# stores scattering data (neutron and x-ray) for the elements/isotopes
DB_SLDATA_NAME='scattering_data'
DB_SLDATA_FIELDS=    ['ID', 'data']
DB_SLDATA_CONVERTERS=[pint, carray]

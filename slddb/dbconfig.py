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

from .converters import CType, CLimited, CArray, CDate, CComplex, CFormula, CSelect, CMultiSelect, CUrl, CMail

cstr=CType(str, str)
cint=CType(int, int)
pint=CType(int, int, 'integer primary key')
cfloat=CType(float, float)
cposfloat=CLimited(float, float, 0.0)
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
   #(Name,           converter, default)
    ('ID',           pint,      None),
    ('created',      cdate,     'CURRENT_TIMESTAMP'),
    ('created_by',   cmail,     None),
    ('updated',      cdate,     None),
    ('validated',    cdate,     None),
    ('validated_by', cstr,      None),
    ('accessed',     cint,      0),
    ('selected',     cint,      0),
    ('name',         cstr,      None),
    ('description',  cstr,      None),
    ('formula',      cformula,  None),
    ('HR_fomula',    cstr,      None),
    ('density',      cposfloat, None),
    ('FU_volume',    cposfloat, None),
    ('SLD_n',        ccomplex,  None),
    ('SLD_x',        ccomplex,  None),
    ('E_x',          cfloat,    None),
    ('mu',           cfloat,    0.0),
    ('physical_state', CSelect(['solid', 'liquid', 'gas', 'solution',
                                'micellar aggregate', 'assembled monolayer/bilayer',
                                'nanoparticle']), 'solid'),
    ('tags', CMultiSelect(['magnetic', 'polymer', 'biology', 'membrane', 'lipid',
                           'metal', 'metal alloy', 'inorganic', 'small organic',
                           'surfactant', 'lipid', 'synthetic polymer', 'proteins']), None),
    ('ref_website',  curl,      None),
    ('reference',    cstr,      None),
    ('doi',          cstr,      None),
    ('purity',       cstr,      None),
    ('CAS_No',       cstr,      None),
    ('crystal_data', cstr,      None),
    ('temperature',  cposfloat, None),
    ('data_origin',  CSelect(['unspecified', 'text book',
                              'x-ray reflectivity', 'neutron reflectivity',
                              'mass density', 'diffraction', 'interferometry',
                              'SANS', 'SAXS', ]), 'unspecified'),
    ('comments',     cstr,      None),
    ('invalid',      cdate,     None),
    ('invalid_by',   cstr,      None),
    ]
DB_MATERIALS_FIELDS=[fi[0] for fi in DB_MATERIALS_COLUMNS]
DB_MATERIALS_CONVERTERS=[fi[1] for fi in DB_MATERIALS_COLUMNS]
DB_MATERIALS_FIELD_DEFAULTS=[fi[2] for fi in DB_MATERIALS_COLUMNS]
DB_MATERIALS_HIDDEN_DATA=    ['created', 'created_by', 'updated',
                              'validated', 'validated_by', 'accessed', 'selected',
                              'invalid', 'invalid_by']
db_lookup=dict([(field, (i, converter, default))
                for i, (field, converter, default) in
                enumerate(zip(DB_MATERIALS_FIELDS,
                              DB_MATERIALS_CONVERTERS,
                              DB_MATERIALS_FIELD_DEFAULTS))])

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

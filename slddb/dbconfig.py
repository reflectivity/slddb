"""
Configure the database file as well as parameters for DB tables used.
"""

from .converters import CType, CLimited, CArray, CDate, CComplex, CFormula

cstr=CType(str, str)
cint=CType(int, int)
pint=CType(int, int, 'integer primary key')
cfloat=CType(float, float)
cposfloat=CLimited(float, float, 0.0)
cdate=CDate()
cformula=CFormula()
ccomplex=CComplex()
carray=CArray()


DB_FILE='slddb.db'

DB_MATERIALS_NAME='materials'
DB_MATERIALS_FIELDS=         ['ID', 'created', 'updated', 'accessed', 'selected',
                              'name', 'description', 'formula', 'HR_fomula',
                              'density', 'FU_volume', 'SLD_n', 'SLD_x', 'E_x' ]
DB_MATERIALS_CONVERTERS=     [pint, cdate,         cdate, cint,       cint,
                              cstr,   cstr,          cformula,      cstr,
                              cposfloat, cposfloat, ccomplex, ccomplex, cfloat]
DB_MATERIALS_FIELD_DEFAULTS= [None, 'CURRENT_TIMESTAMP',       None, 0,     0,
                              None,     None,   None, None,
                              None, None, None, None, None]
DB_MATERIALS_HIDDEN_DATA=    []#'created', 'updated', 'accessed', 'selected']
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

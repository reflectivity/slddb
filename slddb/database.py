"""
Manage database creation, insertion and access.
"""

import sqlite3
from .dbconfig import DB_MATERIALS_CONVERTERS, DB_MATERIALS_NAME, \
    DB_MATERIALS_FIELDS, DB_MATERIALS_FIELD_DEFAULTS, db_lookup
from .element_table import Elements
from .material import Material, Formula

class SLDDB():
    """
    Database to store material parameters to calculate
    scattering length densities (SLDs) for neutron
    and x-ray scattering.
    """

    def __init__(self, dbfile):
        self.db=sqlite3.connect(dbfile)
        self.elements=Elements(self.db)

    def add_material(self, name, formula, commit=True, **data):
        din={}
        for key, value in data.items():
            if not key in DB_MATERIALS_FIELDS:
                raise KeyError('%s is not a valid data field'%key)
            din[key]=db_lookup[key][1].convert(value)

        if not ('density' in din or 'FU volume' in din
                or 'SLD_n' in din or ('SLD_x' in din and 'E_x' in din)):
            raise ValueError("Not enough information to determine density")

        din['name']=db_lookup['name'][1].convert(name)
        din['formula']=db_lookup['formula'][1].convert(formula)

        c=self.db.cursor()
        qstr="INSERT INTO %s (%s) VALUES (%s)"%(
            DB_MATERIALS_NAME, ", ".join(din.keys()),
            ', '.join(["?" for key in din.keys()]))
        c.execute(qstr, tuple(din.values()))
        c.close()
        if commit:
            self.db.commit()

    def search_material(self, join_and=True, **data):
        for key, value in data.items():
            if not key in DB_MATERIALS_FIELDS:
                raise KeyError('%s is not a valid data field'%key)

        if len(data)==0:
            sstr='SELECT * FROM %s'%DB_MATERIALS_NAME
            qstr=''
            qlst=[]
            ustr=''
        else:
            sstr='SELECT * FROM %s WHERE '%DB_MATERIALS_NAME
            ustr='UPDATE %s SET accessed = accessed + 1 WHERE '%DB_MATERIALS_NAME
            qstr=''
            qlst=[]
            for key, value in data.items():
                cval=db_lookup[key][1].convert(value)
                if type(cval) is str:
                    qstr+='%s LIKE ?'%key
                    cval='%%%s%%'%cval
                else:
                    qstr+='%s == ?'%key
                qlst.append(cval)

                if join_and:
                    qstr+=' AND '
                else:
                    qstr+='  OR '
            qstr=qstr[:-5]
        c=self.db.cursor()
        c.execute(sstr+qstr+' ORDER BY accessed DESC', qlst)
        results=c.fetchall()
        keys=[key for key, *ignore in c.description]
        # update access counter
        c.execute(ustr+qstr, qlst)
        c.close()
        self.db.commit()

        # convert values
        output=[]
        for row in results:
            rowdict={key: db_lookup[key][1].revert(value) for key,value in zip(keys, row)}
            output.append(rowdict)
        return output

    def select_material(self, result):
        # generate Material object from database entry and increment selection counter
        formula=Formula(result['formula'])
        m=Material([(self.elements.get_element(element), amount) for element, amount in formula],
                   dens=result['density'],
                   fu_volume=result['FU_volume'],
                   rho_n=result['SLD_n'],
                   xsld=result['SLD_x'], xE=result['E_x'])

        ustr='UPDATE %s SET selected = selected + 1 WHERE ID == ?'%DB_MATERIALS_NAME
        c=self.db.cursor()
        c.execute(ustr, (result['ID'],))
        c.close()
        self.db.commit()
        return m

    def create_table(self):
        c=self.db.cursor()
        name_type=['%s %s %s'%(fi, ci.sql_type, (di is not None) and "DEFAULT %s"%di or "")
                   for fi, ci, di in zip(DB_MATERIALS_FIELDS, DB_MATERIALS_CONVERTERS,
                                     DB_MATERIALS_FIELD_DEFAULTS)]
        qstr='CREATE TABLE %s (%s)'%(DB_MATERIALS_NAME, ", ".join(name_type))
        c.execute(qstr)
        c.close()
        self.db.commit()

    def create_database(self):
        self.create_table()
        self.elements.create_table()
        self.elements.fill_table()
        self.db.commit()

    def add_elements(self):
        import periodictable

        for element in periodictable.elements:
            if element is periodictable.n or element.density is None:
                continue
            self.add_material(element.name.capitalize(),
                              element.symbol,
                              commit=False,
                              description=element.density_caveat,
                              density=element.density)
        self.db.commit()

    def __del__(self):
        self.db.close()
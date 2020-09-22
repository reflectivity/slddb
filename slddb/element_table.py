"""
Generate and query database table for chemical elements.
"""
from numpy import array
from .dbconfig import DB_ELEMENTS_CONVERTERS, DB_ELEMENTS_FIELDS, \
    DB_ELEMENTS_NAME, DB_ISOTOPES_CONVERTERS, DB_ISOTOPES_FIELDS, \
    DB_ISOTOPES_NAME, DB_SLDATA_CONVERTERS, DB_SLDATA_FIELDS, DB_SLDATA_NAME
from .constants import sigma_to_b

class Element():
    def __init__(self, db, symbol=None, Z=None):
        # get element from database
        N=None
        if Z is None and symbol is None:
            raise ValueError("Provide either Symbol or Z")
        elif Z is None:
            self.symbol=symbol
            if symbol == 'D':
                symb, N='H', 2
            elif '[' in symbol:
                symb, N=symbol.rstrip(']').split('[', 1)
            else:
                symb=symbol
            c=db.cursor()
            c.execute("SELECT %s FROM %s WHERE %s = ?"%(
                ', '.join(DB_ELEMENTS_FIELDS),
                DB_ELEMENTS_NAME,
                DB_ELEMENTS_FIELDS[1]), (symb,))
            qres=c.fetchone()
            self.Z=DB_ELEMENTS_CONVERTERS[0].revert(qres[0])
        else:
            self.Z=Z
            c=db.cursor()
            c.execute("SELECT %s FROM %s WHERE %s = ?"%(
                ', '.join(DB_ELEMENTS_FIELDS),
                DB_ELEMENTS_NAME,
                DB_ELEMENTS_FIELDS[0]), (Z,))
            qres=c.fetchone()
            self.symbol=DB_ELEMENTS_CONVERTERS[1].revert(qres[1])

        self.name=qres[2]
        xid=qres[6]
        self._xdata=self.get_sldata(xid, c)

        if N is None:
            self.mass=qres[3]
            nid=qres[5]
            self.b=self.get_sldata(nid, c)[0]
        else:
            c.execute("SELECT %s FROM %s WHERE %s = ? AND %s = ?"%(
                ', '.join(DB_ISOTOPES_FIELDS),
                DB_ISOTOPES_NAME,
                DB_ISOTOPES_FIELDS[1],
                DB_ISOTOPES_FIELDS[2],), (self.Z,N))
            qres=c.fetchone()
            self.mass=qres[3]
            nid=qres[4]
            self.b=self.get_sldata(nid, c)[0]

    def get_sldata(self, id, c):
        c.execute("SELECT %s FROM %s WHERE %s = ?"%(DB_SLDATA_FIELDS[1],
                                                    DB_SLDATA_NAME,
                                                    DB_SLDATA_FIELDS[0]), (id,))
        res=c.fetchone()
        return DB_SLDATA_CONVERTERS[1].revert(res[0])

    def f_of_E(self, Ei):
        E, fp, fpp=self._xdata
        fltr=(E>=Ei)
        if not fltr.any():
            return 0.-0j
        else:
            return fp[fltr][0]-1j*fpp[fltr][0]

    @property
    def E(self):
        return self._xdata[0]

    @property
    def f(self):
        return self._xdata[1]-1j*self._xdata[2]

    @property
    def fp(self):
        return self._xdata[1]

    @property
    def fpp(self):
        return self._xdata[2]


class Elements():

    def __init__(self, database):
        self.db=database

    def get_element(self, value):
        if type(value) is int:
            return Element(self.db, Z=value)
        else:
            return Element(self.db, symbol=value)

    def create_table(self):
        self.create_table_for(DB_ELEMENTS_NAME,
                              DB_ELEMENTS_FIELDS, DB_ELEMENTS_CONVERTERS)
        self.create_table_for(DB_ISOTOPES_NAME,
                              DB_ISOTOPES_FIELDS, DB_ISOTOPES_CONVERTERS)
        self.create_table_for(DB_SLDATA_NAME,
                              DB_SLDATA_FIELDS, DB_SLDATA_CONVERTERS)


    def create_table_for(self, name, fields, converters):
        c=self.db.cursor()
        name_type=['%s %s'%(fi, ci.sql_type)
                   for fi, ci in zip(fields, converters)]
        qstr='CREATE TABLE %s (%s)'%(name, ", ".join(name_type))
        c.execute(qstr)
        c.close()

    def fill_table(self):
        # use periodictable module from NIST to gather information
        # not needed if database is provided to user
        import periodictable

        for element in periodictable.elements:
            if element is periodictable.n:
                continue

            Z=element.number  # charge
            mass=element.mass # u
            symbol=element.symbol
            name=element.name

            isotopes=[]
            for isotope in element.isotopes:
                abundance=element[isotope].abundance
                if abundance>0:
                    isotopes.append((Z, isotope, abundance))

            if element.neutron.b_c is not None:
                b=array([element.neutron.b_c-
                         1j*(element.neutron.absorption*sigma_to_b or 0.)])
                nid=self.add_sldata(b)
            else:
                nid=-1

            xdata=element.xray.sftable
            if xdata is not None:
                xid=self.add_sldata(xdata)
            else:
                xid=-1

            self.add_element(Z, symbol, name, mass, isotopes, nid, xid)
            self.add_isotopes(element, isotopes)

    def add_element(self, *pars):
        c=self.db.cursor()
        qstr='INSERT INTO %s (%s) VALUES (%s)'%(DB_ELEMENTS_NAME,
                                ', '.join(DB_ELEMENTS_FIELDS[:len(pars)]),
                                ('?, '*len(pars))[:-2])
        convs=DB_ELEMENTS_CONVERTERS
        data=[convs[i].convert(pi) for i, pi in enumerate(pars)]
        c.execute(qstr, data)
        c.close()

    def add_isotopes(self, element, isotopes):
        c=self.db.cursor()
        convs=DB_ISOTOPES_CONVERTERS[1:]
        qstr='INSERT INTO %s (%s) VALUES (?,?,?,?)'%(DB_ISOTOPES_NAME,
                                                     ', '.join(DB_ISOTOPES_FIELDS[1:]))

        for Z,N,abundance in isotopes:
            isotope=element[N]
            mass=isotope.mass
            b=array([(isotope.neutron.b_c or 0.)-
                     1j*(isotope.neutron.absorption*sigma_to_b or 0.)])
            nid=self.add_sldata(b)

            data=[convs[i].convert(pi) for i, pi
                  in enumerate([Z, N, mass, nid])]
            c.execute(qstr, data)
        c.close()


    def add_sldata(self, data):
        c=self.db.cursor()
        cdata=DB_SLDATA_CONVERTERS[1].convert(data)
        qstr='INSERT INTO %s (%s) VALUES (?)'%(DB_SLDATA_NAME,
                                               DB_SLDATA_FIELDS[1])
        c.execute(qstr, (cdata, ))
        c.close()
        return c.lastrowid


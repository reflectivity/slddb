"""
Class to hold information for one material and allow calculation
of x-ray and neutron SLDs for different applications.
"""

import re
from numpy import array
from collections import OrderedDict
from .constants import u2g, r_e, muB, rho_of_M

SUBSCRIPT_DIGITS="₀₁₂₃₄₅₆₇₈₉"

class Formula(list):
    """
    Evaluate strings for element chemical fomula.
    """
    elements=(r"A[cglmrstu]|B[aehikr]?|C[adeflmorsu]?|D[bsy]{0,1}|E[rsu]|F[emr]?|"
               "G[ade]|H[efgos]?|I[nr]?|Kr?|L[airu]|M[dgnot]|N[abdeiop]?|"
               "Os?|P[abdmortu]?|R[abefghnu]|S[bcegimnr]?|T[abcehilm]|"
               "Uu[bhopqst]|U|V|W|Xe|Yb?|Z[nr]")
    isotopes=(r"(A[cglmrstu]|B[aehikr]?|C[adeflmorsu]?|D[bsy]{0,1}|E[rsu]|F[emr]?|"
               "G[ade]|H[efgos]?|I[nr]?|Kr?|L[airu]|M[dgnot]|N[abdeiop]?|"
               "Os?|P[abdmortu]?|R[abefghnu]|S[bcegimnr]?|T[abcehilm]|"
               "Uu[bhopqst]|U|V|W|Xe|Yb?|Z[nr])"
               "\[[1-9][0-9]{0,2}\]")

    def __init__(self, string, sort=True):
        self._do_sort=sort
        self.HR_formula=string
        list.__init__(self, [])
        self.parse_string(string)
        self.merge_same()

    def parse_string(self, string):
        # remove gaps and ignored characters
        string=string.replace(' ', '').replace('\t', '').replace('\n','')
        string=string.replace('{', '').replace('}', '').replace('_','').replace('$','')

        # TODO: Implement groups of formulas like Fe(HO)3
        items=self.parse_group(string)
        self+=items

    def parse_group(self, group):
        out=[]
        mele=re.search(self.elements, group, flags=re.IGNORECASE)
        miso=re.search(self.isotopes, group, flags=re.IGNORECASE)
        if miso is not None and miso.start()==mele.start():
            prev=miso
        else:
            prev=mele
        if prev is None or prev.start()!=0:
            raise ValueError('Did not find any valid elemnt in string')
        pos=prev.end()
        while pos<len(group):
            mele=re.search(self.elements, group[pos:], flags=re.IGNORECASE)
            miso=re.search(self.isotopes, group[pos:], flags=re.IGNORECASE)
            if miso is not None and miso.start()==mele.start():
                next=miso
            else:
                next=mele
            if next is None:
                break
            if next.start()==0:
                out.append((prev.string[prev.start():prev.end()].capitalize(), 1.0))
            else:
                out.append((prev.string[prev.start():prev.end()].capitalize(),
                            float(group[pos:pos+next.start()])))
            prev=next
            pos+=next.end()
        if pos==len(group):
            out.append((prev.string[prev.start():].capitalize(), 1.0))
        else:
            out.append((prev.string[prev.start():prev.end()].capitalize(), float(group[pos:])))
        return out

    def merge_same(self):
        elements=OrderedDict({})
        for ele, amount in self:
            if ele in elements:
                elements[ele]+=amount
            else:
                elements[ele]=amount
        self[:]=[items for items in elements.items()]
        if self._do_sort:
            self.sort()

    def __str__(self):
        output=''
        for element, number in self:
            if number == 1.0:
                output+=element
            elif number.is_integer():
                output+=element+str(int(number))
            else:
                output+=element+str(number)
        return output

class Material():
    """
    Units used:
    b: fm
    fu_volume: Å³
    fu_dens: 1/Å³
    dens: g/cm³
    roh_n: Å^{-2}
    roh_m: Å^{-2}
    mu: muB/FU
    M: kA/m = emu/cm³
    """

    def __init__(self, elements, dens=None, fu_volume=None, rho_n=None, mu=0., xsld=None, xE=None):
        self.elements=elements
        # generate formula unit density using different priority of possible inputs
        if fu_volume is not None:
            self.fu_dens=1./fu_volume
        elif dens is not None:
            self.fu_dens=dens/self.fu_mass/u2g*1e-24
        elif rho_n is not None:
            self.fu_dens=abs(rho_n/self.fu_b)*1e5
        elif xsld is not None and xE is not None:
            self.fu_dens=abs(xsld/self.f_of_E(xE))*(1e5/r_e)
        else:
            raise ValueError(
                "Need to provide means to calculate density, {dens, fu_volume, rho_n, xsld+xE}")
        self.mu=mu

    @property
    def rho_n(self):
        return self.fu_b*self.fu_dens*1e-5 # Å^-1

    @property
    def rho_m(self):
        return self.M*rho_of_M

    @property
    def M(self):
        return self.mu*muB*self.fu_dens

    def f_of_E(self, E):
        f=0.
        for element, number in self.elements:
            f+=number*element.f_of_E(E)
        return f

    def delta_of_E(self, E):
        f=self.f_of_E(E)
        return f*r_e*self.fu_dens*1e-5 # Å^-1

    def delta_vs_E(self):
        # generate full energy range data
        E=self.elements[0][0].E
        for element, number in self.elements:
            E=E[(E>=element.E.min())&(E<=element.E.max())]
        delta=array([self.delta_of_E(Ei) for Ei in E])
        return E,delta

    @property
    def dens(self):
        return self.fu_mass*u2g*self.fu_dens*1e24 # g/cm³

    @property
    def fu_mass(self):
        m=0.
        for element, number in self.elements:
            m+=number*element.mass
        return m

    @property
    def fu_b(self):
        b=0.
        for element, number in self.elements:
            b+=number*element.b
        return b

    def convert_subscript(self, number):
        if number == 1.0:
            return ''
        nstr=str(number)
        out=''
        for digit in nstr:
            if digit == '.':
                if number.is_integer():
                    break
                out+='.'
            else:
                out+=SUBSCRIPT_DIGITS[int(digit)]
        return out

    def __str__(self):
        output=''
        for element, number in self.elements:
            nstr=self.convert_subscript(number)
            output+=element.symbol+nstr
        return output

    def __repr__(self):
        output='Material('
        output+=str([(ei.symbol, num) for ei, num in self.elements])
        output+=', fu_volume=%s'%(1./self.fu_dens)
        output+=')'
        return output

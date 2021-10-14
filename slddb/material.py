"""
Class to hold information for one material and allow calculation
of x-ray and neutron SLDs for different applications.
"""

import re
from numpy import array, pi
from collections import OrderedDict
from .constants import u2g, r_e, r_e_angstrom, muB, rho_of_M, Cu_kalpha, E_to_lambda, fm2angstrom

SUBSCRIPT_DIGITS="₀₁₂₃₄₅₆₇₈₉"

class Formula(list):
    """
    Evaluate strings for element chemical fomula.
    """
    elements=(r"A[cglmrstu]|B[aehikr]?|C[adeflmorsu]?|D[bsy]{0,1}|E[rsu]|F[emr]?|"
              r"G[ade]|H[efgosx]?|I[nr]?|Kr?|L[airu]|M[dgnot]|N[abdeiop]?|"
              r"Os?|P[abdmortu]?|R[abefghnu]|S[bcegimnr]?|T[abcehilm]|"
              r"Uu[bhopqst]|U|V|W|Xe|Yb?|Z[nr]")
    isotopes=(r"(A[cglmrstu]|B[aehikr]?|C[adeflmorsu]?|D[bsy]{0,1}|E[rsu]|F[emr]?|"
              r"G[ade]|H[efgos]?|I[nr]?|Kr?|L[airu]|M[dgnot]|N[abdeiop]?|"
              r"Os?|P[abdmortu]?|R[abefghnu]|S[bcegimnr]?|T[abcehilm]|"
              r"Uu[bhopqst]|U|V|W|Xe|Yb?|Z[nr])"
              r"\[[1-9][0-9]{0,2}\]")

    def __init__(self, string, sort=True):
        if isinstance(string, list):
            list.__init__(self, string)
            if isinstance(string, Formula):
                self._do_sort=string._do_sort
                self.HR_formula=string.HR_formula
            else:
                self._do_sort=sort
                self.HR_formula=str(self)
        else:
            self._do_sort=sort
            self.HR_formula=string
            list.__init__(self, [])
            self.parse_string(string)
            self.merge_same()

    def parse_string(self, string):
        # remove gaps and ignored characters
        string=string.replace(' ', '').replace('\t', '').replace('\n','')
        string=string.replace('{', '').replace('}', '').replace('_','').replace('$','')

        groups=self.split_groups(string)
        for group, factor in groups:
            try:
                items=self.parse_group(group, case_sensitive=True)
            except ValueError:
                items=self.parse_group(group, case_sensitive=False)
            items=[(i[0], i[1]*factor) for i in items]
            self+=items

    def split_groups(self, string):
        if not '(' in string:
            return [(string, 1.0)]
        out=[]
        start=string.index('(')
        end=start
        if start>0:
            out.append((string[:start], 1.0))
        while end<len(string):
            end=start+string[start:].find(')')
            next=end+1
            if end<start:
                raise ValueError('Brackets need to be closed')
            while not (next==len(string) or string[next].isalpha() or string[next]=='('):
                next+=1
            block=string[start+1:end]
            if '(' in block:
                raise ValueError("Only one level of brackets is allowed")
            number=string[end+1:next]
            if number=='':
                out.append((block, 1.0))
            else:
                out.append((block, float(number)))
            if next==len(string):
                break
            if not '(' in string[next:]:
                out.append((string[next:], 1.0))
                break
            else:
                start=next+string[next:].index('(')
                end=start
                if start>next:
                    out.append((string[next:start], 1.0))
        return out


    def parse_group(self, group, case_sensitive=True):
        if case_sensitive:
            flags=0
        else:
            flags=re.IGNORECASE
        out=[]
        mele=re.search(self.elements, group, flags=flags)
        miso=re.search(self.isotopes, group, flags=flags)
        if miso is not None and miso.start()==mele.start():
            prev=miso
        else:
            prev=mele
        if prev is None or prev.start()!=0:
            raise ValueError('Did not find any valid element in string')
        pos=prev.end()
        while pos<len(group):
            mele=re.search(self.elements, group[pos:], flags=flags)
            miso=re.search(self.isotopes, group[pos:], flags=flags)
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

    def __contains__(self, item):
        # check if an element is in the formula
        return item in [el[0] for el in self]

    def index(self, item):
        return [el[0] for el in self].index(item)

    def __add__(self, other):
        out=Formula(self[:]+other[:], sort=self.sort)
        out.merge_same()
        return out

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

    def __init__(self, elements, dens=None, fu_volume=None, rho_n=None, mu=0., xsld=None, xE=None,
                 fu_dens=None, M=None,
                 ID=None):
        self.elements=elements
        # generate formula unit density using different priority of possible inputs
        if fu_volume is not None:
            if dens is not None or fu_dens is not None:
                raise ValueError("fu_volume can't be supplied together with a density value")
            self.fu_dens=1./fu_volume
        elif dens is not None:
            if fu_dens is not None:
                raise ValueError("dens and fu_dens can't be provided at the same time")
            self.fu_dens=dens/self.fu_mass/u2g*1e-24
        elif fu_dens is not None:
            self.fu_dens=fu_dens
        elif rho_n is not None:
            self.fu_dens=abs(rho_n/self.fu_b)/fm2angstrom
        elif xsld is not None and xE is not None:
            self.fu_dens=abs(xsld/self.f_of_E(xE))*(1./r_e_angstrom)
        else:
            raise ValueError(
                "Need to provide means to calculate density, {dens, fu_volume, rho_n, xsld+xE}")
        if M is not None:
            if mu!=0.:
                raise ValueError("M and mu can't be provided at the same time")
            self.M=M
        else:
            self.mu=mu
        self.ID=ID

    @property
    def fu_volume(self):
        return 1./self.fu_dens

    @property
    def rho_n(self):
        return self.fu_b*self.fu_dens*fm2angstrom # Å^-1

    @property
    def rho_m(self):
        return self.M*rho_of_M

    @property
    def M(self):
        return self.mu*muB*self.fu_dens

    @M.setter
    def M(self, value):
        self.mu=value/self.fu_dens/muB

    def f_of_E(self, E=Cu_kalpha):
        f=0.
        for element, number in self.elements:
            f+=number*element.f_of_E(E)
        return f

    def rho_of_E(self, E):
        f=self.f_of_E(E)
        return f*r_e*self.fu_dens*fm2angstrom # Å^-1

    def delta_of_E(self, E):
        rho=self.rho_of_E(E)
        lamda=E_to_lambda/E
        return lamda**2/2./pi*rho.real

    def beta_of_E(self, E):
        rho=self.rho_of_E(E)
        lamda=E_to_lambda/E
        return -lamda**2/2./pi*rho.imag

    def mu_of_E(self, E):
        rho=self.rho_of_E(E)
        lamda=E_to_lambda/E
        return -lamda*2.*rho.imag

    def rho_vs_E(self):
        # generate full energy range data for E,SLD
        E=self.elements[0][0].E
        for element, number in self.elements:
            E=E[(E>=element.E.min())&(E<=element.E.max())]
        rho=array([self.rho_of_E(Ei) for Ei in E])
        return E,rho

    def delta_vs_E(self):
        E,rho=self.rho_vs_E()
        lamda=E_to_lambda/E
        return E,lamda**2/2./pi*rho.real

    def beta_vs_E(self):
        E,rho=self.rho_vs_E()
        lamda=E_to_lambda/E
        return E,-lamda**2/2./pi*rho.imag

    def mu_vs_E(self):
        E,rho=self.rho_vs_E()
        lamda=E_to_lambda/E
        return E,-lamda*2.*rho.imag

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

    @property
    def formula(self):
        output=''
        for element, number in self.elements:
            output+=element.symbol+str(number)
        return Formula(output)

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

    def __add__(self, other):
        # add two materials by adding the chemical formula and FU_volume of each element.
        if type(other)!=type(self):
            raise ValueError('Can only combine two Material instances.')
        fout=dict(self.elements)
        for ele, number in other.elements:
            if ele in fout:
                fout[ele]+=number
            else:
                fout[ele]=number
        fout=list(fout.items())
        Vout=self.fu_volume+other.fu_volume
        mout=self.mu+other.mu
        return Material(fout, fu_volume=Vout, mu=mout)

    def __mul__(self, other):
        """
        Calculate a multiple of this material, mostly useful when combining
        different components. The SLD should stay the same as the formula
        as well as the FU_volume are multiplied with the same amount.
        """
        if type(other) in [int, float]:
            fout=[(ele, number*other) for ele, number in self.elements]
            return Material(fout, fu_volume=self.fu_volume*other,
                            mu=self.mu*other)
        else:
            raise ValueError("Can only multiply material by scalar")

    def __rmul__(self, other):
        return self.__mul__(other)

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
        if self.ID:
            output+=', ID=%i'%self.ID
        output+=')'
        return output

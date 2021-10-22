"""
Generate a python file that stores data collected from various sources.
"""
import os
import periodictable
import numpy as np
from slddb import constants
from urllib import request, error as urlerr

def calc_mass(element, atoms, isotopes):
    isos = [iso for iso in isotopes if iso[0]==atoms[element][0] and iso[3]!='']
    sub = [iso[2]*float(iso[3].split('(')[0]) for iso in isos]
    if len(sub)==0:
        return None
    else:
        return sum(sub)

def collect_weights():
    global Z_by_name

    txt=open('atomic_weights.txt', 'r').read()
    atoms={}
    isotopes=[]
    for isotope in txt.split('\n\n'):
        lns = [ln for ln in isotope.splitlines() if not ln.startswith('#')]
        Z = int(lns[0].split('=')[1])
        El = lns[1].split('=')[1].strip()
        N = int(lns[2].split('=')[1])
        mI = float(lns[3].split('=')[1].split('(')[0])
        cI = lns[4].split('=')[1].strip()
        aW = lns[5].split('=')[1].strip()
        atoms[El] = (Z, aW)
        isotopes.append((Z, N, mI, cI))

    weights={}
    Z_by_name={}
    full_names={}
    for Z, N, mI, cI in isotopes:
        weights[(Z, N)]=mI
    for El, (Z, aW) in atoms.items():
        Z_by_name[El]=Z
        ptel=getattr(periodictable, El, None)
        if ptel:
            full_names[El]=ptel.name
        else:
            full_names[El]=El
        if aW=='':
            weights[El]=None
        elif '[' in aW:
            weights[El]=calc_mass(El, atoms, isotopes)
        else:
            weights[El]=float(aW.split('(')[0])
    abundances={}
    for Z, N, mI, cI in isotopes:
        if cI=='':
            abundances[(Z, N)]=None
        else:
            abundances[(Z, N)]=float(cI.split('(')[0])


    output='ATOMIC_WEIGHTS='+repr(weights)+'\n'
    output+='ISOTOPE_ABUNDANCES='+repr(abundances)+'\n'
    output+='ELEMENT_CHARGES='+repr(Z_by_name)+'\n'
    output+='ELEMENT_FULLNAMES='+repr(full_names)+'\n'

    header='\n'.join([ln[2:] for ln in txt.splitlines() if ln.startswith('#')])
    open(os.path.join('..', 'slddb', 'element_table', 'masses.py'), 'w').write(f'"""\n{header}\n"""\n\n{output}')

def collect_nlengths():
    txt = open('nist_nlengths.txt', 'r').read()
    nlengths={}
    for line in txt.splitlines():
        if line.startswith('#'):
            continue
        itms = line.split('\t')
        if itms[0][0].isdigit():
            i=0
            while itms[0][i].isdigit():
                i+=1
            N=int(itms[0][:i])
            El=itms[0][i:]
            Z=Z_by_name[El]
            key=(Z,N)
        else:
            El=itms[0]
            key=El
        try:
            b=complex(itms[2].split('(', 1)[0].replace('i', 'j'))
        except ValueError:
            b=None
        nlengths[key]=b

    header = '\n'.join([ln[2:] for ln in txt.splitlines() if ln.startswith('#')])
    output='NEUTRON_SCATTERING_LENGTHS='+repr(nlengths)+'\n'
    open(os.path.join('..', 'slddb', 'element_table', 'nlengths.py'), 'w').write(f'"""\n{header}\n"""\n\n{output}')

def collect_nlengths_pt():
    nlengths={}
    for element in periodictable.elements:
        Z=element.number  # charge

        if element.neutron.b_c is not None:
            b=element.neutron.b_c-1j*constants.sigma_to_b*element.neutron.absorption
            nlengths[element.symbol]=b

        for N in element.isotopes:
            abundance=element[N].abundance
            if abundance > 0 and element[N].neutron.b_c is not None:
                b=element[N].neutron.b_c-1j*constants.sigma_to_b*element[N].neutron.absorption
                key=(Z, N)
                nlengths[key]=b

    header = 'Rauch, H. and Waschkowski, W. (2003) Neutron Scattering Lengths in ILL Neutron Data Booklet (second edition), ' \
             'A.-J. Dianoux, G. Lander, Eds. Old City Publishing, Philidelphia, PA. pp 1.1-1 to 1.1-17. ' \
             '(https://www.ill.eu/fileadmin/user_upload/ILL/1_About_ILL/Documentation/NeutronDataBooklet.pdf)' \
             'Imported from python periodictable package'
    output='NEUTRON_SCATTERING_LENGTHS='+repr(nlengths)+'\n'
    open(os.path.join('..', 'slddb', 'element_table', 'nlengths_pt.py'), 'w').write(f'"""\n{header}\n"""\n\n{output}')

def collect_nabsorptions():
    # datasets are large, so store as numpy array directly
    nlengths={}
    for element in periodictable.elements:
        Z=element.number  # charge

        resdir=os.path.join('..', 'slddb', 'element_table', 'nabs_geant4')
        if not os.path.exists(resdir):
            os.mkdir(resdir)

        if os.path.exists(os.path.join('geant4', f'g4xs_{element.symbol}.txt')):
            E,_,xs_a=np.loadtxt(os.path.join('geant4', f'g4xs_{element.symbol}.txt')).T
            L=constants.h_Js/np.sqrt(2*E*constants.eV2J*constants.m_n)*constants.m2angstrom
            fltr=(L>=0.05)&(L<=50.0)
            b_abs=xs_a*constants.sigma_to_b_1A/L
            order=L[fltr].argsort()
            data=np.array([L[fltr][order], b_abs[fltr][order]])
            fname=f'nabs_{element.symbol}.npz'
            np.savez(os.path.join('..', 'slddb', 'element_table', 'nabs_geant4', fname), data)
            nlengths[element.symbol]=fname

        for N in element.isotopes:
            abundance=element[N].abundance
            if abundance > 0 and element[N].neutron.b_c is not None:
                key=(Z, N)
                if os.path.exists(os.path.join('geant4', f'g4xs_{element.symbol}{N}.txt')):
                    E, _, xs_a=np.loadtxt(os.path.join('geant4', f'g4xs_{element.symbol}{N}.txt')).T
                    L = constants.h_Js/np.sqrt(2*E*constants.eV2J*constants.m_n)*constants.m2angstrom
                    fltr=(L >= 0.05) & (L <= 50.0)
                    b_abs=xs_a*constants.sigma_to_b_1A/L
                    order=L[fltr].argsort()
                    data = np.array([L[fltr][order], b_abs[fltr][order]])
                    fname = f'nabs_{element.symbol}{N}.npz'
                    np.savez(os.path.join('..', 'slddb', 'element_table', 'nabs_geant4', fname), data)
                    nlengths[key] = fname

    header = 'Neutron cross sections extracted from Geant4 by the ESS dgcode framework (doi:10.1016/j.physb.2018.03.025).'
    output='DATA_DIR="nabs_geant4"\n'
    output+='NEUTRON_ABSORPTIONS='+repr(nlengths)+'\n'
    open(os.path.join('..', 'slddb', 'element_table', 'nabs_geant4.py'), 'w').write(f'"""\n{header}\n"""\n\n{output}')

def collect_xray():
    xres={}
    for El in Z_by_name.keys():
        print(f'Query Henke for {El}')
        try:
            res=request.urlopen(f'https://henke.lbl.gov/optical_constants/sf/{El.lower()}.nff').read()
        except urlerr.HTTPError:
            continue
        print('   Success')
        data=[]
        for ln in res.splitlines()[1:]:
            E,f1,f2=map(float, ln.split(None, 2))
            E/=1e3
            if f1==-9999.:
                f1=np.nan
            if f2==-9999.:
                f2=np.nan
            data.append([E,f1,f2])
        xres[El]=np.array(data).T.tolist()

    header = 'Data downloaded from Henke tables at https://henke.lbl.gov/optical_constants/asf.html'
    output = 'nan=float("nan")\n\n'
    output +='XRAY_SCATTERING_FACTORS='+repr(xres)+'\n'
    open(os.path.join('..', 'slddb', 'element_table', 'xray_henke.py'), 'w').write(f'"""\n{header}\n"""\n\n{output}')

def collect_xray_new():
    xres={}
    for El,Z in Z_by_name.items():
        print(f'NIST Standard Reference Database for {El}')
        try:
            res=request.urlopen(f'https://physics.nist.gov/cgi-bin/ffast/ffast.pl?Z={Z}&Formula=&gtype=4&lower=&upper=&density=&frames=no').read()
        except urlerr.HTTPError:
            continue
        data=[]
        for ln in res.splitlines()[26:]:
            items=ln.split(None, 3)
            try:
                E,f1,f2=map(float, items[:3])
            except ValueError:
                continue
            if f1==-9999.:
                f1=np.nan
            if f2==-9999.:
                f2=np.nan
            data.append([E,f1,f2])
        if len(data)==0:
            continue
        xres[El]=np.array(data).T.tolist()

    header = 'Data downloaded from NIST Standard Reference Database at https://physics.nist.gov/PhysRefData/FFast/html/form.html'
    output='nan=float("nan")\n\n'
    output+='XRAY_SCATTERING_FACTORS='+repr(xres)+'\n'
    open(os.path.join('..', 'slddb', 'element_table', 'xray_nist.py'), 'w').write(f'"""\n{header}\n"""\n\n{output}')


if __name__=='__main__':
    collect_weights()
    collect_nlengths()
    collect_nlengths_pt()
    collect_nabsorptions()
    collect_xray()
    collect_xray_new()

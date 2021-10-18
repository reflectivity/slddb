"""
Generate a python file that stores data collected from various sources.
"""
import os
import periodictable
import numpy as np
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
    #collect_xray()
    #collect_xray_new()

"""
Database entreis for soft matter and biology calculations.
"""

import slddb
from slddb import __version__, dbconfig
# for flask use database file in startup folder
DB_FILE='slddb.db';dbconfig.DB_FILE=DB_FILE;slddb.DB_FILE=DB_FILE
from slddb import SLDDB
from slddb.dbconfig import DB_FILE


###################### Water #####################
T0=273.15 # K to °C
WATER_DENSITY_LINK='https://www.usgs.gov/special-topic/water-science-school/science/water-density'
WATER_DENSITY_REF='U.S. Department of the Interior, Bureau of Reclaimation, 1977, Ground Water Manual, from ' \
                  'The Water Encyclopedia, Third Edition, Hydrologic Data and Internet Resources, ' \
                  'Edited by Pedro Fierro, Jr. and Evan K. Nyler, 2007'
WATER_DENSITY = [
    # T (°C)  dens (g/cm³)
    [  0.0,  0.99987],
    [  4.0,  1.00000],
    [  4.4,  0.99999],
    [ 10.0,  0.99975],
    [ 15.6,  0.99907],
    [ 21.0,  0.99802],
    [ 26.7,  0.99669],
    [ 32.2,  0.99510],
    [ 37.8,  0.99318],
    [ 48.9,  0.98870],
    [ 60.0,  0.98338],
    [ 71.1,  0.97729],
    [ 82.2,  0.97056],
    [ 93.3,  0.96333],
    [100.0,  0.95865],
    ]
def enter_water():
    db=SLDDB(DB_FILE)
    for T,dens in WATER_DENSITY:
        print(f'Water at {T}°C with density {dens}')
        db.add_material(f'Water', 'H2O',
                        description=f"Water at {T}°C", reference=WATER_DENSITY_REF,
                        ref_website=WATER_DENSITY_LINK, density=dens, temperature=T0+T,
                        physical_state='liquid', data_origin='textbook')

################ Proteins, RND, DNA ###############
AMINO_DENS_REF='"Neutron scattering in biology: Techniques and Applications" (pg 15, ISSN: 1618-7210)'
AMINO_HEX_REF='"The study of biological molecules by neutron scattering" by B Jacrot (Rep. Prog. Phys. 1976 39 911-953)'
AMINO_REF_DOI='10.1088/0034-4885/39/10/001'
AMINO_REF_LINK='https://www.springer.com/gp/book/9783540291084'
AMINO_DATA=[
    # Hx is the hydrogen that exchanges, so the actual formula H=H+Hx
    # Name             Formula+H(ex)   FU_volume
    ['Glycine',        'C2NOH2Hx',     59.9],
    ['Alanine',        'C3NOH4Hx',     87.8],
    ['Valine',         'C5NOH8Hx',     138.8],
    ['Leucine',        'C6NOH10Hx',    168.0],
    ['Isoleucine',     'C6NOH10Hx',    166.1],
    ['Phenylalanine',  'C9NOH8Hx',     189.7],
    ['Tyrosine',       'C9NO2H7Hx2',   192.2],
    ['Tryptophan',     'C11N2OH8Hx2',  227.9],
    ['Aspartate',      'C4NO3H3Hx',    120.1],
    ['Glutamate',      'C5NO3H5Hx',    145.1],
    ['Serine',         'C3NO2H3Hx2',   91.7],
    ['Threonine',      'C4NO2H5Hx2',   118.3],
    ['Asparagine',     'C4N2O2H3Hx3',  115.4],
    ['Glutamine',      'C5N2O2H5Hx3',  140.9],
    ['Lysine',         'C6N2OH9Hx4',   172.7],
    ['Arginine',       'C6N4OH7Hx6',   188.2],
    ['Histidine',      'C6N3OH5Hx1.5', 156.3],
    ['Methionine',     'C5NOSH8Hx',    165.2],
    ['Cysteine',       'C3NOSH3Hx2',   105.4],
    ['Proline',        'C5NOH7',       123.3],
    ]
def enter_amino():
    db=SLDDB(DB_FILE)
    for name, formula, fu_volume in AMINO_DATA:
        print(f'{name}: {formula}    {fu_volume}')
        db.add_material(name, formula,
                        description=f"Amino acid in protein", reference=f'{AMINO_DENS_REF}|{AMINO_HEX_REF}',
                        ref_website=AMINO_REF_LINK, doi=AMINO_REF_DOI, FU_volume=fu_volume,
                        tags=['biology', 'small organic'],
                        physical_state='solution', data_origin='textbook')


RNA_ABRV=[
    ["RNA-Adenine",     'C10H9Hx3O6N5P',      314.0],
    ["RNA-Guanine",     'C10H8Hx4O7N5P',      326.3],
    ["RNA-Cytosine",    'C9H10Hx2O7N3P',      285.6],
    ["RNA-Uracil",      'C9H9Hx2O8N2P',       282.3],
    ]
DNA_ABRV=[
    ["DNA-Adenine",     'C10H10Hx2O5N5P',     314.0],
    ["DNA-Guanine",     'C10H9Hx3O6N5P',      326.3],
    ["DNA-Cytosine",    'C9H9Hx3O6N3P',       285.6],
    ["DNA-Thymine",     'C10H12Hx1O7N2P',     308.7],
    ]
def enter_rnadna():
    db=SLDDB(DB_FILE)
    for name, formula, fu_volume in RNA_ABRV:
        print(f'{name}: {formula}    {fu_volume}')
        db.add_material(name, formula,
                        description=f"Nucleotides in RNA", reference=AMINO_DENS_REF,
                        ref_website=AMINO_REF_LINK, FU_volume=fu_volume,
                        tags=['biology', 'small organic'],
                        physical_state='solution', data_origin='textbook')
    for name, formula, fu_volume in DNA_ABRV:
        print(f'{name}: {formula}    {fu_volume}')
        db.add_material(name, formula,
                        description=f"Nucleotides in DNA", reference=AMINO_DENS_REF,
                        ref_website=AMINO_REF_LINK, FU_volume=fu_volume,
                        tags=['biology', 'small organic'],
                        physical_state='solution', data_origin='textbook')


if __name__=="__main__":
    enter_water()
    enter_amino()
    enter_rnadna()

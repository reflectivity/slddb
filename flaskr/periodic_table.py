from flask import flash, render_template, redirect, url_for
from orsopy.slddb import SLDDB, DB_FILE
from orsopy.slddb.element_table.element import ELEMENT_NAMES, ELEMENT_FULLNAMES
from orsopy.slddb.element_table import get_element
from orsopy.slddb.constants import Cu_kalpha, Mo_kalpha

# The number of elements on the left and right of the periodic table per row
COL_RANGES = [(1, 1), (2, 6), (2, 6), (2, 16), (2, 16), (3, 15), (3, 15)]

# Generate data that is only calculated once
ELEMENTS = {}
Z = 1
for row in range(7):
    for left in range(COL_RANGES[row][0]):
        ELEMENTS[row, left] = (Z, ELEMENT_NAMES[Z])
        Z += 1
    if row>4:
        ELEMENTS[row+3, 2] = (Z-1, ELEMENT_NAMES[Z-1])
        for sub in range(14):
            ELEMENTS[row+3, 3+sub] = (Z, ELEMENT_NAMES[Z])
            Z += 1
    for right in range(COL_RANGES[row][1]):
        ELEMENTS[row, 18-COL_RANGES[row][1]+right] = (Z, ELEMENT_NAMES[Z])
        Z += 1

GROUP_COLORS={0: [200, 255, 200], 17: [240, 180, 240]}
GROUP_COLORS[1] = [200, 255, 200]
for g in range(2,12):
    GROUP_COLORS[g]=[255, 200, 200]
for g in range(12,17):
    GROUP_COLORS[g]=[200, 200, 255]
GROUP_COLORS[18] = [255, 255, 150]
ELEMENT_COLORS=dict([(Z, GROUP_COLORS[col]) if row<7 else (Z, GROUP_COLORS[18]) for (row, col), (Z, _) in ELEMENTS.items()])
# Color La and Ac as 4f
ELEMENT_COLORS[57]=[200, 200, 100]
ELEMENT_COLORS[89]=ELEMENT_COLORS[57]
FULLNAMES_OF_Z=dict([(Z, ELEMENT_FULLNAMES[ele].capitalize()) for Z, ele in ELEMENT_NAMES.items()])

ELEMENT_B = {}
ELEMENT_F = {}
ELEMENT_F_MO = {}
ELEMENT_WEIGHT = {}
PLOT_SCALES = {None: None, 'neutron': {}, 'xray': {}, 'xrayMo': {}}

for Z, ele in ELEMENT_NAMES.items():
    try:
        element = get_element(ele)
    except ValueError:
        PLOT_SCALES['neutron'][Z] = [0, 0, 0]
        PLOT_SCALES['xray'][Z] = [0, 0, 0]
        PLOT_SCALES['xrayMo'][Z] = [0, 0, 0]
        continue
    bi = element.b
    fi = element.f_of_E(Cu_kalpha)
    fMoi = element.f_of_E(Mo_kalpha)
    mi = element.mass
    PLOT_SCALES['neutron'][Z] = [100+int(bi.real*125./13), 100+int(bi.real*125./13), 130+int(bi.real*125./10)]
    try:
        PLOT_SCALES['xray'][Z] = [75+int(fi.real*2), 75+int(fi.real*1.5), 75+int(fi.real*1.5)]
    except ValueError:
        PLOT_SCALES['xray'][Z] = [0, 0, 0]
    try:
        PLOT_SCALES['xrayMo'][Z] = [75+int(fMoi.real*1.5), 75+int(fMoi.real*2.0), 75+int(fMoi.real*1.5)]
    except ValueError:
        PLOT_SCALES['xrayMo'][Z] = [0, 0, 0]
    if bi is not None:
        ELEMENT_B[Z] = f'{bi.real:.3f}-{-bi.imag:.3f}i'
    if fi is not None:
        ELEMENT_F[Z] = f'{fi.real:.3f}-{-fi.imag:.3f}i'
        ELEMENT_F_MO[Z] = f'{fMoi.real:.3f}-{-fMoi.imag:.3f}i'
    if mi is not None:
        ELEMENT_WEIGHT[Z] = mi


def get_periodic_table(requested_element=None, plot_scale=None):
    if requested_element:
        db = SLDDB(DB_FILE)
        try:
            res = db.search_material(formula=requested_element, name=ELEMENT_FULLNAMES[requested_element])
        except ValueError:
            res=[]
        if len(res)>0:
            return redirect(url_for('calculate_sld', _anchor='results_header', ID=res[0]['ID']))
        else:
            flash(f'No SLD for {ELEMENT_FULLNAMES[requested_element]}')
    scale_colors=PLOT_SCALES[plot_scale]
    return render_template('periodic_table.html', elements=ELEMENTS,
                           element_names=ELEMENT_NAMES, element_colors=ELEMENT_COLORS,
                           element_fullnames=FULLNAMES_OF_Z, element_weight=ELEMENT_WEIGHT,
                           element_b=ELEMENT_B, element_f=ELEMENT_F, element_fMo=ELEMENT_F_MO,
                           scale_colors=scale_colors)

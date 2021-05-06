from flask import render_template

from slddb.constants import Cu_kalpha, Mo_kalpha
from slddb import SLDDB, DB_FILE
from slddb.material import Material, Formula

from numpy import nan_to_num
import base64
from io import BytesIO
from matplotlib.figure import Figure

def get_graph(E, real, imag, name='Iron'):
    # Generate the figure **without using pyplot**.
    fig = Figure()
    ax = fig.subplots()
    ax.plot(E, real, label='real')
    ax.plot(E, imag, label='imaginary')
    ax.set_xlabel('E (keV)')
    ax.set_ylabel('SLD (Å⁻²)')
    ax.set_title('X-Ray optical parameters for %s'%name)
    # Save it to a temporary buffer.
    buf = BytesIO()
    fig.savefig(buf, format="png")
    fig.tight_layout()
    # Embed the result in the html output.
    data = base64.b64encode(buf.getbuffer()).decode("ascii")
    return f"<img src='data:image/png;base64,{data}'/>"

def calculate_selection(ID):
    db=SLDDB(DB_FILE)
    res=db.search_material(ID=ID)
    try:
        material=db.select_material(res[0])
    except Exception as e:
        return render_template('base.html', error=repr(e)+'<br >'+"Raised when tried to parse material = %s"%res[0])
    E, delta=material.delta_vs_E()
    script=get_graph(E, delta.real, delta.imag, res[0]['name'])
    return render_template('sldcalc.html', material=material, material_name=res[0]['name'],
                           material_description=res[0]['description'], Cu_kalpha=Cu_kalpha,
                           Mo_kalpha=Mo_kalpha, script=script, xray_E=E.tolist(),
                           xray_delta_real=nan_to_num(delta.real).tolist(),
                           xray_delta_imag=nan_to_num(delta.imag).tolist(),
                           validated=res[0]['validated'], validated_by=res[0]['validated_by'],
                           formula=res[0]['formula'], density=material.dens, mu=material.mu)

def calculate_user(formula, density, is_density, mu):
    db=SLDDB(DB_FILE)
    try:
        if is_density:
            m=Material([(db.elements.get_element(element), amount) for element, amount in formula],
                   dens=density, mu=mu)
        else:
            m=Material([(db.elements.get_element(element), amount) for element, amount in formula],
                       fu_volume=density, mu=mu)
    except Exception as e:
        return render_template('sldcalc.html', error=repr(e)+'<br/>'+str(e))
    else:
        E, delta=m.delta_vs_E()
        script=get_graph(E, delta.real, delta.imag, str(formula))
        return render_template('sldcalc.html', material=m, material_name="User input",
                           material_description="", Cu_kalpha=Cu_kalpha,
                           Mo_kalpha=Mo_kalpha, script=script, xray_E=E.tolist(),
                           xray_delta_real=nan_to_num(delta.real).tolist(),
                           xray_delta_imag=nan_to_num(delta.imag).tolist())

def validate_selection(ID, user):
    db=SLDDB(DB_FILE)
    db.validate_material(ID, user)
    return calculate_selection(ID)


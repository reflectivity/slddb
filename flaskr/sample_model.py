import yaml
import json
import sqlite3
import hashlib

from flask import render_template

from numpy import linspace
from io import BytesIO
from matplotlib.figure import Figure
from dataclasses import dataclass, asdict

from orsopy.fileio.model_building_blocks import Material
from refnx.reflect import SLD, ReflectModel, Structure
from orsopy.fileio import model_language, model_complex
from orsopy.slddb import api as slddb_api
from orsopy.slddb import SLDDB, DB_FILE
from orsopy.utils.chemical_formula import Formula

# make sure the material resolution is done locally
slddb_api.use_webquery = False

q = linspace(0.001, 0.4, 400)

def sample_form():
    return render_template('sample.html')

@dataclass
class LayerInfo:
    thickness: float
    roughness: float
    sldx_r: float
    sldx_i: float
    sldn_r: float
    sldn_i: float
    sldm: float

#TODO: Add resolved_samples table creation to databse setup.
def simulate_reflectivity(hash):
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    qstr = "SELECT data FROM resolved_samples WHERE hash=?"
    c.execute(qstr, (hash,))
    res = c.fetchone()
    data = json.loads(res[0])
    layers = [LayerInfo(**di) for di in data]
    magnetic = any([li.sldm for li in layers])

    fig = Figure(figsize=(6,8))
    fig.set_facecolor('none')
    ax, ax2 = fig.subplots(nrows=2)

    structure = Structure()
    structurex = Structure()
    if magnetic:
        structure_down = Structure()
    for lj in layers:
        mx = SLD(lj.sldx_r+1j*lj.sldx_i)
        structurex |= mx(lj.thickness, lj.roughness)
        if magnetic:
            m = SLD(lj.sldn_r+lj.sldm+lj.sldn_i*1j)
            m_down = SLD(lj.sldn_r-lj.sldm+lj.sldn_i*1j)
            structure_down |= m_down(lj.thickness, lj.roughness)
        else:
            m = SLD(lj.sldn_r+lj.sldn_i*1j)
        structure |= m(lj.thickness, lj.roughness)
    model = ReflectModel(structure, bkg=0.0)
    if magnetic:
        model_down = ReflectModel(structure_down, bkg=0.0)
    modelx = ReflectModel(structurex, bkg=0.0)

    ax.set_title('sample reflectivity')
    if magnetic:
        ax.semilogy(q, model(q)+1e-9, label="neutron-u", color='C0')
        ax.semilogy(q, model_down(q)+1e-9, label="neutron-d", color='C2')
    else:
        ax.semilogy(q, model(q)+1e-9, label="neutron", color='C0')
    ax.semilogy(q, modelx(q)+1e-9, label="x-ray (Cu)", color='C1')
    ax.legend(loc='lower left')
    ax.set_xlabel("q / Å$^{-1}$")
    ax.set_ylabel("Reflectivity")

    ax2.set_title('sample SLD profiles')
    ax2.set_ylabel('SLDn / 10$^{-6}$ Å$^{-1}$')
    ax2.set_xlabel('depth / nm')
    x,y=structure.sld_profile()
    if magnetic:
        ax2.plot(x/10., y, color='C0', label="neutron-u")
        x, y = structure_down.sld_profile()
        ax2.plot(x/10., y, color='C2', label="neutron-d")
    else:
        ax2.plot(x/10., y, color='C0', label="neutron")
    ax2x=ax2.twinx()
    x,y=structurex.sld_profile()
    ax2x.plot(x/10., y, color='C1', label="x-ray (Cu)")
    ax2x.set_ylabel('SLDx / 10$^{-6}$ Å$^{-1}$')
    fig.subplots_adjust(hspace=0.35, wspace=0.1, top=0.95, bottom=0.1, left=0.15, right=0.85)

    # Save it to a temporary buffer.
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=300)
    return bytes(buf.getbuffer())

bM=0.000_002_7 # nm / µB
def create_plot_link(sample:model_language.SampleModel):
    plink='plot_sample.png?'
    layers = sample.resolve_to_layers()
    data = []
    for lj in layers:
        nsld = complex(lj.material.get_sld() * 1e6+0j)
        if getattr(lj.material, 'magnetic_moment', None) is not None:
            msld = float(bM*lj.material.magnetic_moment.as_unit('muB')*lj.material.number_density.as_unit('1/nm^3')*1e4)
        else:
            msld = 0.
        xsld = complex(lj.material.get_sld(xray_energy="Cu") * 1e6 + 0j)
        data.append(
                asdict(LayerInfo(thickness=lj.thickness.as_unit("angstrom"),
                          roughness=lj.roughness.as_unit("angstrom"),
                          sldx_r=xsld.real, sldx_i=xsld.imag,
                          sldn_r=nsld.real, sldn_i=nsld.imag,
                          sldm=msld
                          ))
                )
    data_str = json.dumps(data).encode('utf-8')
    hash = hashlib.sha256(data_str).hexdigest()
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    qstr = "SELECT * FROM resolved_samples WHERE hash=? AND inserted < date('now', '+30 days')"
    c.execute(qstr, (hash,))
    if len(c.fetchall())==0:
        # purge old data
        qstr = "DELETE FROM resolved_samples WHERE inserted < date('now', '+30 days')"
        c.execute(qstr)
        qstr = "INSERT INTO resolved_samples (hash, data) VALUES (?,?)"
        c.execute(qstr, (hash, data_str))
        c.close()
        db.commit()


    plink += f'hash={hash}'
    return plink

def sample_form_eval(data_yaml, single_layer=False):
    try:
        # parse data as yaml
        data = yaml.safe_load(data_yaml)
    except Exception as e:
        error = f'Could not parse yaml data:<br />{repr(e)}'
        return render_template('sample.html', error=error)

    if "data_source" in data:
        data = data["data_source"]
    if "sample" in data:
        data = data["sample"]
    if "model" in data:
        data = data["model"]

    try:
        sample = model_language.SampleModel(**data)
    except Exception as e:
        error = f'Could not parse the sample model:<br />{repr(e)}<br />'
        error += f'<div class="tooltip">Hover here for YAML data<div class="tooltiptext">{data}</div></div>'
        return render_template('sample.html', error=error)
    # connect resolution API to local database
    slddb_api.db = SLDDB(DB_FILE)
    try:
        if single_layer:
            structure = structure_to_html(sample.resolve_to_layers())
        else:
            structure = structure_to_html(sample.resolve_stack())
    except Exception as e:
        error = f'Could not evaluate the sample model:<br />{repr(e)}<br />'
        error += f'<div class="tooltip">Hover here for SampleModel<div class="tooltiptext">{sample}</div></div>'
        return render_template('sample.html', error=error)

    try:
        img = create_plot_link(sample)
    except Exception as e:
        error = f'Could not evaluate the layer sequence:<br />{repr(e)}<br />'
        return render_template('sample.html', structure=structure, error=error)

    slddb_api.db.db.close()
    slddb_api.db=None
    return render_template('sample.html', structure=structure, img=img)

def structure_to_html(items):
    output = ""
    for item in items:
        if isinstance(item, model_language.Layer):
            item_table_html = layer_table(item)
            if 'average element density' in (item.material.comment or 'none') or \
                getattr(item.material, 'relative_density', None) is not None:
                output += f'<div class="sample_mixed">{item_table_html}</div>\n'
            elif item.material.comment is None:
                output += f'<div class="sample_defined">{item_table_html}</div>\n'
            else:
                output+=f'<div class="sample_item">{item_table_html}</div>\n'
        elif isinstance(item, model_language.SubStack):
            if item.original_name:
                output += f'<div class="sample_stack">{item.repetitions} x {item.original_name}\n    '
            else:
                output+=f'<div class="sample_stack">{item.repetitions} x Stack\n    '
            output+=structure_to_html(item.sequence).replace('\n', '    \n')
            output+='</div>\n'
        elif isinstance(item, model_complex.FunctionTwoElements):
            output += (f'<div class="sample_special"><table><tr><th>{item.original_name or ""}</th><td class="alignright">FunctionTwoElements\n'
                       f'<div class="tooltip">🛈<div class="tooltiptext"> SLD = m1 * (f-1) + m2 * f<br />'
                       f'f(x) = {item.function}<br />(with x = (z-z0)/d</div></div></td></tr></table>\n    ')
            output+=two_elements_table(item)
            output+='</div>\n'
        else:
            output+= '<div class="sample_unknown">Unknown Item Type</div>\n'
    return output

def layer_table(layer:model_language.Layer):
    if layer.material is None:
        layer.generate_material()
    if isinstance(layer.material, model_language.Composit):
        return composite_table(layer)
    output = '<table class="layer">\n'
    material = layer.material
    material.generate_density()
    material_info = get_material_info(material)

    output += f'<tr><th rowspan="2" class="expand">{layer.original_name or layer.material.original_name or ""}</th><th>material</th><th>d</th><th>σ</th></tr>\n'
    output += f'<tr><td>{getattr(layer.material, "formula", None) or "SLD"} <div class="tooltip">🛈<div class="tooltiptext">' \
              f'{material_info}' \
              f'</div></div></td><td>{layer.thickness.as_unit("nm"):.2f}</td>' \
              f'<td>{layer.roughness.as_unit("nm"):.1f}</td></tr>\n'
    output += '</table>\n'
    return output


def get_material_info(material: Material) -> str:
    material_info = f'{material.comment or "defined values"}<br />'
    for key in ['formula', 'number_density', 'mass_density', 'sld', 'relative_density', 'magnetic_moment']:
        value = getattr(material, key, None)
        if value:
            if hasattr(value, 'magnitude'):
                value = f'{value.magnitude:.3g} {value.unit}'
            elif hasattr(value, 'real') and hasattr(value, 'unit'):
                value = f'{value.real:.3g}+{value.imag:.3g}i {value.unit}'
            material_info += f'{key} = {value}<br />'
    return material_info


def two_elements_table(item:model_complex.FunctionTwoElements):
    output = '<table class="layer">\n'
    SRinfo = (f'<div class="tooltip">🛈<div class="tooltiptext">slice resolution {item.slice_resolution.as_unit("nm"):.0f} nm<br />'
              f'=>{int(item.thickness.as_unit("nm")/item.slice_resolution.as_unit("nm"))} slices</div></div>')
    output += '<tr>' \
              f'<th>mat. 1</th><th>mat. 2</th><th>d </th><th>σ</th></tr>\n'
    output += '<tr>'
    m1, m2 = item._materials
    m1.generate_density()
    m2.generate_density()
    m1info = get_material_info(m1)
    m2info = get_material_info(m2)
    output += f'<tr><td>{getattr(m1, "formula", None) or "SLD"} ' \
              f'<div class="tooltip">🛈<div class="tooltiptext">{m1info}</div></div></td>'
    output += f'<td>{getattr(m2, "formula", None) or "SLD"} ' \
              f'<div class="tooltip">🛈<div class="tooltiptext">{m2info}</div></div></td>'
    output +=f'<td>{item.thickness.as_unit("nm"):.2f} {SRinfo}</td>' \
              f'<td>{item.roughness.as_unit("nm"):.1f}</td></tr>\n'


    output += '</table>\n'
    return output

def composite_table(layer:model_language.Layer):
    nitems = len(layer.material.composition)

    layer.material.generate_density()
    output = '<table class="layer">\n'
    output += f'<tr><th rowspan="{nitems+1}" class="expand">{layer.original_name or layer.material.original_name or "composit"}</th>' \
              f'<th>fraction</th><th>material</th><th>d</th><th>σ</th></tr>\n'
    for i, (key, fraction) in enumerate(layer.material.composition.items()):
        material = layer.material._composition_materials[key]

        material_info = f'{material.comment or "defined values"}<br />'
        for key in ['formula', 'number_density', 'mass_density', 'sld', 'relative_density']:
            value = getattr(material, key, None)
            if value:
                if hasattr(value, 'magnitude'):
                    value = f'{value.magnitude:.3g} {value.unit}'
                elif hasattr(value, 'real'):
                    value = f'{value.real:.3g}+{value.imag:.3g}i {value.unit}'
                material_info += f'{key} = {value}<br />'

        output += f'<tr><td>{getattr(material, "formula", None) or key} <div class="tooltip">🛈<div class="tooltiptext">' \
              f'{material_info}' \
              f'</div></div></td><td>{fraction*100:.1f}%</td>'
        if i==0:
            output += f'<td rospan="{nitems}">{layer.thickness.as_unit("nm"):.2f}</td>' \
                      f'<td rospan="{nitems}">{layer.roughness.as_unit("nm"):.1f}</td></tr>\n'
        else:
            output += '</tr>\n'

    output += '</table>\n'
    return output

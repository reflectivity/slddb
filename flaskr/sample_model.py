import yaml

from flask import render_template

from numpy import linspace
from io import BytesIO
from matplotlib.figure import Figure
from refnx.reflect import SLD, ReflectModel, Structure
from orsopy.fileio import model_language
from orsopy.slddb import api as slddb_api
from orsopy.slddb import SLDDB, DB_FILE
from orsopy.utils.chemical_formula import Formula

# make sure the material resolution is done locally
slddb_api.use_webquery = False

q = linspace(0.001, 0.4, 400)

def sample_form():
    return render_template('sample.html')

def simulate_reflectivity(xray, neutron, magnetic=None):
    fig = Figure(figsize=(6,8))
    fig.set_facecolor('none')
    ax, ax2 = fig.subplots(nrows=2)

    structure = Structure()
    if magnetic:
        magnetic=magnetic.split('_')
        structure_down = Structure()
    for j, lj in enumerate(neutron.split('_')):
        d, sigma, sldr, sldi = lj.split(';')
        if magnetic:
            m = SLD(float(sldr)+float(magnetic[j])+1j*float(sldi))
            m_down = SLD(float(sldr)-float(magnetic[j])+1j*float(sldi))
            structure_down |= m_down(float(d), float(sigma))
        else:
            m = SLD(float(sldr)+1j*float(sldi))
        structure |= m(float(d), float(sigma))
    model = ReflectModel(structure, bkg=0.0)
    if magnetic:
        model_down = ReflectModel(structure_down, bkg=0.0)
    structurex = Structure()
    for lj in xray.split('_'):
        d, sigma, sldr, sldi = lj.split(';')
        m = SLD(float(sldr)+1j*float(sldi))
        structurex |= m(float(d), float(sigma))
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
    xray = []
    neutron = []
    magnetic = []
    layers = sample.resolve_to_layers()
    for lj in layers:
        nsld = lj.material.get_sld() * 1e6+0j
        print(lj)
        if getattr(lj.material, 'magnetic_moment', None) is not None:
            msld = bM*lj.material.magnetic_moment.as_unit('muB')*lj.material.number_density.as_unit('1/nm^3')*1e4
        else:
            msld = 0.
        magnetic.append(msld)
        neutron.append(f'{lj.thickness.as_unit("angstrom")};{lj.roughness.as_unit("angstrom")};{nsld.real};{nsld.imag}')
        xsld = lj.material.get_sld(xray_energy="Cu") * 1e6 + 0j
        xray.append(f'{lj.thickness.as_unit("angstrom")};{lj.roughness.as_unit("angstrom")};{xsld.real};{xsld.imag}')
    plink += f'xray={"_".join(xray)}&neutron={"_".join(neutron)}'
    if any([msld!=0 for msld in magnetic]):
        plink += f'&magnetic={"_".join([str(msld) for msld in magnetic])}'
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
    if single_layer:
        structure = structure_to_html(sample.resolve_to_layers())
    else:
        structure = structure_to_html(sample.resolve_stack())

    img = create_plot_link(sample)

    slddb_api.db.db.close()
    slddb_api.db=None
    return render_template('sample.html', structure=structure, img=img)

def structure_to_html(items):
    output = ""
    for item in items:
        if isinstance(item, model_language.Layer):
            output+=f'<div class="sample_item">{layer_table(item)}</div>\n'
        elif isinstance(item, model_language.SubStack):
            if item.original_name:
                output += f'<div class="sample_stack">{item.repetitions} x {item.original_name}\n    '
            else:
                output+=f'<div class="sample_stack">{item.repetitions} x Stack\n    '
            output+=structure_to_html(item.sequence).replace('\n', '    \n')
            output+='</div>\n'
    return output

def layer_table(layer:model_language.Layer):
    if layer.material is None:
        layer.generate_material()
    if isinstance(layer.material, model_language.Composit):
        return composite_table(layer)
    output = '<table class="layer">\n'
    layer.material.generate_density()
    material_info = f'{layer.material.comment or "defined values"}<br />'
    for key in ['formula', 'number_density', 'mass_density', 'sld', 'relative_density', 'magnetic_moment']:
        value = getattr(layer.material, key, None)
        if value:
            if hasattr(value, 'magnitude'):
                value = f'{value.magnitude:.3g} {value.unit}'
            elif hasattr(value, 'real') and hasattr(value, 'unit'):
                value = f'{value.real:.3g}+{value.imag:.3g}i {value.unit}'
            material_info+=f'{key} = {value}<br />'

    output += f'<tr><th rowspan="2" class="expand">{layer.original_name or layer.material.original_name or ""}</th><th>material</th><th>d</th><th>σ</th></tr>\n'
    output += f'<tr><td>{getattr(layer.material, "formula", None) or "SLD"} <div class="tooltip">🛈<div class="tooltiptext">' \
              f'{material_info}' \
              f'</div></div></td><td>{layer.thickness.as_unit("nm"):.2f}</td>' \
              f'<td>{layer.roughness.as_unit("nm"):.1f}</td></tr>\n'
    output += '</table>\n'
    return output

def composite_table(layer:model_language.Layer):
    output = '<table class="layer">\n'
    nitems = len(layer.material.composition)

    layer.material.generate_density()
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

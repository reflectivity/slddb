import yaml

from flask import render_template

from numpy import linspace
from io import BytesIO
from matplotlib.figure import Figure
from refnx.reflect import SLD, ReflectModel, Structure
from orsopy.fileio import model_language

q = linspace(0.001, 0.2, 200)

def sample_form():
    return render_template('sample.html')

def simulate_reflectivity(xray, neutron):
    fig = Figure()
    ax = fig.subplots()

    structure = Structure()
    for lj in neutron.split('_'):
        d, sigma, sldr, sldi = lj.split(';')
        m = SLD(float(sldr)+1j*float(sldi))
        structure |= m(float(d), float(sigma))
    model = ReflectModel(structure, bkg=0.0)
    structurex = Structure()
    for lj in xray.split('_'):
        d, sigma, sldr, sldi = lj.split(';')
        m = SLD(float(sldr)+1j*float(sldi))
        structurex |= m(float(d), float(sigma))
    modelx = ReflectModel(structurex, bkg=0.0)
    ax.semilogy(q, model(q), label="neutron")
    ax.semilogy(q, modelx(q), label="x-ray (Cu)")
    ax.legend(loc='lower left')
    ax.set_xlabel("q [Å$^{-1}$]")
    ax.set_ylabel("Reflectivity")

    ax2 = fig.add_axes([0.65, 0.65, 0.27, 0.27])
    ax2.plot([0,1],[0,1])
    ax2.set_ylabel('SLDn')
    ax2.set_xlabel('depth')
    ax2.plot(*structure.sld_profile(), color='C0', label="neutron")
    ax2x=ax2.twinx()
    ax2x.plot(*structurex.sld_profile(), color='C1', label="x-ray (Cu)")
    ax2x.set_ylabel('SLDx')

    # Save it to a temporary buffer.
    buf = BytesIO()
    fig.savefig(buf, format="png")
    return bytes(buf.getbuffer())


def create_plot_link(sample:model_language.SampleModel):
    plink='plot_sample.png?'
    xray = []
    neutron = []
    layers = sample.resolve_to_layers()
    for lj in layers:
        nsld = lj.material.get_sld() * 1e6+0j
        neutron.append(f'{lj.thickness.as_unit("angstrom")};{lj.roughness.as_unit("angstrom")};{nsld.real};{nsld.imag}')
        xsld = lj.material.get_sld(xray_energy="Cu") * 1e6 + 0j
        xray.append(f'{lj.thickness.as_unit("angstrom")};{lj.roughness.as_unit("angstrom")};{xsld.real};{xsld.imag}')
    plink += f'xray={"_".join(xray)}&neutron={"_".join(neutron)}'
    return plink

def sample_form_eval(data_yaml, single_layer=False):
    # parse data as yaml
    data = yaml.safe_load(data_yaml)
    if "data_source" in data:
        data = data["data_source"]
    if "sample" in data:
        data = data["sample"]["model"]
    sample = model_language.SampleModel(**data)
    if single_layer:
        structure = structure_to_html(sample.resolve_to_layers())
    else:
        structure = structure_to_html(sample.resolve_stack())
    img = create_plot_link(sample)
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
    if isinstance(layer.material, model_language.Composit):
        return composite_table(layer)
    output = '<table class="layer">\n'
    if layer.original_name:
        output += f'<tr><th rowspan="2">{layer.original_name}</th><th>material</th><th>d</th><th>σ</th></tr>\n'
    elif layer.material.original_name:
        output += f'<tr><th rowspan="2">{layer.material.original_name}</th><th>material</th><th>d</th><th>σ</th></tr>\n'
    else:
        output += '<tr><th>material</th><th>d</th><th>σ</th></tr>\n'
    output += f'<tr><td>{getattr(layer.material, "formula", None) or "SLD"}</td><td>{layer.thickness.as_unit("nm"):.2f}</td>' \
              f'<td>{layer.roughness.as_unit("nm"):.1f}</td></tr>\n'
    output += '</table>\n'
    return output

def composite_table(layer:model_language.Layer):
    output = '<table class="layer">\n'
    nitems = len(layer.material.composition)
    if layer.original_name:
        output += f'<tr><th rowspan="{nitems+1}">{layer.original_name}</th><th>fraction</th><th>material</th><th>d</th><th>σ</th></tr>\n'
    elif layer.material.original_name:
        output += f'<tr><th rowspan="{nitems+1}">{layer.material.original_name}</th><th>fraction</th><th>material</th><th>d</th><th>σ</th></tr>\n'
    else:
        output += f'<tr><th>material</th><th>fraction</th><th>d</th><th>σ</th></tr>\n'
    for i, (key, fraction) in enumerate(layer.material.composition.items()):
        material = layer.material._composition_materials[key]
        output += f'<tr><td>{getattr(material, "formula", None) or key}</td><td>{fraction*100:.1f}%</td>'
        if i==0:
            output += f'<td rospan="{nitems}">{layer.thickness.as_unit("nm"):.2f}</td>' \
                      f'<td rospan="{nitems}">{layer.roughness.as_unit("nm"):.1f}</td></tr>\n'
        else:
            output += '</tr>\n'

    output += '</table>\n'
    return output

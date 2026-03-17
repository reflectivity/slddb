function updateSlider(slideAmount) {
    var unit = document.getElementById("user_select").value;
    var real_part; var imag_part;
    if (slideAmount<0) {
        slideAmount=document.getElementById("xray_energy_value").value;
        if (can_switch) {
            can_switch=false;
            document.getElementById("cu_select").selectedIndex=document.getElementById("user_select").selectedIndex;
            document.getElementById("mo_select").selectedIndex=document.getElementById("user_select").selectedIndex;
            switch_sld_cu(unit)
            switch_sld_mo(unit)
            can_switch=true;
        }
        }
    if (unit == 'sld') {
        factor=1.0e6;
        real_part=mdata.material_rho_real;
        imag_part=mdata.material_rho_imag;
        plot_image.src=plot_url;
    } else if (unit == 'electron'){
        factor=1.0e5/mdata.r_e;
        real_part=mdata.material_rho_real;
        imag_part=mdata.material_rho_imag;
        plot_image.src=plot_url;
    } else {
        factor=1.0;
        real_part=mdata.material_delta;
        imag_part=mdata.material_beta;
        plot_image.src=plot_url+'&delta=1';
    }

    var factor; var val_real; var val_imag;
    var xval=parseFloat(slideAmount)/1000.0;
    var left = mdata.material_energies.findIndex(ele => ele >= xval);
    var right = left+1;
    var dxleft = mdata.material_energies[left]-xval;
    var dxright = xval-mdata.material_energies[right];
    var dx=dxleft+dxright;
    if (dxleft>0) {
        val_real=real_part[left]*(dxright/dx)+real_part[right]*(dxleft/dx);
        val_imag=imag_part[left]*(dxright/dx)+imag_part[right]*(dxleft/dx);
    } else {
        val_real=real_part[left];
        val_imag=imag_part[left];
    }

    if (unit == 'n_db') {
        document.getElementById("value_real").innerHTML = (val_real).toExponential(3);
        document.getElementById("value_imag").innerHTML = (val_imag).toExponential(3);
    } else {
        document.getElementById("value_real").innerHTML = (val_real*factor).toFixed(5);
        document.getElementById("value_imag").innerHTML = (val_imag*factor).toFixed(5)+'i';
    }

    document.getElementById("xray_energy_value").value = slideAmount;
}

function updateValue() {
    const value = document.getElementById("xray_energy_value").value;
    document.getElementById("xray_energy").value = value;
    updateSlider(value);
}

function copy_all() {
    var out = '';
    out=out.concat('Compound', '\t', mdata.material_name, '\n');
    out=out.concat('Description', '\t', mdata.material_description, '\n');
    out=out.concat('Chemical Formula', '\t', mdata.chemical_formula, '\n');

    var dens_select=document.getElementById("densresult")
    out=out.concat(dens_select.options[dens_select.selectedIndex].text, '\t',
                    document.getElementById("density_value").innerHTML, '\n');

    out=out.concat('Neutron nuclear SLD (10⁻⁶ Å⁻²)',
                    '\t', document.getElementById("neutron_entry_real").innerHTML,
                    '\t', document.getElementById("neutron_entry_imag").innerHTML, '\n');
    if (mdata.material_rho_m!=0) {
        var magn_select=document.getElementById("magnresult")
        out=out.concat(magn_select.options[magn_select.selectedIndex].text, '\t', mdata.material_rho_m, '\n');
        }

    var xray_select=document.getElementById("cu_select");
    var xray_unit=xray_select.options[xray_select.selectedIndex].text
    out=out.concat(`Cu-Kɑ ${xray_unit}`,
                    '\t', document.getElementById("cu_entry_real").innerHTML,
                    '\t', document.getElementById("cu_entry_imag").innerHTML, '\n');
    out=out.concat(`Mo-Kɑ SLD ${xray_unit}`,
                    '\t', document.getElementById("mo_entry_real").innerHTML,
                    '\t', document.getElementById("mo_entry_imag").innerHTML, '\n');
    out=out.concat(`Custom (${document.getElementById("xray_energy_value").value} eV) ${xray_unit}`,
                    '\t', document.getElementById("value_real").innerHTML,
                    '\t', document.getElementById("value_imag").innerHTML, '\n');

    navigator.clipboard.writeText(out);
}

function copy_NSLD() {
    const value_real=document.getElementById("neutron_entry_real").innerHTML;
    const value_imag=document.getElementById("neutron_entry_imag").innerHTML;

    navigator.clipboard.writeText(`${value_real}\t${value_imag}`);
}
function copy_Nmag() {
    navigator.clipboard.writeText(`${material_neutron_magn.toFixed(6)}`);
}
function copy_Cu() {
    const value_real=document.getElementById("cu_entry_real").innerHTML;
    const value_imag=document.getElementById("cu_entry_imag").innerHTML;
    var unit = document.getElementById("cu_select").value;
    if (unit == 'n_db') {
    navigator.clipboard.writeText(`${value_real}\t${value_imag}`);
    } else {
    navigator.clipboard.writeText(`${value_real}+${value_imag}`.replace('+-', '-'));
    }
}
function copy_Mo() {
    const value_real=document.getElementById("mo_entry_real").innerHTML;
    const value_imag=document.getElementById("mo_entry_imag").innerHTML;
    var unit = document.getElementById("mo_select").value;
    if (unit == 'n_db') {
    navigator.clipboard.writeText(`${value_real}\t${value_imag}`);
    } else {
    navigator.clipboard.writeText(`${value_real}+${value_imag}`.replace('+-', '-'));
    }
}
function copy_xE() {
    var unit = document.getElementById("user_select").value;
    var factor;
    if (unit == 'sld') {
        var out = 'E (kev)\tSLD real\tSLD imag\n';
        factor=1.0e6;
        real_part=mdata.material_rho_real;
        imag_part=mdata.material_rho_imag;
    } else if (unit == 'electron'){
        var out = 'E (kev)\te-dens real\te-dens imag\n';
        factor=1.0e5/mdata.r_e;
        real_part=mdata.material_rho_real;
        imag_part=mdata.material_rho_imag;
    } else {
        var out = 'E (kev)\tdelta\tbeta\n';
        factor=1.0;
        real_part=mdata.material_delta;
        imag_part=mdata.material_beta;
    }

    for (let i = 0; i < mdata.material_energies.length; i++) {
      out+=`${mdata.material_energies[i]}\t${factor*real_part[i]}\t${factor*imag_part[i]}\n`;
    }

    const SLD_real=document.getElementById("value_real").innerHTML;
    const SLD_imag=document.getElementById("value_imag").innerHTML;
    navigator.clipboard.writeText(out);
}
function copy_xray() {
    const SLD_real=document.getElementById("value_real").innerHTML;
    const SLD_imag=document.getElementById("value_imag").innerHTML;
    var unit = document.getElementById("user_select").value;
    if (unit == 'n_db') {
    navigator.clipboard.writeText(`${SLD_real}\t${SLD_imag}`);
    } else {
    navigator.clipboard.writeText(`${SLD_real}+${SLD_imag}`.replace('+-', '-'));
    }
}

function switch_density() {
    var selection = document.getElementById("densresult").value;
    if (selection == 'density') {document.getElementById("density_value").innerHTML = mdata.material_dens.toFixed(6);}
    if (selection == 'FUdens') {document.getElementById("density_value").innerHTML = mdata.material_fu_dens.toFixed(8);}
    if (selection == 'FUdnm') {document.getElementById("density_value").innerHTML = (mdata.material_fu_dens*1e3).toFixed(5);}
    if (selection == 'volume') {document.getElementById("density_value").innerHTML = mdata.material_fu_volume.toFixed(5);}
}

var can_switch=true;
function switch_sld_cu(selection) {
    if (selection == 'electron') {
        document.getElementById("cu_entry_real").innerHTML = mdata.material_cu_real.toFixed(5);
        document.getElementById("cu_entry_imag").innerHTML = `${mdata.material_cu_imag.toFixed(5)}i`;
//        {% if material.ID %}
//        document.getElementById("download_link").href = '{{url_for('api_download', ID=material.ID, xray_unit='edens')|safe}}';
//        {% endif %}
        } else if (selection == 'sld') {
        document.getElementById("cu_entry_real").innerHTML = mdata.material_sld_cu_real.toFixed(5);
        document.getElementById("cu_entry_imag").innerHTML = `${mdata.material_sld_cu_imag.toFixed(5)}i`;
//        {% if material.ID %}
//        document.getElementById("download_link").href = '{{url_for('api_download', ID=material.ID, xray_unit='sld')|safe}}';
//        {% endif %}
        } else if (selection == 'n_db') {
        document.getElementById("cu_entry_real").innerHTML = mdata.material_cu_delta.toExponential(3);
        document.getElementById("cu_entry_imag").innerHTML = mdata.material_cu_beta.toExponential(3);
//        {% if material.ID %}
//        document.getElementById("download_link").href = '{{url_for('api_download', ID=material.ID, xray_unit='n_db')|safe}}';
//        {% endif %}
        }
    if (can_switch) {
        can_switch=false;
        document.getElementById("mo_select").selectedIndex=document.getElementById("cu_select").selectedIndex;
        switch_sld_mo(selection)
        document.getElementById("user_select").selectedIndex=document.getElementById("cu_select").selectedIndex;
        updateSlider(-1)
        can_switch=true;
    }
}

function switch_sld_mo(selection) {
    if (selection == 'electron') {
        document.getElementById("mo_entry_real").innerHTML = mdata.material_mo_real.toFixed(5);
        document.getElementById("mo_entry_imag").innerHTML = `${mdata.material_mo_imag.toFixed(5)}i`;
        } else if (selection == 'sld') {
        document.getElementById("mo_entry_real").innerHTML = mdata.material_sld_mo_real.toFixed(5);
        document.getElementById("mo_entry_imag").innerHTML = `${mdata.material_sld_mo_imag.toFixed(5)}i`;
        } else if (selection == 'n_db') {
        document.getElementById("mo_entry_real").innerHTML = mdata.material_mo_delta.toExponential(3);
        document.getElementById("mo_entry_imag").innerHTML = mdata.material_mo_beta.toExponential(3);
        }
    if (can_switch) {
        can_switch=false;
        document.getElementById("cu_select").selectedIndex=document.getElementById("mo_select").selectedIndex;
        switch_sld_cu(selection)
        document.getElementById("user_select").selectedIndex=document.getElementById("mo_select").selectedIndex;
        updateSlider(-1)
        can_switch=true;
    }
}

function switch_magn() {
    var selection = document.getElementById("magnresult").value;
    var material_neutron_magn=0.;
    if (selection == 'msld') {material_neutron_magn= mdata.material_rho_m;}
    if (selection == 'muB') {material_neutron_magn=mdata.material_mu;}
    if (selection == 'magn') {material_neutron_magn=mdata.material_m;}
    document.getElementById("magn_value").innerHTML = material_neutron_magn.toFixed(6);
}

const plot_image=document.getElementById("xray_image");
const plot_url=plot_image.src;

// setup the vairables
var mdata = {};
pref_form=document.getElementById("preferences");
pref_form.onkeydown=function(event){return event.key != 'Enter'};
for( var d in pref_form.dataset) {
    try{mdata[d]=JSON.parse(pref_form.dataset[d]);}
    catch (SyntaxError) {mdata[d]=pref_form.dataset[d]}
}

// connect actions
document.getElementById("densresult").onchange=switch_density;

if (mdata.material_rho_m!=0){document.getElementById("magnresult").onchange=switch_magn;}
document.getElementById("cu_select").onchange=function() {switch_sld_cu(document.getElementById("cu_select").value)};
document.getElementById("mo_select").onchange=function() {switch_sld_mo(document.getElementById("mo_select").value)};
document.getElementById("user_select").onchange=function() {updateSlider(-1)};
document.getElementById("xray_energy").onchange=function() {updateSlider(document.getElementById("xray_energy").value)};
document.getElementById("xray_energy_value").onchange=function() {updateValue(document.getElementById("xray_energy_value").value)};
document.getElementById("xray_energy_value").onkeyup=function(event) {if (event.key=='Enter')
            {updateValue(document.getElementById("xray_energy_value").value)}};

document.getElementById("copy_all_button").onclick=copy_all;
document.getElementById("copy_xe_button").onclick=copy_xE;

// user preferences from cookies
if (mdata.user_densresult!='') {
    document.getElementById("densresult").value=mdata.user_densresult;
    switch_density();
}
if (mdata.user_magnresult!='' & mdata.material_rho_m!=0) {
    document.getElementById("magnresult").value=mdata.user_magnresult;
    switch_magn();
}
if (mdata.user_cu_select!='') {
    document.getElementById("cu_select").value=mdata.user_cu_select;
    switch_sld_cu(mdata.user_cu_select);
}

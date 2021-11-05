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
    } else if (unit == 'electron'){
        factor=1.0e5/mdata.r_e;
        real_part=mdata.material_rho_real;
        imag_part=mdata.material_rho_imag;
    } else {
        factor=1.0;
        real_part=mdata.material_delta;
        imag_part=mdata.material_beta;
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
        document.getElementById("value_real").innerHTML = (val_real).toExponential(4);
        document.getElementById("value_imag").innerHTML = (val_imag).toExponential(4);
    } else {
        document.getElementById("value_real").innerHTML = (val_real*factor).toFixed(6);
        document.getElementById("value_imag").innerHTML = (val_imag*factor).toFixed(6)+'i';
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
    out=out.concat('Compound', '\t', material_name, '\n');
    out=out.concat('Description', '\t', material_description, '\n');
    out=out.concat('Chemical Formula', '\t', chemical_formula, '\n');

    var dens_select=document.getElementById("densresult")
    out=out.concat(dens_select.options[dens_select.selectedIndex].text, '\t',
                    document.getElementById("density_value").innerHTML, '\n');

    out=out.concat('Neutron nuclear SLD (10⁻⁶ Å⁻²)',
                    '\t', document.getElementById("neutron_entry_real").innerHTML,
                    '\t', document.getElementById("neutron_entry_imag").innerHTML, '\n');
    if (material_neutron_magn!=0) {
    var magn_select=document.getElementById("magnresult")
    out=out.concat(magn_select.options[magn_select.selectedIndex].text, '\t', material_neutron_magn, '\n');}

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
        factor=1.0e6;
        real_part=material_rho_real;
        imag_part=material_rho_imag;
    } else if (unit == 'electron'){
        factor=1.0e5/r_e;
        real_part=material_rho_real;
        imag_part=material_rho_imag;
    } else {
        factor=1.0;
        real_part=material_delta;
        imag_part=material_beta;
    }

    var out = 'E (kev)\treal\timag\n';
    for (let i = 0; i < material_energies.length; i++) {
      out+=`${material_energies[i]}\t${factor*real_part[i]}\t${factor*imag_part[i]}\n`;
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
        document.getElementById("cu_entry_real").innerHTML = mdata.material_sld_cu_real;
        document.getElementById("cu_entry_imag").innerHTML = `${mdata.material_sld_cu_real}i`;
//        {% if material.ID %}
//        document.getElementById("download_link").href = '{{url_for('api_download', ID=material.ID, xray_unit='edens')|safe}}';
//        {% endif %}
        } else if (selection == 'sld') {
        document.getElementById("cu_entry_real").innerHTML = '{{"%.6f"%(1e6*material.rho_of_E(Cu_kalpha).real)}}';
        document.getElementById("cu_entry_imag").innerHTML = '{{"%.6f"%(1e6*material.rho_of_E(Cu_kalpha).imag)}}i';
//        {% if material.ID %}
//        document.getElementById("download_link").href = '{{url_for('api_download', ID=material.ID, xray_unit='sld')|safe}}';
//        {% endif %}
        } else if (selection == 'n_db') {
        document.getElementById("cu_entry_real").innerHTML = '{{"%.4e"%(material.delta_of_E(Cu_kalpha))}}';
        document.getElementById("cu_entry_imag").innerHTML = '{{"%.4e"%(material.beta_of_E(Cu_kalpha))}}';
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
        document.getElementById("mo_entry_real").innerHTML = '{{"%.6f"%(material.rho_of_E(Mo_kalpha).real/r_e_angstrom)}}';
        document.getElementById("mo_entry_imag").innerHTML = '{{"%.6f"%(material.rho_of_E(Mo_kalpha).imag/r_e_angstrom)}}i';
        } else if (selection == 'sld') {
        document.getElementById("mo_entry_real").innerHTML = '{{"%.6f"%(1e6*material.rho_of_E(Mo_kalpha).real)}}';
        document.getElementById("mo_entry_imag").innerHTML = '{{"%.6f"%(1e6*material.rho_of_E(Mo_kalpha).imag)}}i';
        } else if (selection == 'n_db') {
        document.getElementById("mo_entry_real").innerHTML = '{{"%.4e"%(material.delta_of_E(Mo_kalpha))}}';
        document.getElementById("mo_entry_imag").innerHTML = '{{"%.4e"%(material.beta_of_E(Mo_kalpha))}}';
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
//    if (selection == 'msld') {material_neutron_magn={{1e6*material.rho_m}};}
//    if (selection == 'muB') {material_neutron_magn={{material.mu}};}
//    if (selection == 'magn') {material_neutron_magn={{material.M}};}
//    document.getElementById("magn_value").innerHTML = material_neutron_magn.toFixed(6);
}


// setup the vairables
var mdata = {};
pref_form=document.getElementById("preferences");
pref_form.onkeydown=function(event){return event.key != 'Enter'};
for( var d in pref_form.dataset) {
    try{mdata[d]=JSON.parse(pref_form.dataset[d]);}
    catch (SyntaxError) {mdata[d]=pref_form.dataset[d]}
}
console.log(mdata)

// connect actions
document.getElementById("densresult").onchange=switch_density;
//document.getElementById("deuteration_amount").onchange=function() {deuterateSlider(document.getElementById("deuteration_amount").value)};
//document.getElementById("deuteration_amount_value").onchange=function() {deuterateValue(document.getElementById("deuteration_amount_value").value)};
//document.getElementById("deuteration_amount_value").onkeyup=function(event) {if (event.key=='Enter') {deuterateValue(document.getElementById("deuteration_amount_value").value)}};
//document.getElementById("exchange_amount").onchange=function() {deuterateSlider(document.getElementById("exchange_amount").value)};
//document.getElementById("exchange_amount_value").onchange=function() {deuterateValue(document.getElementById("exchange_amount_value").value)};
//document.getElementById("exchange_amount_value").onkeyup=function(event) {if (event.key=='Enter') {deuterateValue(document.getElementById("exchange_amount_value").value)}};
//document.getElementById("d2o_amount").onchange=function() {deuterateSlider(document.getElementById("d2o_amount").value)};
//document.getElementById("d2o_amount_value").onchange=function() {deuterateValue(document.getElementById("d2o_amount_value").value)};
//document.getElementById("d2o_amount_value").onkeyup=function(event) {if (event.key=='Enter') {deuterateValue(document.getElementById("d2o_amount_value").value)}};

if (mdata.material_neutron_magn!=0){document.getElementById("magnresult").onchange=switch_magn;}
document.getElementById("cu_select").onchange=function() {switch_sld_cu(document.getElementById("cu_select").value)};
document.getElementById("mo_select").onchange=function() {switch_sld_mo(document.getElementById("mo_select").value)};
document.getElementById("user_select").onchange=function() {updateSlider(-1)};
document.getElementById("xray_energy").onchange=function() {updateSlider(document.getElementById("xray_energy").value)};
document.getElementById("xray_energy_value").onchange=function() {updateValue(document.getElementById("xray_energy_value").value)};

document.getElementById("copy_all_button").onchange=copy_all;
document.getElementById("copy_xe_button").onchange=copy_xE;

var but_coll  = document.getElementsByClassName("collapsible")[0];
if (typeof but_coll !== 'undefined') {
    but_coll.addEventListener("click", toggleImageXrayNeutron);
}

// user preferences from cookies
if (mdata.items_collapsed=='true') {but_coll.click();}
if (mdata.user_densresult!='') {
    document.getElementById("densresult").value=mdata.user_densresult;
    switch_density();
}
if (mdata.user_magnresult!='' & mdata.material_neutron_magn!=0) {
    document.getElementById("magnresult").value=mdata.user_magnresult;
    switch_magn();
}
if (mdata.user_cu_select!='') {
    document.getElementById("cu_select").value=mdata.user_cu_select;
    switch_sld_cu(mdata.user_cu_select);
}

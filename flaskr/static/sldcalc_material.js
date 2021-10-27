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

    var factor; var val_real; var val_imag;
    var xval=parseFloat(slideAmount)/1000.0;
    var left = material_energies.findIndex(ele => ele >= xval);
    var right = left+1;
    var dxleft = material_energies[left]-xval;
    var dxright = xval-material_energies[right];
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

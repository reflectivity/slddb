function deuterateSlider(slideAmount) {
    frac=slideAmount*0.01;

    var val_real=(1.0-frac)*mdata.material_neutron_real+frac*mdata.deuterated_neutron_real;
    var val_imag=(1.0-frac)*mdata.material_neutron_imag+frac*mdata.deuterated_neutron_imag;

    document.getElementById("neutron_entry_real").innerHTML = (val_real).toFixed(5);
    document.getElementById("neutron_entry_imag").innerHTML = (val_imag).toFixed(5)+'i';

    document.getElementById("deuteration_amount_value").value = slideAmount;

    if (document.getElementById("densresult").value == 'density') {
        material_dens = ((1.0-frac)*mdata.hydrogenated_density + frac*mdata.deuterated_density).toFixed(6);
        document.getElementById("density_value").innerHTML = material_dens;
    }
}

function deuterateValue() {
    const value = document.getElementById("deuteration_amount_value").value;
    document.getElementById("deuteration_amount").value = value;
    deuterateSlider(value);
}

//extend mdata dictionary from sldcalc_material
entry_data=document.getElementById("deuteration_amount");
for( var d in entry_data.dataset) {
    try{mdata[d]=JSON.parse(entry_data.dataset[d]);}
    catch (SyntaxError) {mdata[d]=entry_data.dataset[d]}
}


document.getElementById("deuteration_amount").onchange=function() {deuterateSlider(document.getElementById("deuteration_amount").value)};
document.getElementById("deuteration_amount_value").onchange=deuterateValue;
document.getElementById("deuteration_amount_value").onkeyup=function(event) {if (event.key=='Enter') {deuterateValue()}};

var but_coll  = document.getElementsByClassName("collapsible")[0];

but_coll.addEventListener("click", toggleImageXrayNeutron);

// user preferences from cookies
if (document.getElementsByName("items_collapsed")[0].value=='true') {but_coll.click();}

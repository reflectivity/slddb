var h2o_sld_real = -0.55992;
var d2o_sld_real = 6.39978;

function updateNSLD() {
    frac_deuterated=document.getElementById("deuteration_amount_value").value*0.01;
    frac_exchange=document.getElementById("exchange_amount_value").value*0.01;
    frac_d2o=document.getElementById("d2o_amount_value").value*0.01;

    // SLD for material with no exchange
    var val_hd_real=(1.0-frac_deuterated)*mdata.material_neutron_real+
                    frac_deuterated*mdata.deuterated_neutron_real;
    var val_hd_imag=(1.0-frac_deuterated)*mdata.material_neutron_imag+
                    frac_deuterated*mdata.deuterated_neutron_imag;
    var val_hd_dens=(1.0-frac_deuterated)*mdata.hydrogenated_density+
                    frac_deuterated*mdata.deuterated_density;

    // SLD for full H2O and D2O exchange
    var val_exH_real=val_hd_real-frac_deuterated*mdata.exchanged_diff_real;
    var val_exH_imag=val_hd_imag-frac_deuterated*mdata.exchanged_diff_imag;
    var val_exD_real=val_hd_real+(1.0-frac_deuterated)*mdata.exchanged_diff_real;
    var val_exD_imag=val_hd_imag+(1.0-frac_deuterated)*mdata.exchanged_diff_imag;
    var val_exH_dens=val_hd_dens-frac_deuterated*mdata.exchanged_diff_density;
    var val_exD_dens=val_hd_dens+(1.0-frac_deuterated)*mdata.exchanged_diff_density;

    // SLD for partial exchanged system with full H2O/D2O
    var val_mH_real=(1.0-frac_exchange)*val_hd_real+frac_exchange*val_exH_real;
    var val_mH_imag=(1.0-frac_exchange)*val_hd_imag+frac_exchange*val_exH_imag;
    var val_mD_real=(1.0-frac_exchange)*val_hd_real+frac_exchange*val_exD_real;
    var val_mD_imag=(1.0-frac_exchange)*val_hd_imag+frac_exchange*val_exD_imag;
    var val_mH_dens=(1.0-frac_exchange)*val_hd_dens+frac_exchange*val_exH_dens;
    var val_mD_dens=(1.0-frac_exchange)*val_hd_dens+frac_exchange*val_exD_dens;

    // Mix exchanged materials
    var val_real=(1.0-frac_d2o)*val_mH_real+frac_d2o*val_mD_real;
    var val_imag=(1.0-frac_d2o)*val_mH_imag+frac_d2o*val_mD_imag;
    var val_dens=(1.0-frac_d2o)*val_mH_dens+frac_d2o*val_mD_dens;

    // Calculate new match point
    var val_match=100.0*(h2o_sld_real-val_mH_real)/
                        (val_mD_real+h2o_sld_real-val_mH_real-d2o_sld_real);

    document.getElementById("neutron_entry_real").innerHTML = (val_real).toFixed(5);
    document.getElementById("neutron_entry_imag").innerHTML = (val_imag).toFixed(5)+'i';
    document.getElementById("match_point_value").innerHTML = (val_match).toFixed(2)+' % D<sub>2</sub>O';


    if (document.getElementById("densresult").value == 'density') {
        document.getElementById("density_value").innerHTML = (val_dens).toFixed(6);
    }
}

function deuterateSlider(slideAmount) {
    document.getElementById("deuteration_amount_value").value = slideAmount;
    updateNSLD();
}

function deuterateValue() {
    const value = document.getElementById("deuteration_amount_value").value;
    document.getElementById("deuteration_amount").value = value;
    deuterateSlider(value);
}
function exchangeSlider(slideAmount) {
    document.getElementById("exchange_amount_value").value = slideAmount;
    updateNSLD();
}

function exchangeValue() {
    const value = document.getElementById("exchange_amount_value").value;
    document.getElementById("exchange_amount").value = value;
    exchangeSlider(value);
}
function d2oSlider(slideAmount) {
    document.getElementById("d2o_amount_value").value = slideAmount;
    updateNSLD();
}

function d2oValue() {
    const value = document.getElementById("d2o_amount_value").value;
    document.getElementById("d2o_amount").value = value;
    d2oSlider(value);
}

//extend mdata dictionary from sldcalc_material
entry_data=document.getElementById("deuteration_amount");
for( var d in entry_data.dataset) {
    try{mdata[d]=JSON.parse(entry_data.dataset[d]);}
    catch (SyntaxError) {mdata[d]=entry_data.dataset[d]}
}
entry_data=document.getElementById("exchange_amount");
for( var d in entry_data.dataset) {
    try{mdata[d]=JSON.parse(entry_data.dataset[d]);}
    catch (SyntaxError) {mdata[d]=entry_data.dataset[d]}
}

document.getElementById("deuteration_amount").onchange=function() {deuterateSlider(document.getElementById("deuteration_amount").value)};
document.getElementById("deuteration_amount_value").onchange=deuterateValue;
document.getElementById("deuteration_amount_value").onkeyup=function(event) {if (event.key=='Enter') {deuterateValue()}};

document.getElementById("exchange_amount").onchange=function() {exchangeSlider(document.getElementById("exchange_amount").value)};
document.getElementById("exchange_amount_value").onchange=exchangeValue;
document.getElementById("exchange_amount_value").onkeyup=function(event) {if (event.key=='Enter') {exchangeValue()}};
document.getElementById("d2o_amount").onchange=function() {d2oSlider(document.getElementById("d2o_amount").value)};
document.getElementById("d2o_amount_value").onchange=d2oValue;
document.getElementById("d2o_amount_value").onkeyup=function(event) {if (event.key=='Enter') {d2oValue()}};


var but_coll  = document.getElementsByClassName("collapsible")[0];

but_coll.addEventListener("click", toggleImageXrayNeutron);

// user preferences from cookies
if (document.getElementsByName("items_collapsed")[0].value=='true') {but_coll.click();}

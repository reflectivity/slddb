    function deuterateSlider(slideAmount) {
        frac=slideAmount*0.01;

        var val_real=(1.0-frac)*material_neutron_real+frac*deuterated_neutron_real;
        var val_imag=(1.0-frac)*material_neutron_imag+frac*deuterated_neutron_imag;

        document.getElementById("neutron_entry_real").innerHTML = (val_real).toFixed(5);
        document.getElementById("neutron_entry_imag").innerHTML = (val_imag).toFixed(5)+'i';

        document.getElementById("deuteration_amount_value").value = slideAmount;

        if (document.getElementById("densresult").value == 'density') {
            material_dens = ((1.0-frac)*hydrogenated_density + frac*deuterated_density).toFixed(4);
            document.getElementById("density_value").innerHTML = material_dens;
        }
    }

    function deuterateValue() {
        const value = document.getElementById("deuteration_amount_value").value;
        document.getElementById("deuteration_amount").value = value;
        deuterateSlider(value);
    }

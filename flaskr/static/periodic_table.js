function show_element(element) {
    document.getElementById("ElementDisplay").style.display = 'block';
    document.getElementById("ElementSymbol").innerHTML = ele_names[element];
    document.getElementById("ElementSymbol").style.background = `radial-gradient(circle, rgba(${ele_colors[element][0]},${ele_colors[element][1]},${ele_colors[element][2]},1) 0%, #ffffff 100%)`;
    document.getElementById("ElementName").innerHTML = ele_fullnames[element];
    document.getElementById("ElementCharge").innerHTML = element.toString();
    if (ele_weight.hasOwnProperty(element)) {
        document.getElementById("ElementWeigth").innerHTML = ele_weight[element].toFixed(2);
    } else {
        document.getElementById("ElementWeigth").innerHTML = 'unknown';
    }
    if (ele_b.hasOwnProperty(element)) {
        document.getElementById("ElementB").innerHTML = ele_b[element];
    } else {
        document.getElementById("ElementB").innerHTML = 'unknown';
    }
    if (ele_f.hasOwnProperty(element)) {
        document.getElementById("ElementF").innerHTML = ele_f[element];
    } else {
        document.getElementById("ElementF").innerHTML = 'unknown';
    }
    if (ele_fMo.hasOwnProperty(element)) {
        document.getElementById("ElementFMo").innerHTML = ele_fMo[element];
    } else {
        document.getElementById("ElementFMo").innerHTML = 'unknown';
    }
    document.getElementById("ElementDisplay").style.backgroundColor = '#ffffff';
}

function copy_element(element){
    var out = '';
        out=out.concat(ele_fullnames[element], '(', ele_names[element], '):\n');
        out=out.concat('Z=', element.toString(), '\n');
        if (ele_weight.hasOwnProperty(element)) {
            out=out.concat('weight=', ele_weight[element].toFixed(1), '\n');
        }
        if (ele_b.hasOwnProperty(element)) {
            out=out.concat('b-neutron=',  ele_b[element], '\n');
        }
        if (ele_f.hasOwnProperty(element)) {
            out=out.concat('f-xray Cu=',  ele_f[element], '\n');
        }
        if (ele_fMo.hasOwnProperty(element)) {
            out=out.concat('f-xray Mo=',  ele_fMo[element], '\n');
        }
    navigator.clipboard.writeText(out);
    document.getElementById("ElementDisplay").style.backgroundColor = '#eeeeee';
}

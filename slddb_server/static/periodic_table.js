function show_element(element) {
    document.getElementById("ElementDisplay").style.display = 'block';
    document.getElementById("ElementSymbol").innerHTML = element.dataset.name;
    rgb=JSON.parse(element.dataset.elementcolor);
    rgb_low=[(rgb[0]*0.8).toFixed(), (rgb[1]*0.8).toFixed(), (rgb[2]*0.8).toFixed()]
    document.getElementById("ElementSymbol").style.background =
      `radial-gradient(circle, rgba(${rgb[0]}, ${rgb[1]}, ${rgb[2]}, 1) 0%, rgba(${rgb_low[0]}, ${rgb_low[1]}, ${rgb_low[2]}, 1))`;
    document.getElementById("ElementName").innerHTML = element.dataset.fullname;
    document.getElementById("ElementCharge").innerHTML = element.dataset.z;
    document.getElementById("ElementWeight").innerHTML = parseFloat(element.dataset.weight).toFixed(2);
    document.getElementById("ElementB").innerHTML = element.dataset.b;
    document.getElementById("ElementF").innerHTML = element.dataset.fcu;
    document.getElementById("ElementFMo").innerHTML = element.dataset.fmo;
    document.getElementById("ElementDisplay").style.backgroundColor = '#ffffff';
}

function copy_element(element){
    var out = '';
        out=out.concat(element.dataset.fullname, '(', element.dataset.name, '):\n');
        out=out.concat('Z=', element.dataset.z, '\n');
        out=out.concat('weight=', element.dataset.weight, '\n');
        out=out.concat('b-neutron=',  element.dataset.b, '\n');
        out=out.concat('f-xray Cu=',  element.dataset.fcu, '\n');
        out=out.concat('f-xray Mo=',  element.dataset.fmo, '\n');
    navigator.clipboard.writeText(out);
    document.getElementById("ElementDisplay").style.backgroundColor = '#eeeeee';
}

function set_element_config(element){
    // set background color according to data attribute
    rgb=JSON.parse(element.dataset.color);
    rgb_low=[(rgb[0]*0.8).toFixed(), (rgb[1]*0.8).toFixed(), (rgb[2]*0.8).toFixed()]
    element.style.background= `radial-gradient(circle, rgba(${rgb[0]}, ${rgb[1]}, ${rgb[2]}, 1) 0%, rgba(${rgb_low[0]}, ${rgb_low[1]}, ${rgb_low[2]}, 1))`;

    element.onmouseover=function() {show_element(element);};
    element.onclick=function() {copy_element(element);};
    element.ondblclick=function() {window.open(element.dataset.url, '_self');};
}

elements=document.getElementsByClassName('actual_element')
for (var i=0; i<elements.length; i++) {
    set_element_config(elements[i]);
}

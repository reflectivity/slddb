elements=document.getElementsByClassName('clear_field')
for (var i=0; i<elements.length; i++) {
   var element=elements[i];
   element.onclick=function() {document.getElementById(`compound ${element.dataset.field}`).selectedIndex=-1;};
}

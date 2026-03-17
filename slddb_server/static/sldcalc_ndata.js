var but_coll  = document.getElementsByClassName("collapsible")[0];

but_coll.addEventListener("click", toggleImageXrayNeutron);

// user preferences from cookies
if (document.getElementsByName("items_collapsed")[0].value=='true') {but_coll.click();}

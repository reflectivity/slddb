var but_coll  = document.getElementsByClassName("collapsible")[0];

but_coll.addEventListener("click", function() {
    this.classList.toggle("active");
    var coll_itms = document.getElementsByClassName("collapsed");
    for (var i = 0; i < coll_itms.length; i++) {
      var content = coll_itms[i];
      if (content.style.display == "table-cell") {
        content.style.display = "none";
      } else {
        content.style.display = "table-cell";
      }
    }
});

const collapse_button = document.getElementById("collapse_button")
if (collapse_button.dataset.shown=="true") {
    var coll_itms = document.getElementsByClassName("collapsed");
    for (var i = 0; i < coll_itms.length; i++) {
           var content = coll_itms[i];
           content.style.display = "table-cell";
    }
}
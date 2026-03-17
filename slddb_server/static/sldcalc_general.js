function toggleImageXrayNeutron() {
    var added = this.classList.toggle("active");
    document.getElementsByName("items_collapsed")[0].value=added;
    var coll_itms = document.getElementsByClassName("collapsed");
    for (var i = 0; i < coll_itms.length; i++) {
      var content = coll_itms[i];
      if (content.style.display === "table-cell") {
        content.style.display = "none";
      } else {
        content.style.display = "table-cell";
      }}
    var uncoll_itms = document.getElementsByClassName("uncollapsed");
    for (var i = 0; i < uncoll_itms.length; i++) {
      var content = uncoll_itms[i];
      if (content.style.display === "none") {
        content.style.display = "table-cell";
      } else {
        content.style.display = "none";
      }
    }
}
const example_select = document.getElementById("example_scripts");
const yaml_text_entry = document.getElementById("sample_yaml");

for (let name in example_yaml_scripts) {
    example_select.add(new Option(name, name),undefined);
}

function example_selected() {
    name = example_select.value;
    if (name==="empty") {
         editor.setValue('');
    } else {
        text = example_yaml_scripts[name];
        editor.setValue(text);
        editor.clearSelection()
        example_select.value = "empty";
    }
};

example_select.addEventListener("change", example_selected);

var editor = ace.edit("editor");
editor.setTheme("ace/theme/eclipse");
editor.renderer.setShowGutter(false);
editor.setOption("useSoftTabs", true);
editor.session.setTabSize(2);
editor.session.setMode("ace/mode/yaml");

function store_before_submit() {
    document.getElementById("sample_yaml").value = editor.getValue();
}

document.getElementById("submit_yaml").addEventListener("submit", store_before_submit);
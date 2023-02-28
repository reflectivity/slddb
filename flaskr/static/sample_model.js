var example_yaml_scripts = {
  "minimal sample": `stack: vacuum | Au 10 | Pt 20 | Si`,
  "explicit layers": `stack: ambient | layer1 | layer2 | substrate
layers:
  ambient:
    material: air
  layer1:
    material: Au
    thickness: 10.0
  layer2:
    material: Pt
    thickness: 20.0
  substrate:
    material: Si`,
  "explicit materials": `stack: ambient | gold 10 | platinum 20 | silicon
materials:
  ambient:
    sld: 0.0
  gold:
    formula: Au
    mass_density: 19.32
  platinum:
    formula: Pt
    mass_density: 21.45
  silicon:
    formula: Si
    mass_density: 2.329`,
  "orsopy 1 - simple multilayer": `stack: air | 10 ( Si 7 | Fe 7 ) | Si`,
  "orsopy 2 - materials and globals": `origin: guess based on preparation / XRR
stack: air | 10 ( Si 70 | Fe 70 ) | Si
materials:
  Fe:
    magnetic_moment: 2.2
  Si:
    formula: SiN0.01
    relative_density: 0.95
globals:
  length_unit: angstrom
  m_moment_unit: muB
  roughness: {magnitude: 5.0, unit: angstrom}
  sld_unit: 1/angstrom^2`,
  "orsopy 3 - group by sub-stacks": `stack: substrate | film | water
sub_stacks:
  substrate:
    sequence:
    - material: Si
      roughness: 2
    - material: SiO2
      thickness: 5
      roughness: 3
  film:
    repetitions: 5
    stack: head_group 4 | tail | tail | head_group 4
layers:
  tail:
    material: tailstuff
    thickness: 22.
materials:
  head_group:
    sld: 0.2E-06
  tailstuff:
    formula: CH2
    mass_density: 1.2
  SiO2:
    formula: SiO2
    mass_density: 2.5
  Si:
    formula: Si
    mass_density: 2.33
composits:
  water:
    composition:
      H2O: 0.3
      D2O: 0.7
globals:
  roughness: {magnitude: 5, unit: angstrom}
  length_unit: angstrom
  mass_density_unit: g/cm^3
  sld_unit: 1/angstrom^2`,
  "orsopy 4 - representing refNX class": `stack: Si | LL | rLL | D2O
sub_stacks:
    LL:
        sequence:
        - material: {sld: 1.88401254e-06}
          thickness: 9.0
          roughness: 3.0
        - material: {sld: -3.73401535e-07}
          thickness: 1.4
          roughness: 3.0
        represents:  refnx.reflect.LipidLeaflet
        arguments: [56, 6.01e-4, 319, 9, -2.92e-4, 782, 14, 3, 3]
    rLL:
        sequence:
        - material: {sld: -3.73401535e-07}
          thickness: 1.4
          roughness: 0.0
        - material: {sld: 1.88401254e-06}
          thickness: 9.0
          roughness: 3.0
        represents:  refnx.reflect.LipidLeaflet
        arguments: [56, 6.01e-4, 319, 9, -2.92e-4, 782, 14, 3, 0]
        keywords: {reverse_monolayer: true}
globals:
    length_unit: angstrom`,
  "orsopy 5 - relative density": `stack: air | 10 ( Si 7 | Fe 7 ) | Si
materials:
  Fe:
    magnetic_moment: 2.5
  Si:
    relative_density: 0.9`,
  "orsopy 6 - export GenX": `stack: ambient | top | ML | buffer | substrate
origin: GenX model "X-ray_Reflectivity.hgx"
sub_stacks:
  top:
    repetitions: 1
    stack: topPt | TopFe
  ML:
    repetitions: 19
    stack: Pt | Fe
  buffer:
    repetitions: 1
    stack: bufPt | bufFe
layers:
  topPt:
    thickness: 11.0
    roughness: 3.0
    material:
      sld: {real: 4.864311704082625e-06, imag: -4.533346598101179e-07}
  TopFe:
    thickness: 11.0
    roughness: 2.0
    material:
      sld: {real: 2.1041406836134337e-06, imag: -2.7004929545359514e-07}
  Pt:
    thickness: 11.0
    roughness: 2.0
    material:
      sld: {real: 4.864311704082625e-06, imag: -4.533346598101179e-07}
  Fe:
    thickness: 11.0
    roughness: 2.0
    material:
      sld: {real: 2.1041406836134337e-06, imag: -2.7004929545359514e-07}
  bufPt:
    thickness: 45.0
    roughness: 2.0
    material:
      sld: {real: 4.864311704082625e-06, imag: -4.533346598101179e-07}
  bufFe:
    thickness: 2.0
    roughness: 2.0
    material:
      sld: {real: 2.1041406836134337e-06, imag: -2.7004929545359514e-07}
materials:
  ambient:
    sld: {real: 9.999999999999999e-27, imag: 9.999999999999999e-27}
  substrate:
    sld: {real: 5.456591989186995e-07, imag: -5.636808187886301e-09}
globals:
  roughness: {magnitude: 0.3, unit: nm}
  length_unit: angstrom
  mass_density_unit: g/cm^3
  number_density_unit: 1/nm^3
  sld_unit: 1/angstrom^2
  magnetic_moment_unit: muB`,
  "deep sub-stacks": `stack: substrate | film | water
sub_stacks:
  substrate:
    sequence:
    - material: Si
      roughness: 2
    - material: SiO2
      thickness: 5
      roughness: 3
  film:
    repetitions: 5
    stack: repeating_group
  repeating_group:
    stack: top_group| bottom_group
  top_group:
    stack: head_group 4 | tail_group 22
  bottom_group:
    stack: tail_group 22 | head_group 4
materials:
  head_group:
    sld: 0.2E-06
  tail_group:
    formula: CH2
    mass_density: 1.2`
};

const example_select = document.getElementById("example_scripts");
const yaml_text_entry = document.getElementById("sample_yaml");

for (let name in example_yaml_scripts) {
    example_select.add(new Option(name, name),undefined);
}

function example_selected() {
    name = example_select.value;
    if (name==="empty") {
        yaml_text_entry.value = "";
    } else {
        text = example_yaml_scripts[name];
        yaml_text_entry.value = text;
        example_select.value = "empty";
    }
};

example_select.addEventListener("change", example_selected);
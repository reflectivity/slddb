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
  "orsopy 2 - materials and globals": `stack: air | 10 ( Si 70 | Fe 70 ) | Si
materials:
  Fe:
    sld: 5.02e-6
  Si:
    formula: SiN0.01
    rel_density: 0.95
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
  "orsopy 5 - relative density": `stack: air | 10 ( Si 7 | Fe 7 ) | Si
materials:
  Fe:
    magnetic_moment: 2.5
  Si:
    relative_density: 0.9`,
  "orsopy 6 - SLD function": `stack: air | gtop 50 | 5 (rgradient 50 | gradient 50) | Si
sub_stacks:
  gradient:
    sub_stack_class: FunctionTwoElements
    material1: Ni
    material2: Ti
    function: x
  rgradient:
    like: gradient
    but:
      function: 1-x
  gtop:
    like: gradient
    but:
      roughness: 15.0
globals:
    slice_resolution: {magnitude: 10.0, unit: nm}`,
  "orsopy 7 - sine wave SLD": `stack: air | 5 (wave 10) | Si
sub_stacks:
  wave:
    sub_stack_class: FunctionTwoElements
    material1: Ni
    material2: Ti
    function: 0.5+0.5*sin(x*2*pi)`,
  "orsoyp 8 - modulated sine": `stack: air | wave 200 | Si
sub_stacks:
  wave:
    sub_stack_class: FunctionTwoElements
    material1: Ni
    material2: Ti
    function: (0.5+0.5*sin(x*20.0*2*pi))*exp(-(x-0.5)**2/0.25**2)`,
  "orsopy 9 - BioBlender": `comment: Material from SLD db Bio Blender mixture
stack: air | dna1 50 | RNA=AUGUUUAGUUAA 50 | protein1 100 | Si
layers:
    dna1:
        material: DNA=ATTAG
    protein1:
        material: Protein=MAHAGRTGYDNREIVMKYIHYKLSQRGYEWDAGDVGAAPPGAAPAPGIFSSQPGHTPHPAASRDPVARTSPLQTPAAPGAAAGPALSPVPPVVHLTLRQAGDDFSRRYRRDFAEMSSQLHLTPFTARGRFATVVEELFRDGVNWGRIVAFFEFGGVMCVESVNREMSPLVDNIALWMTEYLNRHLHTWIQDNGGWDAFVELYGPSMRPLFDFSWLSLKTLLSLALVGACITLGAYLGHK
        comment: Bcl-2`,
  "export from GenX": `stack: Amb | top | ML | buffer | Sub
origin: Model "X-ray_Reflectivity.hgx" exported directly from GenX
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
  Amb:
    material:
      sld: {real: 1.0e-25, imag: 1.0e-25, unit: 1/angstrom^2}
  topPt:
    thickness: 11.0
    roughness: 3.0
    material:
      formula: Pt
      number_density: 0.06640515431495381
  TopFe:
    thickness: 11.0
    roughness: 2.0
    material:
      formula: Fe
      number_density: 0.08495744391749196
  Pt:
    thickness: 18.0
    roughness: 2.0
    material:
      formula: Pt
      number_density: 0.06640515431495381
  Fe:
    thickness: 11.0
    roughness: 2.0
    material:
      formula: Fe
      number_density: 0.08495744391749196
  bufPt:
    thickness: 45.0
    roughness: 2.0
    material:
      formula: Pt
      number_density: 0.06640515431495381
  bufFe:
    thickness: 2.0
    roughness: 2.0
    material:
      formula: Fe
      number_density: 0.08495744391749196
  Sub:
    roughness: 4.0
    material:
      formula: MgO
      number_density: 0.026994924954108625
globals:
  length_unit: angstrom
  number_density_unit: 1/angstrom^3`,
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
    mass_density: 1.2`,
  "composits": `stack: Si | film | water
sub_stacks:
  film:
    repetitions: 2
    stack: head_group 4 | tail_group 22 | tail_group 22 | head_group 4
materials:
  head_group:
    sld: 0.2E-06
  tail_group:
    formula: CH2
    mass_density: 1.2
composits:
  water:
    composition:
      H2O: 0.9
      D2O: 0.1`
};

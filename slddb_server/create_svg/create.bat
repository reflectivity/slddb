latex formula_sld.tex
dvisvgm.exe --no-fonts -O -p 1 .\formula_sld.dvi
dvisvgm.exe --no-fonts -O -p 2 .\formula_sld.dvi
move *.svg ..\static\
del *.aux *.dvi *.log
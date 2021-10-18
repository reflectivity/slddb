"""
https://www.ncnr.nist.gov/resources/n-lengths/list.html
Neutron scattering lengths and cross sections
Isotope	conc	Coh b	Inc b	Coh xs	Inc xs	Scatt xs	Abs xs
"""

NEUTRON_SCATTERING_LENGTHS={'H': (-3.739+0j), (1, 1): (-3.7406+0j), (1, 2): (6.671+0j), (1, 3): (4.792+0j), 'He': None, (2, 3): (5.74-1.483j), (2, 4): (3.26+0j), 'Li': (-1.9+0j), (3, 6): (2-0.261j), (3, 7): (-2.22+0j), 'Be': (7.79+0j), 'B': (5.3-0.213j), (5, 10): (-0.1-1.066j), (5, 11): (6.65+0j), 'C': (6.646+0j), (6, 12): (6.6511+0j), (6, 13): (6.19+0j), 'N': (9.36+0j), (7, 14): (9.37+0j), (7, 15): (6.44+0j), 'O': (5.803+0j), (8, 16): (5.803+0j), (8, 17): (5.78+0j), (8, 18): (5.84+0j), 'F': (5.654+0j), 'Ne': (4.566+0j), (10, 20): (4.631+0j), (10, 21): (6.66+0j), (10, 22): (3.87+0j), 'Na': (3.63+0j), 'Mg': (5.375+0j), (12, 24): (5.66+0j), (12, 25): (3.62+0j), (12, 26): (4.89+0j), 'Al': (3.449+0j), 'Si': (4.1491+0j), (14, 28): (4.107+0j), (14, 29): (4.7+0j), (14, 30): (4.58+0j), 'P': (5.13+0j), 'S': (2.847+0j), (16, 32): (2.804+0j), (16, 33): (4.74+0j), (16, 34): (3.48+0j), (16, 36): None, 'Cl': (9.577+0j), (17, 35): (11.65+0j), (17, 37): (3.08+0j), 'Ar': (1.909+0j), (18, 36): (24.9+0j), (18, 38): (3.5+0j), (18, 40): (1.83+0j), 'K': (3.67+0j), (19, 39): (3.74+0j), (19, 40): None, (19, 41): (2.69+0j), 'Ca': (4.7+0j), (20, 40): (4.8+0j), (20, 42): (3.36+0j), (20, 43): (-1.56+0j), (20, 44): (1.42+0j), (20, 46): (3.6+0j), (20, 48): (0.39+0j), 'Sc': (12.29+0j), 'Ti': (-3.438+0j), (22, 46): (4.93+0j), (22, 47): (3.63+0j), (22, 48): (-6.08+0j), (22, 49): (1.04+0j), (22, 50): (6.18+0j), 'V': (-0.3824+0j), (23, 50): (7.6+0j), (23, 51): (-0.402+0j), 'Cr': (3.635+0j), (24, 50): (-4.5+0j), (24, 52): (4.92+0j), (24, 53): (-4.2+0j), (24, 54): (4.55+0j), 'Mn': (-3.73+0j), 'Fe': (9.45+0j), (26, 54): (4.2+0j), (26, 56): (9.94+0j), (26, 57): (2.3+0j), (26, 58): None, 'Co': (2.49+0j), 'Ni': (10.3+0j), (28, 58): (14.4+0j), (28, 60): (2.8+0j), (28, 61): (7.6+0j), (28, 62): (-8.7+0j), (28, 64): (-0.37+0j), 'Cu': (7.718+0j), (29, 63): (6.43+0j), (29, 65): (10.61+0j), 'Zn': (5.68+0j), (30, 64): (5.22+0j), (30, 66): (5.97+0j), (30, 67): (7.56+0j), (30, 68): (6.03+0j), (30, 70): None, 'Ga': (7.288+0j), (31, 69): (7.88+0j), (31, 71): (6.4+0j), 'Ge': (8.185+0j), (32, 70): (10+0j), (32, 72): (8.51+0j), (32, 73): (5.02+0j), (32, 74): (7.58+0j), (32, 76): (8.2+0j), 'As': (6.58+0j), 'Se': (7.97+0j), (34, 74): (0.8+0j), (34, 76): (12.2+0j), (34, 77): (8.25+0j), (34, 78): (8.24+0j), (34, 80): (7.48+0j), (34, 82): (6.34+0j), 'Br': (6.795+0j), (35, 79): (6.8+0j), (35, 81): (6.79+0j), 'Kr': (7.81+0j), (36, 78): None, (36, 80): None, (36, 82): None, (36, 83): None, (36, 84): None, (36, 86): (8.1+0j), 'Rb': (7.09+0j), (37, 85): (7.03+0j), (37, 87): (7.23+0j), 'Sr': (7.02+0j), (38, 84): None, (38, 86): (5.67+0j), (38, 87): (7.4+0j), (38, 88): (7.15+0j), 'Y': (7.75+0j), 'Zr': (7.16+0j), (40, 90): (6.4+0j), (40, 91): (8.7+0j), (40, 92): (7.4+0j), (40, 94): (8.2+0j), (40, 96): (5.5+0j), 'Nb': (7.054+0j), 'Mo': (6.715+0j), (42, 92): (6.91+0j), (42, 94): (6.8+0j), (42, 95): (6.91+0j), (42, 96): (6.2+0j), (42, 97): (7.24+0j), (42, 98): (6.58+0j), (42, 100): (6.73+0j), 'Tc': (6.8+0j), 'Ru': (7.03+0j), (44, 96): None, (44, 98): None, (44, 99): None, (44, 100): None, (44, 101): None, (44, 102): None, (44, 104): None, 'Rh': (5.88+0j), 'Pd': (5.91+0j), (46, 102): None, (46, 104): None, (46, 105): (5.5+0j), (46, 106): (6.4+0j), (46, 108): (4.1+0j), (46, 110): None, 'Ag': (5.922+0j), (47, 107): (7.555+0j), (47, 109): (4.165+0j), 'Cd': (4.87-0.7j), (48, 106): None, (48, 108): (5.4+0j), (48, 110): (5.9+0j), (48, 111): (6.5+0j), (48, 112): (6.4+0j), (48, 113): (-8-5.73j), (48, 114): (7.5+0j), (48, 116): (6.3+0j), 'In': (4.065-0.0539j), (49, 113): (5.39+0j), (49, 115): (4.01-0.0562j), 'Sn': (6.225+0j), (50, 112): None, (50, 114): (6.2+0j), (50, 115): None, (50, 116): (5.93+0j), (50, 117): (6.48+0j), (50, 118): (6.07+0j), (50, 119): (6.12+0j), (50, 120): (6.49+0j), (50, 122): (5.74+0j), (50, 124): (5.97+0j), 'Sb': (5.57+0j), (51, 121): (5.71+0j), (51, 123): (5.38+0j), 'Te': (5.8+0j), (52, 120): (5.3+0j), (52, 122): (3.8+0j), (52, 123): (-0.05-0.116j), (52, 124): (7.96+0j), (52, 125): (5.02+0j), (52, 126): (5.56+0j), (52, 128): (5.89+0j), (52, 130): (6.02+0j), 'I': (5.28+0j), 'Xe': (4.92+0j), (54, 124): None, (54, 126): None, (54, 128): None, (54, 129): None, (54, 130): None, (54, 131): None, (54, 132): None, (54, 134): None, (54, 136): None, 'Cs': (5.42+0j), 'Ba': (5.07+0j), (56, 130): (-3.6+0j), (56, 132): (7.8+0j), (56, 134): (5.7+0j), (56, 135): (4.67+0j), (56, 136): (4.91+0j), (56, 137): (6.83+0j), (56, 138): (4.84+0j), 'La': (8.24+0j), (57, 138): None, (57, 139): (8.24+0j), 'Ce': (4.84+0j), (58, 136): (5.8+0j), (58, 138): (6.7+0j), (58, 140): (4.84+0j), (58, 142): (4.75+0j), 'Pr': (4.58+0j), 'Nd': (7.69+0j), (60, 142): (7.7+0j), (60, 143): None, (60, 144): (2.8+0j), (60, 145): None, (60, 146): (8.7+0j), (60, 148): (5.7+0j), (60, 150): (5.3+0j), 'Pm': (12.6+0j), 'Sm': (0.8-1.65j), (62, 144): None, (62, 147): None, (62, 148): None, (62, 149): (-19.2-11.7j), (62, 150): None, (62, 152): (-5+0j), (62, 154): (9.3+0j), 'Eu': (7.22-1.26j), (63, 151): (6.13-2.53j), (63, 153): (8.22+0j), 'Gd': (6.5-13.82j), (64, 152): None, (64, 154): None, (64, 155): (6-17j), (64, 156): (6.3+0j), (64, 157): (-1.14-71.9j), (64, 158): None, (64, 160): (9.15+0j), 'Tb': (7.38+0j), 'Dy': (16.9-0.276j), (66, 156): (6.1+0j), (66, 158): None, (66, 160): (6.7+0j), (66, 161): (10.3+0j), (66, 162): (-1.4+0j), (66, 163): (5+0j), (66, 164): (49.4-0.79j), 'Ho': (8.01+0j), 'Er': (7.79+0j), (68, 162): (8.8+0j), (68, 164): (8.2+0j), (68, 166): (10.6+0j), (68, 167): (3+0j), (68, 168): (7.4+0j), (68, 170): (9.6+0j), 'Tm': (7.07+0j), 'Yb': (12.43+0j), (70, 168): (-4.07-0.62j), (70, 170): (6.77+0j), (70, 171): (9.66+0j), (70, 172): (9.43+0j), (70, 173): (9.56+0j), (70, 174): (19.3+0j), (70, 176): (8.72+0j), 'Lu': (7.21+0j), (71, 175): (7.24+0j), (71, 176): (6.1-0.57j), 'Hf': (7.7+0j), (72, 174): None, (72, 176): (6.61+0j), (72, 177): None, (72, 178): (5.9+0j), (72, 179): (7.46+0j), (72, 180): (13.2+0j), 'Ta': (6.91+0j), (73, 180): None, (73, 181): (6.91+0j), 'W': (4.86+0j), (74, 180): None, (74, 182): (6.97+0j), (74, 183): (6.53+0j), (74, 184): (7.48+0j), (74, 186): (-0.72+0j), 'Re': (9.2+0j), (75, 185): (9+0j), (75, 187): (9.3+0j), 'Os': (10.7+0j), (76, 184): None, (76, 186): None, (76, 187): None, (76, 188): (7.6+0j), (76, 189): (10.7+0j), (76, 190): (11+0j), (76, 192): (11.5+0j), 'Ir': (10.6+0j), (77, 191): None, (77, 193): None, 'Pt': (9.6+0j), (78, 190): (9+0j), (78, 192): (9.9+0j), (78, 194): (10.55+0j), (78, 195): (8.83+0j), (78, 196): (9.89+0j), (78, 198): (7.8+0j), 'Au': (7.63+0j), 'Hg': (12.692+0j), (80, 196): None, (80, 198): None, (80, 199): (16.9+0j), (80, 200): None, (80, 201): None, (80, 202): None, (80, 204): None, 'Tl': (8.776+0j), (81, 203): (6.99+0j), (81, 205): (9.52+0j), 'Pb': (9.405+0j), (82, 204): (9.9+0j), (82, 206): (9.22+0j), (82, 207): (9.28+0j), (82, 208): (9.5+0j), 'Bi': (8.532+0j), 'Po': None, 'At': None, 'Rn': None, 'Fr': None, 'Ra': None, 'Ac': None, 'Th': (10.31+0j), 'Pa': (9.1+0j), 'U': (8.417+0j), (92, 233): (10.1+0j), (92, 234): (12.4+0j), (92, 235): (10.47+0j), (92, 238): (8.402+0j), 'Np': (10.55+0j), 'Pu': None, (94, 238): (14.1+0j), (94, 239): (7.7+0j), (94, 240): (3.5+0j), (94, 242): (8.1+0j), 'Am': (8.3+0j), 'Cm': None, (96, 244): (9.5+0j), (96, 246): (9.3+0j), (96, 248): (7.7+0j)}

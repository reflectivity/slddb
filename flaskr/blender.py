from flask import redirect, url_for

from slddb import DB_FILE, SLDDB

CALC_DEFAULT_FIELDS = dict(densinput='volume',mu=0.0,magninput='muB')

AMINO_ABRV={
    "A": "Alanine",
    "R": "Arginine",
    "N": "Asparagine",
    "D": "Aspartate",
    "B": "Aspartate",
    "C": "Cysteine",
    "E": "Glutamate",
    "Q": "Glutamine",
    "Z": "Glutamate",
    "G": "Glycine",
    "H": "Histidine",
    "I": "Isoleucine",
    "L": "Leucine",
    "K": "Lysine",
    "M": "Methionine",
    "F": "Phenylalanine",
    "P": "Proline",
    "S": "Serine",
    "T": "Threonine",
    "W": "Tryptophan",
    "Y": "Tyrosine",
    "V": "Valine",
    }

RNA_ABRV={
    "A": "RNA-Adenine",
    "G": "RNA-Guanine",
    "C": "RNA-Cytosine",
    "U": "RNA-Uracil",
    }
DNA_ABRV={
    "A": "DNA-Adenine",
    "G": "DNA-Guanine",
    "C": "DNA-Cytosine",
    "T": "DNA-Thymine",
    }

class SequenceParseError(ValueError):
    pass

def collect_combination(ids, name_dict):
    db = SLDDB(DB_FILE)
    elements=[]
    loaded_ids={}
    for id in ids:
        if not id in loaded_ids:
            try:
                entry=db.search_material(name=name_dict[id])[0]
            except KeyError:
                raise SequenceParseError(f"Not a valid identifier {id}")
            except IndexError:
                raise SequenceParseError(f"Molecule {name_dict[id]} not found in database")
            m=db.select_material(entry)
            loaded_ids[id]=m
        elements.append(loaded_ids[id])
    result=elements[0]
    for element in elements[1:]:
        # combine molecule matierials
        result+=element
    return result

def clean_str(string):
    return string.replace('\n', '').replace('\r', '').replace('\t', '').replace(' ', '').strip()

def calculate_blend(mtype, name, idstr):
    result=collect_blend(mtype, name, idstr)

    return redirect(url_for('calculate_sld', formula=str(result.formula), density=result.fu_volume,
                            name=name or mtype, **CALC_DEFAULT_FIELDS))

def collect_blend(mtype, name, idstr):
    if mtype=='protein':
        return collect_protein(name, idstr)
    elif mtype=='dna':
        return collect_dna(name, idstr)
    elif mtype=='rna':
        return collect_rna(name, idstr)
    elif mtype=='db':
        return collect_blendIDs(name, idstr)

def collect_protein(name, acids):
    acids=clean_str(acids).upper()
    result=collect_combination(acids, AMINO_ABRV)
    return result

def collect_dna(name, bases):
    bases=clean_str(bases).upper()
    result=collect_combination(bases, DNA_ABRV)
    return result

def collect_rna(name, bases):
    bases=clean_str(bases).upper()
    result=collect_combination(bases, RNA_ABRV)
    return result

def collect_blendIDs(name, formula):
    db = SLDDB(DB_FILE)
    elements=[]
    loaded_ids={}
    items=[]
    while '(' in clean_str(formula):
        pre, formula=formula.split(')',1)
        number=float(pre.split('*',1)[0].strip('(').strip())
        ID=int(pre.split('*',1)[1].strip())
        items.append((number, ID))
    for number, ID in items:
        if not ID in loaded_ids:
            entry=db.search_material(ID=ID)[0]
            m=db.select_material(entry)
            loaded_ids[ID]=m
        elements.append(loaded_ids[ID])
    result=elements[0]
    for element in elements[1:]:
        # combine molecule matierials
        result+=element
    return result
